"""AI 智能辨证服务 — DeepSeek API + RAG"""
import json
import uuid
from datetime import datetime
from typing import AsyncGenerator

import httpx
from sqlalchemy.orm import Session

from app.config import settings
from app.models.herb import Herb, IncompatibilityRule
from app.models.knowledge import KnowledgeEntry
from app.services.incompatibility_checker import (
    check_prescription_herbs,
    check_dosage_limits,
    check_pregnancy_contraindications,
)


# ── System Prompt ──

TCM_SYSTEM_PROMPT = """你是一位经验丰富的中医师，精通中医理论、辨证论治和方剂学。请遵循以下原则：

1. **辨证论治**：基于四诊信息，按照八纲辨证、脏腑辨证、气血津液辨证等中医辨证体系进行系统分析。
2. **理法方药**：给出完整的理法方药链条——病机分析→治法→方剂→药味及剂量。
3. **方剂推荐**：优先推荐经典方剂（《伤寒论》《金匮要略》《温病条辨》等），说明加减变化。
4. **安全性**：必须注意十八反十九畏配伍禁忌、毒性药剂量限制、孕妇禁忌。
5. **术语规范**：使用 GB/T 16751 中医药学名词术语标准。
6. **循证参考**：引用经典原文支撑辨证依据。
7. **免责声明**：每次回复末尾加上"⚠️ 本分析由AI辅助生成，仅供参考，不替代专业中医师面诊。"
8. **中西医结合**：如患者提供西医诊断（病名、化验指标、影像报告），应：
   - 解读西医检查结果的临床意义
   - 从中医角度分析该西医疾病可能的中医病名和证型
   - 提出中西医结合治疗方案：中医辨证论治 + 西医规范治疗建议
   - 标注哪些症状适合中医治疗、哪些需西医优先处理
9. **图片解读**：如患者上传舌苔照片，应详细描述舌质（颜色、形态）、舌苔（颜色、厚薄、润燥）并据此辨证；
   如上传面色照片，应描述面色、神态并分析；如上传化验单/影像报告，应解读指标含义并给出中西医结合建议。
10. **重要提醒**：图片识别仅供参考，临床诊断需结合实际四诊合参。化验单解读仅作参考，不能替代医师判断。

请用中文回答，保持专业性和可读性。"""


class DiagnosisService:
    """AI智能辨证服务"""

    # ── DB 辅助 ──

    def _get_or_create_conversation(self, conversation_id: str | None, db: Session, patient_id: int | None = None):
        """按 uuid 查找或新建 Conversation 行，返回 (ConvORM, uuid_str)"""
        from app.models.conversation import Conversation
        if conversation_id:
            conv = db.query(Conversation).filter(Conversation.uuid == conversation_id).first()
            if conv:
                return conv, conversation_id
        # 新建
        new_uuid = conversation_id or str(uuid.uuid4())
        conv = Conversation(uuid=new_uuid, patient_id=patient_id)
        db.add(conv)
        db.commit()
        db.refresh(conv)
        return conv, new_uuid

    def _build_messages_from_db(self, conv, db: Session, limit: int = 40) -> list[dict]:
        """从 DB 读取历史消息，构建 DeepSeek API 格式"""
        from app.models.conversation import Message
        db_msgs = db.query(Message).filter(
            Message.conversation_id == conv.id
        ).order_by(Message.seq.desc()).limit(limit).all()
        db_msgs.reverse()

        result = []
        for m in db_msgs:
            if m.images:
                # 多模态消息：还原为 content_parts
                content_parts: list[dict] = [{"type": "text", "text": m.content}]
                for img in m.images:
                    if isinstance(img, dict) and "url" in img:
                        content_parts.append({"type": "image_url", "image_url": {"url": img["url"]}})
                    elif isinstance(img, str):
                        content_parts.append({"type": "image_url", "image_url": {"url": img}})
                result.append({"role": m.role, "content": content_parts})
            else:
                result.append({"role": m.role, "content": m.content})
        return result

    def _save_message(self, conv, seq: int, role: str, content: str, db: Session,
                      images: list | None = None, warnings: list | None = None):
        """写入一条 Message 并更新 Conversation 冗余字段"""
        from app.models.conversation import Message
        msg = Message(
            conversation_id=conv.id,
            seq=seq,
            role=role,
            content=content,
            images=images,
            warnings=warnings,
        )
        db.add(msg)
        conv.message_count = (conv.message_count or 0) + 1
        conv.last_message_at = datetime.now()
        db.commit()

    # ── 非流式 chat（保留兼容） ──

    async def chat(
        self,
        message: str,
        images: list[str] | None = None,
        conversation_id: str | None = None,
        patient_id: int | None = None,
        visit_id: int | None = None,
        db: Session | None = None,
    ) -> dict:
        """对话式智能问诊"""
        if not settings.deepseek_api_key:
            return {
                "conversation_id": conversation_id or "demo",
                "reply": "⚠️ DeepSeek API Key 未配置，请在系统设置中配置后使用。",
                "safety_warnings": [],
            }

        conv, conv_id = self._get_or_create_conversation(conversation_id, db, patient_id)

        # 首次消息自动设标题
        if not conv.title and message:
            conv.title = message[:50] + ("..." if len(message) > 50 else "")
            db.commit()

        # RAG
        context = ""
        if db:
            context = await self._retrieve_context(message, db)

        # 构建 API 消息
        api_messages = [{"role": "system", "content": TCM_SYSTEM_PROMPT}]
        if context:
            api_messages.append({"role": "system", "content": f"参考以下中医知识库内容：\n\n{context}"})
        api_messages.extend(self._build_messages_from_db(conv, db))
        user_msg = self._build_user_message(message, images)
        api_messages.append(user_msg)

        # 调用 API
        has_images = bool(images)
        reply = await self._call_deepseek(api_messages, use_vision=has_images)
        safety_warnings = self._check_safety_in_reply(reply, db)

        # 持久化消息
        next_seq = (conv.message_count or 0) + 1
        img_data = [{"url": u} for u in images] if images else None
        self._save_message(conv, next_seq, "user", message, db, images=img_data)
        self._save_message(conv, next_seq + 1, "assistant", reply, db, warnings=safety_warnings)

        return {
            "conversation_id": conv_id,
            "reply": reply,
            "suggested_syndrome": None,
            "suggested_formula": None,
            "safety_warnings": safety_warnings,
        }

    async def analyze(
        self,
        observation: str | None = None,
        auscultation: str | None = None,
        inquiry: str | None = None,
        palpation: str | None = None,
        tongue_body: str | None = None,
        tongue_coat: str | None = None,
        pulse: str | None = None,
        chief_complaint: str | None = None,
        patient_gender: str | None = None,
        is_pregnant: bool | None = None,
        tongue_image: str | None = None,
        face_image: str | None = None,
        lab_report_images: list[str] | None = None,
        db: Session | None = None,
    ) -> dict:
        """四诊信息 → 辨证分析（支持图片）"""
        if not settings.deepseek_api_key:
            return {
                "syndrome_analysis": "⚠️ DeepSeek API Key 未配置",
                "safety_warnings": ["请在系统设置中配置 DeepSeek API Key"],
            }

        # 构建四诊摘要
        four_diag = []
        if chief_complaint:
            four_diag.append(f"【主诉】{chief_complaint}")
        if observation:
            four_diag.append(f"【望诊】{observation}")
        if auscultation:
            four_diag.append(f"【闻诊】{auscultation}")
        if inquiry:
            four_diag.append(f"【问诊】{inquiry}")
        if palpation:
            four_diag.append(f"【切诊】{palpation}")
        if tongue_body or tongue_coat:
            four_diag.append(f"【舌象】舌质{tongue_body or '未记录'}，舌苔{tongue_coat or '未记录'}")
        if pulse:
            four_diag.append(f"【脉象】{pulse}")

        patient_info = ""
        if patient_gender:
            patient_info += f"患者性别：{patient_gender}。"
        if is_pregnant:
            patient_info += "⚠️患者为孕妇，需注意孕妇禁忌。"

        user_message = f"请根据以下四诊信息进行辨证分析：\n\n{patient_info}\n" + "\n".join(four_diag)
        user_message += "\n\n请给出：1.病机分析 2.中医病名 3.证型 4.治法 5.推荐方剂及加减 6.调护建议"

        # RAG
        context = ""
        search_query = chief_complaint or " ".join(filter(None, [observation, inquiry, pulse]))
        if db and search_query:
            context = await self._retrieve_context(search_query, db)

        messages = [{"role": "system", "content": TCM_SYSTEM_PROMPT}]
        if context:
            messages.append({
                "role": "system",
                "content": f"参考以下中医知识库内容：\n\n{context}"
            })

        # 构建多模态用户消息
        content_parts: list[dict] = [{"type": "text", "text": user_message}]
        if tongue_image:
            content_parts.append({"type": "text", "text": "【舌象照片】请仔细观察以下舌象照片："})
            content_parts.append({"type": "image_url", "image_url": {"url": tongue_image}})
        if face_image:
            content_parts.append({"type": "text", "text": "【面色照片】请观察以下面色照片："})
            content_parts.append({"type": "image_url", "image_url": {"url": face_image}})
        if lab_report_images:
            content_parts.append({"type": "text", "text": "【化验单/影像报告】请解读以下检查报告："})
            for img in lab_report_images:
                content_parts.append({"type": "image_url", "image_url": {"url": img}})

        # 如果有图片用多模态格式，否则用纯文本
        if len(content_parts) > 1:
            messages.append({"role": "user", "content": content_parts})
        else:
            messages.append({"role": "user", "content": user_message})

        has_images = bool(tongue_image or face_image or lab_report_images)
        reply = await self._call_deepseek(messages, use_vision=has_images)
        safety_warnings = self._check_safety_in_reply(reply, db)

        return {
            "syndrome_analysis": reply,
            "tcm_disease": None,
            "tcm_syndrome": None,
            "treatment_method": None,
            "recommended_formulas": [],
            "safety_warnings": safety_warnings,
            "references": [],
        }

    async def analyze_stream(
        self,
        observation: str | None = None,
        auscultation: str | None = None,
        inquiry: str | None = None,
        palpation: str | None = None,
        tongue_body: str | None = None,
        tongue_coat: str | None = None,
        pulse: str | None = None,
        chief_complaint: str | None = None,
        patient_gender: str | None = None,
        is_pregnant: bool | None = None,
        tongue_image: str | None = None,
        face_image: str | None = None,
        lab_report_images: list[str] | None = None,
        db: Session | None = None,
    ) -> AsyncGenerator[str, None]:
        """流式四诊辨证分析"""
        if not settings.deepseek_api_key:
            yield f"data: {json.dumps({'type': 'error', 'content': '⚠️ DeepSeek API Key 未配置'}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
            return

        four_diag = []
        if chief_complaint:
            four_diag.append(f"【主诉】{chief_complaint}")
        if observation:
            four_diag.append(f"【望诊】{observation}")
        if auscultation:
            four_diag.append(f"【闻诊】{auscultation}")
        if inquiry:
            four_diag.append(f"【问诊】{inquiry}")
        if palpation:
            four_diag.append(f"【切诊】{palpation}")
        if tongue_body or tongue_coat:
            four_diag.append(f"【舌象】舌质{tongue_body or '未记录'}，舌苔{tongue_coat or '未记录'}")
        if pulse:
            four_diag.append(f"【脉象】{pulse}")

        patient_info = ""
        if patient_gender:
            patient_info += f"患者性别：{patient_gender}。"
        if is_pregnant:
            patient_info += "⚠️患者为孕妇，需注意孕妇禁忌。"

        user_message = f"请根据以下四诊信息进行辨证分析：\n\n{patient_info}\n" + "\n".join(four_diag)
        user_message += "\n\n请给出：1.病机分析 2.中医病名 3.证型 4.治法 5.推荐方剂及加减 6.调护建议"

        context = ""
        search_query = chief_complaint or " ".join(filter(None, [observation, inquiry, pulse]))
        if db and search_query:
            context = await self._retrieve_context(search_query, db)

        messages = [{"role": "system", "content": TCM_SYSTEM_PROMPT}]
        if context:
            messages.append({"role": "system", "content": f"参考以下中医知识库内容：\n\n{context}"})

        content_parts: list[dict] = [{"type": "text", "text": user_message}]
        if tongue_image:
            content_parts.append({"type": "text", "text": "【舌象照片】请仔细观察以下舌象照片："})
            content_parts.append({"type": "image_url", "image_url": {"url": tongue_image}})
        if face_image:
            content_parts.append({"type": "text", "text": "【面色照片】请观察以下面色照片："})
            content_parts.append({"type": "image_url", "image_url": {"url": face_image}})
        if lab_report_images:
            content_parts.append({"type": "text", "text": "【化验单/影像报告】请解读以下检查报告："})
            for img in lab_report_images:
                content_parts.append({"type": "image_url", "image_url": {"url": img}})

        if len(content_parts) > 1:
            messages.append({"role": "user", "content": content_parts})
        else:
            messages.append({"role": "user", "content": user_message})

        has_images = bool(tongue_image or face_image or lab_report_images)
        full_reply = ""
        async for chunk in self._call_deepseek_stream(messages, use_vision=has_images):
            full_reply += chunk
            yield f"data: {json.dumps({'type': 'content', 'content': chunk}, ensure_ascii=False)}\n\n"

        safety_warnings = self._check_safety_in_reply(full_reply, db)
        yield f"data: {json.dumps({'type': 'warnings', 'warnings': safety_warnings}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    def _build_user_message(self, message: str, images: list[str] | None = None) -> dict:
        """构建用户消息，支持多模态（文字+图片）"""
        if not images:
            return {"role": "user", "content": message}

        content_parts: list[dict] = [{"type": "text", "text": message}]
        for img_url in images:
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": img_url}
            })
        return {"role": "user", "content": content_parts}

    async def _retrieve_context(self, query: str, db: Session, top_k: int = 5) -> str:
        """RAG 多路召回"""
        contexts = []

        # 1. 关键词检索 (SQL)
        try:
            entries = db.query(KnowledgeEntry).filter(
                (KnowledgeEntry.title.contains(query)) | (KnowledgeEntry.content.contains(query))
            ).limit(top_k).all()
            for e in entries:
                contexts.append(f"[{e.category}] {e.title}\n{e.content[:500]}")
        except Exception:
            pass

        # 2. 语义检索 (ChromaDB) — 如果可用
        try:
            from app.services.vector_store import vector_store
            vector_results = vector_store.search(query, top_k=top_k)
            for r in vector_results:
                contexts.append(f"[{r.get('category', '知识库')}] {r.get('title', '')}\n{r.get('content', '')[:500]}")
        except ImportError:
            pass  # ChromaDB 未安装
        except Exception:
            pass  # 向量检索失败，降级到关键词

        if not contexts:
            return ""

        return "\n\n---\n\n".join(contexts[:8])

    async def _call_deepseek(self, messages: list[dict], use_vision: bool = False) -> str:
        """调用 DeepSeek API — 有图片时使用 Vision 端点，无 Vision 配置时降级为纯文字"""
        # 判断是否有 Vision 能力
        vision_model = settings.deepseek_vision_model
        vision_base_url = settings.deepseek_vision_base_url or settings.deepseek_base_url
        vision_api_key = settings.deepseek_vision_api_key or settings.deepseek_api_key

        if use_vision and not vision_model:
            # 无 Vision 配置：剥离图片，只保留文字描述
            messages = self._strip_images(messages)

        # 选择模型、端点和 Key
        if use_vision and vision_model:
            model = vision_model
            base_url = vision_base_url
            api_key = vision_api_key
        else:
            model = settings.deepseek_model
            base_url = settings.deepseek_base_url
            api_key = settings.deepseek_api_key

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=30.0)) as client:
                response = await client.post(
                    f"{base_url}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 4000,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"]
        except httpx.TimeoutException:
            return "⚠️ 请求超时，请稍后重试。"
        except httpx.HTTPStatusError as e:
            detail = ""
            try:
                detail = e.response.json().get("error", {}).get("message", "") or e.response.text[:200]
            except Exception:
                detail = e.response.text[:200]
            return f"⚠️ API 调用失败 (HTTP {e.response.status_code}): {detail}"
        except Exception as e:
            return f"⚠️ 请求出错: {str(e)}"

    async def _call_deepseek_stream(self, messages: list[dict], use_vision: bool = False) -> AsyncGenerator[str, None]:
        """流式调用 DeepSeek API，逐块 yield 文本内容"""
        vision_model = settings.deepseek_vision_model
        vision_base_url = settings.deepseek_vision_base_url or settings.deepseek_base_url
        vision_api_key = settings.deepseek_vision_api_key or settings.deepseek_api_key

        if use_vision and not vision_model:
            messages = self._strip_images(messages)

        if use_vision and vision_model:
            model = vision_model
            base_url = vision_base_url
            api_key = vision_api_key
        else:
            model = settings.deepseek_model
            base_url = settings.deepseek_base_url
            api_key = settings.deepseek_api_key

        try:
            async with httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=30.0)) as client:
                async with client.stream(
                    "POST",
                    f"{base_url}/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 4000,
                        "stream": True,
                    },
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        except httpx.TimeoutException:
            yield "⚠️ 请求超时，请稍后重试。"
        except httpx.HTTPStatusError as e:
            detail = ""
            try:
                detail = e.response.json().get("error", {}).get("message", "") or str(e.response.status_code)
            except Exception:
                detail = str(e.response.status_code)
            yield f"⚠️ API 调用失败 (HTTP {e.response.status_code}): {detail}"
        except Exception as e:
            yield f"⚠️ 请求出错: {str(e)}"

    async def chat_stream(
        self,
        message: str,
        images: list[str] | None = None,
        conversation_id: str | None = None,
        patient_id: int | None = None,
        visit_id: int | None = None,
        db: Session | None = None,
    ) -> AsyncGenerator[str, None]:
        """流式对话式智能问诊"""
        if not settings.deepseek_api_key:
            yield f"data: {json.dumps({'type': 'error', 'content': '⚠️ DeepSeek API Key 未配置'}, ensure_ascii=False)}\n\n"
            return

        conv, conv_id = self._get_or_create_conversation(conversation_id, db, patient_id)

        # 首次消息自动设标题
        if not conv.title and message:
            conv.title = message[:50] + ("..." if len(message) > 50 else "")
            db.commit()

        # 发送 conversation_id
        yield f"data: {json.dumps({'type': 'meta', 'conversation_id': conv_id}, ensure_ascii=False)}\n\n"

        # RAG
        context = ""
        if db:
            context = await self._retrieve_context(message, db)

        # 构建 API 消息
        api_messages = [{"role": "system", "content": TCM_SYSTEM_PROMPT}]
        if context:
            api_messages.append({"role": "system", "content": f"参考以下中医知识库内容：\n\n{context}"})
        api_messages.extend(self._build_messages_from_db(conv, db))
        user_msg = self._build_user_message(message, images)
        api_messages.append(user_msg)

        # 流式调用
        has_images = bool(images)
        full_reply = ""
        async for chunk in self._call_deepseek_stream(api_messages, use_vision=has_images):
            full_reply += chunk
            yield f"data: {json.dumps({'type': 'content', 'content': chunk}, ensure_ascii=False)}\n\n"

        # 安全性校验
        safety_warnings = self._check_safety_in_reply(full_reply, db)

        # 持久化消息
        next_seq = (conv.message_count or 0) + 1
        img_data = [{"url": u} for u in images] if images else None
        self._save_message(conv, next_seq, "user", message, db, images=img_data)
        self._save_message(conv, next_seq + 1, "assistant", full_reply, db, warnings=safety_warnings)

        # 发送安全警告 + 结束标记
        yield f"data: {json.dumps({'type': 'warnings', 'warnings': safety_warnings}, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"

    def _strip_images(self, messages: list[dict]) -> list[dict]:
        """将多模态消息中的图片剥离，保留文字描述（降级到纯文字模型时使用）"""
        result = []
        for msg in messages:
            content = msg.get("content")
            if isinstance(content, list):
                # 多模态消息：提取文字部分，图片标记为 [已上传图片]
                text_parts = []
                has_image = False
                for part in content:
                    if part.get("type") == "text":
                        text_parts.append(part["text"])
                    elif part.get("type") == "image_url":
                        has_image = True
                text = "\n".join(text_parts)
                if has_image:
                    text += "\n\n[用户已上传图片，但当前模型不支持图片识别，请仅根据文字描述进行分析。]"
                result.append({"role": msg["role"], "content": text})
            else:
                result.append(msg)
        return result

    def _check_safety_in_reply(self, reply: str, db: Session | None) -> list[str]:
        """对AI回复进行安全性硬约束校验"""
        warnings = []

        if not db:
            return warnings

        # 检查回复中是否包含配伍禁忌组合
        # 从回复中提取可能出现的药名
        all_herbs = db.query(Herb).filter(Herb.is_active == True).all()
        mentioned_herbs = []
        for herb in all_herbs:
            if herb.name in reply:
                mentioned_herbs.append(herb)
            # 检查异名
            if herb.aliases:
                for alias in herb.aliases:
                    if alias in reply:
                        mentioned_herbs.append(herb)
                        break

        # 配伍禁忌检查
        if len(mentioned_herbs) >= 2:
            herb_ids = [h.id for h in mentioned_herbs]
            conflicts = check_prescription_herbs(herb_ids, db)
            for w in conflicts:
                warnings.append(f"⚠️ 配伍禁忌: {w['herb_a']} + {w['herb_b']} ({w['rule_type']})")

        # 孕妇禁忌检查
        for herb in mentioned_herbs:
            if herb.pregnancy_contraindicated:
                warnings.append(f"⚠️ 孕妇禁忌: {herb.name}")

        # 毒性药提醒
        for herb in mentioned_herbs:
            if herb.toxicity in ("有毒", "有大毒"):
                warnings.append(f"⚠️ 毒性药: {herb.name}({herb.toxicity})，注意剂量控制")

        return warnings


# 全局服务实例
diagnosis_service = DiagnosisService()
