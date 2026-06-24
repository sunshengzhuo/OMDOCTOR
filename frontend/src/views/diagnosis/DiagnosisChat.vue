<template>
  <div class="diagnosis-chat">
    <div class="chat-layout">
      <!-- 侧边栏 -->
      <div class="chat-sidebar">
        <div class="sidebar-header">
          <el-button type="primary" size="small" @click="newConversation" style="width:100%">+ 新建对话</el-button>
        </div>
        <div class="sidebar-list">
          <div v-for="conv in conversations" :key="conv.uuid"
            :class="['conv-item', { active: conv.uuid === activeConvId }]"
            @click="switchConversation(conv.uuid)">
            <div class="conv-title">{{ conv.title || '新对话' }}</div>
            <div class="conv-meta">
              <span>{{ conv.message_count }}条消息</span>
              <span>{{ formatTime(conv.last_message_at || conv.created_at) }}</span>
            </div>
            <el-icon class="conv-delete" @click.stop="deleteConversation(conv.uuid)"><Close /></el-icon>
          </div>
          <div v-if="!conversations.length" class="sidebar-empty">暂无对话</div>
        </div>
      </div>

      <!-- 聊天主区域 -->
      <div class="chat-main">
        <div class="chat-header">
          <span>🤖 智能问诊助手</span>
          <div style="display:flex;align-items:center;gap:8px;">
            <el-tag :type="apiConfigured ? 'success' : 'danger'" size="small">
              {{ apiConfigured ? 'DeepSeek 已连接' : 'API Key 未配置' }}
            </el-tag>
            <el-tag v-if="visionAvailable" type="success" size="small">📷 图片识别</el-tag>
            <el-tag v-if="vectorAvailable" type="success" size="small">🧠 RAG 已启用</el-tag>
            <el-button size="small" @click="showAnalyze = true">四诊分析</el-button>
          </div>
        </div>

        <div class="chat-container">
          <div class="chat-messages" ref="messagesRef">
            <div v-for="(msg, idx) in messages" :key="idx" :class="['chat-message', msg.role]">
              <div class="message-avatar">{{ msg.role === 'user' ? '👤' : '🌿' }}</div>
              <div class="message-content">
                <div class="message-text" v-html="renderMarkdown(msg.content)"></div>
                <div v-if="msg.images?.length" class="message-images">
                  <el-image v-for="(img, i) in msg.images" :key="i" :src="img" fit="cover"
                    class="msg-img" :preview-src-list="msg.images" :initial-index="i" />
                </div>
                <div v-if="msg.warnings?.length" class="message-warnings">
                  <el-alert v-for="w in msg.warnings" :key="w" :title="w" type="warning" :closable="false"
                    show-icon style="margin-top:8px;" />
                </div>
              </div>
            </div>
            <div v-if="loading && (!messages.length || !messages[messages.length-1]?.content)" class="chat-message assistant">
              <div class="message-avatar">🌿</div>
              <div class="message-content">
                <div class="typing-indicator">
                  <span class="dot"></span><span class="dot"></span><span class="dot"></span>
                  思考中...
                </div>
              </div>
            </div>
          </div>

          <div class="chat-input-area">
            <div v-if="pendingImages.length" class="pending-images">
              <div v-for="(img, idx) in pendingImages" :key="idx" class="pending-img-wrap">
                <el-image :src="img" fit="cover" class="pending-img" />
                <el-icon class="remove-img" @click="pendingImages.splice(idx, 1)"><Close /></el-icon>
              </div>
            </div>
            <div class="chat-input">
              <el-button class="img-btn" @click="triggerImageUpload" :disabled="loading" title="上传图片">📷</el-button>
              <input ref="fileInputRef" type="file" accept="image/*" style="display:none" @change="onImageSelect" />
              <el-input v-model="inputText" placeholder="描述症状或上传舌苔/化验单图片..."
                @keydown.enter="sendMessage" :disabled="loading" size="large" style="flex:1" />
              <el-button @click="sendMessage" :loading="loading" type="primary" size="large"
                style="margin-left:8px">发送</el-button>
            </div>
          </div>
        </div>

        <el-alert v-if="!apiConfigured" title="请先在系统设置中配置 DeepSeek API Key"
          type="warning" :closable="false" style="margin-top:8px;" />
      </div>
    </div>

    <!-- 四诊分析对话框 -->
    <el-dialog v-model="showAnalyze" title="🔬 四诊辨证分析" width="700px" destroy-on-close>
      <el-form :model="analyzeForm" label-width="80px">
        <el-form-item label="主诉">
          <el-input v-model="analyzeForm.chief_complaint" placeholder="如：胃脘胀痛一周" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="望诊">
              <el-input v-model="analyzeForm.observation" type="textarea" :rows="2" placeholder="面色、神态、形体" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="闻诊">
              <el-input v-model="analyzeForm.auscultation" type="textarea" :rows="2" placeholder="语声、呼吸、气味" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="问诊">
          <el-input v-model="analyzeForm.inquiry" type="textarea" :rows="3" placeholder="寒热、汗出、饮食、睡眠、二便等" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="舌质">
              <el-select v-model="analyzeForm.tongue_body" placeholder="选择" clearable>
                <el-option v-for="t in tongueOptions" :key="t" :label="t" :value="t" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="舌苔">
              <el-select v-model="analyzeForm.tongue_coat" placeholder="选择" clearable>
                <el-option v-for="t in coatOptions" :key="t" :label="t" :value="t" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="脉象">
              <el-select v-model="analyzeForm.pulse" placeholder="选择" clearable>
                <el-option v-for="p in pulseOptions" :key="p" :label="p" :value="p" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="舌象照片">
              <div class="analyze-upload">
                <el-button size="small" @click="triggerAnalyzeImage('tongue')">📷 上传</el-button>
                <el-image v-if="analyzeImages.tongue" :src="analyzeImages.tongue" fit="cover" class="analyze-thumb"
                  :preview-src-list="[analyzeImages.tongue]" />
                <el-icon v-if="analyzeImages.tongue" class="remove-analyze-img" @click="analyzeImages.tongue = ''"><Close /></el-icon>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="面色照片">
              <div class="analyze-upload">
                <el-button size="small" @click="triggerAnalyzeImage('face')">📷 上传</el-button>
                <el-image v-if="analyzeImages.face" :src="analyzeImages.face" fit="cover" class="analyze-thumb"
                  :preview-src-list="[analyzeImages.face]" />
                <el-icon v-if="analyzeImages.face" class="remove-analyze-img" @click="analyzeImages.face = ''"><Close /></el-icon>
              </div>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="化验单">
              <div class="analyze-upload">
                <el-button size="small" @click="triggerAnalyzeImage('lab')">📷 上传</el-button>
                <span v-if="analyzeImages.lab.length" class="lab-count">{{ analyzeImages.lab.length }}张</span>
              </div>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="性别">
              <el-select v-model="analyzeForm.patient_gender" clearable>
                <el-option label="男" value="男" />
                <el-option label="女" value="女" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="孕妇">
              <el-switch v-model="analyzeForm.is_pregnant" />
            </el-form-item>
          </el-col>
        </el-row>
      </el-form>
      <template #footer>
        <el-button @click="showAnalyze = false">取消</el-button>
        <el-button type="primary" @click="submitAnalyze" :loading="analyzing">开始辨证分析</el-button>
      </template>
    </el-dialog>
    <input ref="analyzeFileInputRef" type="file" accept="image/*" style="display:none" @change="onAnalyzeImageSelect" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Close } from '@element-plus/icons-vue'
import api from '@/utils/api'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  warnings?: string[]
  images?: string[]
}

interface ConvSummary {
  uuid: string
  title: string | null
  message_count: number
  last_message_at: string | null
  created_at: string
}

const GREETING: ChatMessage = {
  role: 'assistant',
  content: '您好！我是中医智能问诊助手 🌿\n\n我可以帮您：\n1. **对话问诊** — 直接描述症状，我来辨证分析\n2. **图片识别** — 上传舌苔照片、化验单、影像报告，我来解读\n3. **四诊分析** — 点击右上角「四诊分析」，结构化输入四诊信息\n4. **中西医结合** — 提供西医病名或化验结果，我给出中西医结合治疗建议\n\n请描述您的症状或上传图片，我将为您提供辨证分析和方剂建议。',
}

const messages = ref<ChatMessage[]>([GREETING])
const inputText = ref('')
const loading = ref(false)
const analyzing = ref(false)
const apiConfigured = ref(false)
const visionAvailable = ref(false)
const vectorAvailable = ref(false)
const messagesRef = ref<HTMLElement>()
const activeConvId = ref<string | null>(null)
const showAnalyze = ref(false)
const conversations = ref<ConvSummary[]>([])

const pendingImages = ref<string[]>([])
const fileInputRef = ref<HTMLInputElement>()
const analyzeFileInputRef = ref<HTMLInputElement>()
const analyzeImageTarget = ref<'tongue' | 'face' | 'lab'>('tongue')
const analyzeImages = ref<{ tongue: string; face: string; lab: string[] }>({ tongue: '', face: '', lab: [] })

const analyzeForm = ref({
  chief_complaint: '', observation: '', auscultation: '', inquiry: '', palpation: '',
  tongue_body: '', tongue_coat: '', pulse: '', patient_gender: '', is_pregnant: false,
})

const tongueOptions = ['舌淡', '舌红', '舌暗红', '舌绛', '舌淡红', '舌紫暗', '舌有瘀斑', '舌胖大有齿痕', '舌瘦薄']
const coatOptions = ['薄白苔', '薄黄苔', '白腻苔', '黄腻苔', '黄燥苔', '灰黑苔', '无苔', '花剥苔', '白滑苔']
const pulseOptions = ['浮脉', '沉脉', '迟脉', '数脉', '虚脉', '实脉', '滑脉', '涩脉', '弦脉', '紧脉', '缓脉', '细脉', '洪脉', '濡脉', '弱脉', '弦滑', '弦数', '沉细', '沉弦']

onMounted(async () => {
  try {
    const res = await api.get('/config') as any
    apiConfigured.value = res.deepseek_configured
    visionAvailable.value = res.vision_configured || false
    try {
      const status = await api.get('/diagnosis/status') as any
      vectorAvailable.value = status.vector_store_available || false
    } catch {}
  } catch {}
  await loadConversations()
})

async function loadConversations() {
  try {
    const res = await api.get('/diagnosis/conversations') as any
    conversations.value = res.items || []
  } catch { /* ignore */ }
}

async function switchConversation(uuid: string) {
  if (uuid === activeConvId.value) return
  activeConvId.value = uuid
  messages.value = []
  try {
    const res = await api.get(`/diagnosis/conversations/${uuid}/messages`) as any
    for (const m of res.items || []) {
      const imgs = m.images?.map((i: any) => typeof i === 'string' ? i : i.url).filter(Boolean)
      messages.value.push({
        role: m.role,
        content: m.content,
        images: imgs?.length ? imgs : undefined,
        warnings: m.warnings?.length ? m.warnings : undefined,
      })
    }
  } catch { /* ignore */ }
  if (!messages.value.length) messages.value = [GREETING]
  await nextTick()
  scrollBottom()
}

async function newConversation() {
  try {
    const res = await api.post('/diagnosis/conversations', {}) as any
    activeConvId.value = res.uuid
    messages.value = [GREETING]
    await loadConversations()
  } catch {
    ElMessage.error('创建对话失败')
  }
}

async function deleteConversation(uuid: string) {
  try {
    await ElMessageBox.confirm('确定删除此对话？', '提示', { type: 'warning' })
  } catch { return }
  try {
    await api.delete(`/diagnosis/conversations/${uuid}`)
    if (activeConvId.value === uuid) {
      activeConvId.value = null
      messages.value = [GREETING]
    }
    await loadConversations()
  } catch {
    ElMessage.error('删除失败')
  }
}

function formatTime(dt: string | null) {
  if (!dt) return ''
  const d = new Date(dt)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${d.getMonth() + 1}/${d.getDate()}`
}

function triggerImageUpload() { fileInputRef.value?.click() }

async function onImageSelect(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) { ElMessage.warning('图片不能超过5MB'); return }
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post('/diagnosis/upload-image', formData) as any
    pendingImages.value.push(res.data_url)
  } catch { ElMessage.error('图片上传失败') }
  input.value = ''
}

function triggerAnalyzeImage(target: 'tongue' | 'face' | 'lab') {
  analyzeImageTarget.value = target
  analyzeFileInputRef.value?.click()
}

async function onAnalyzeImageSelect(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (file.size > 5 * 1024 * 1024) { ElMessage.warning('图片不能超过5MB'); return }
  try {
    const formData = new FormData()
    formData.append('file', file)
    const res = await api.post('/diagnosis/upload-image', formData) as any
    const target = analyzeImageTarget.value
    if (target === 'lab') analyzeImages.value.lab.push(res.data_url)
    else analyzeImages.value[target] = res.data_url
  } catch { ElMessage.error('图片上传失败') }
  input.value = ''
}

async function sendMessage() {
  if ((!inputText.value.trim() && !pendingImages.value.length) || loading.value) return
  const text = inputText.value.trim() || '请分析我上传的图片'
  const images = [...pendingImages.value]
  inputText.value = ''
  pendingImages.value = []

  messages.value.push({ role: 'user', content: text, images: images.length ? images : undefined })
  messages.value.push({ role: 'assistant', content: '', warnings: [] })
  const msgIdx = messages.value.length - 1
  loading.value = true
  await nextTick()
  scrollBottom()

  try {
    const payload: any = { message: text, conversation_id: activeConvId.value }
    if (images.length) payload.images = images

    const isElectronProd = typeof window !== 'undefined' && window.location.protocol === 'file:'
    const baseUrl = isElectronProd ? 'http://127.0.0.1:8765/api/v1' : '/api/v1'
    const response = await fetch(`${baseUrl}/diagnosis/chat/stream`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })

    if (!response.ok || !response.body) {
      messages.value[msgIdx].content = `抱歉，请求出错 (HTTP ${response.status})`
      loading.value = false; return
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const dataStr = line.slice(6)
        if (dataStr.trim() === '[DONE]') continue
        try {
          const data = JSON.parse(dataStr)
          if (data.type === 'meta') activeConvId.value = data.conversation_id
          else if (data.type === 'content') {
            messages.value[msgIdx].content += data.content
            await nextTick(); scrollBottom()
          } else if (data.type === 'warnings') messages.value[msgIdx].warnings = data.warnings || []
          else if (data.type === 'error') messages.value[msgIdx].content = data.content
        } catch { /* skip */ }
      }
    }
  } catch {
    messages.value[msgIdx].content = '抱歉，请求出错，请稍后重试。'
  }
  loading.value = false
  await loadConversations()
  await nextTick(); scrollBottom()
}

async function submitAnalyze() {
  analyzing.value = true; showAnalyze.value = false
  const form = analyzeForm.value; const imgs = analyzeImages.value

  messages.value.push({
    role: 'user',
    content: `【四诊分析请求】\n主诉: ${form.chief_complaint || '未记录'}\n望诊: ${form.observation || '未记录'}\n问诊: ${form.inquiry || '未记录'}\n舌象: ${form.tongue_body || '未记录'} ${form.tongue_coat || ''}\n脉象: ${form.pulse || '未记录'}${imgs.tongue ? '\n[附舌象照片]' : ''}${imgs.face ? '\n[附面色照片]' : ''}${imgs.lab.length ? '\n[附化验单]' : ''}`,
    images: [imgs.tongue, imgs.face, ...imgs.lab].filter(Boolean) as string[] | undefined as any,
  })
  messages.value.push({ role: 'assistant', content: '', warnings: [] })
  const msgIdx = messages.value.length - 1
  loading.value = true; await nextTick(); scrollBottom()

  try {
    const payload: any = { ...form }
    if (imgs.tongue) payload.tongue_image = imgs.tongue
    if (imgs.face) payload.face_image = imgs.face
    if (imgs.lab.length) payload.lab_report_images = imgs.lab

    const isElectronProd = typeof window !== 'undefined' && window.location.protocol === 'file:'
    const baseUrl = isElectronProd ? 'http://127.0.0.1:8765/api/v1' : '/api/v1'
    const response = await fetch(`${baseUrl}/diagnosis/analyze/stream`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload),
    })

    if (!response.ok || !response.body) {
      messages.value[msgIdx].content = `抱歉，分析出错 (HTTP ${response.status})`
      loading.value = false; analyzing.value = false; return
    }

    const reader = response.body.getReader(); const decoder = new TextDecoder(); let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n'); buffer = lines.pop() || ''
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue
        const dataStr = line.slice(6)
        if (dataStr.trim() === '[DONE]') continue
        try {
          const data = JSON.parse(dataStr)
          if (data.type === 'content') {
            messages.value[msgIdx].content += data.content
            await nextTick(); scrollBottom()
          } else if (data.type === 'warnings') messages.value[msgIdx].warnings = data.warnings || []
          else if (data.type === 'error') messages.value[msgIdx].content = data.content
        } catch { /* skip */ }
      }
    }
  } catch {
    messages.value[msgIdx].content = '抱歉，分析出错，请稍后重试。'
  }
  loading.value = false; analyzing.value = false
  await nextTick(); scrollBottom()
}

function scrollBottom() {
  if (messagesRef.value) messagesRef.value.scrollTop = messagesRef.value.scrollHeight
}

function renderMarkdown(text: string) {
  return text
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    .replace(/\n/g, '<br>')
}
</script>

<style scoped lang="scss">
.chat-layout {
  display: flex;
  height: calc(100vh - 160px);
  min-height: 500px;
  gap: 0;
  border: 1px solid #e8e0d8;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.chat-sidebar {
  width: 260px;
  border-right: 1px solid #e8e0d8;
  display: flex;
  flex-direction: column;
  background: #faf7f4;
  flex-shrink: 0;

  .sidebar-header {
    padding: 12px;
    border-bottom: 1px solid #e8e0d8;
  }

  .sidebar-list {
    flex: 1;
    overflow-y: auto;
    padding: 4px 0;
  }

  .sidebar-empty {
    text-align: center;
    color: #999;
    padding: 40px 0;
    font-size: 13px;
  }

  .conv-item {
    padding: 10px 12px;
    cursor: pointer;
    border-bottom: 1px solid #f0ebe5;
    position: relative;
    transition: background 0.2s;

    &:hover { background: #f5f0eb; }
    &.active { background: #ede4d8; border-left: 3px solid #8B4513; }

    .conv-title {
      font-size: 13px;
      font-weight: 500;
      color: #2C1810;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      padding-right: 20px;
    }

    .conv-meta {
      font-size: 11px;
      color: #999;
      margin-top: 4px;
      display: flex;
      justify-content: space-between;
    }

    .conv-delete {
      position: absolute;
      top: 8px;
      right: 8px;
      font-size: 14px;
      color: #ccc;
      cursor: pointer;
      &:hover { color: #f56c6c; }
    }
  }
}

.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.chat-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e8e0d8;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
  font-size: 15px;
  color: #2C1810;
  background: #faf7f4;
}

.chat-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.chat-message {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;

  &.user {
    flex-direction: row-reverse;
    .message-content { background: #8B4513; color: #fff; }
  }

  &.assistant {
    .message-content {
      background: #fff;
      border: 1px solid #e8e0d8;
      code { background: #f5f0eb; padding: 1px 4px; border-radius: 3px; font-size: 13px; }
    }
  }

  .message-avatar {
    width: 36px; height: 36px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
  }

  .message-content {
    padding: 12px 16px;
    border-radius: 12px;
    max-width: 75%;
    font-size: 14px;
    line-height: 1.7;

    .message-text { word-break: break-word; }
    .message-warnings { margin-top: 4px; }

    .message-images {
      margin-top: 8px;
      display: flex; gap: 6px; flex-wrap: wrap;
      .msg-img { width: 80px; height: 80px; border-radius: 6px; cursor: pointer; }
    }
  }
}

.typing-indicator {
  color: #999; font-style: italic;
  display: flex; align-items: center; gap: 4px;
  .dot {
    width: 6px; height: 6px; border-radius: 50%; background: #D4A574;
    animation: blink 1.4s infinite both;
    &:nth-child(2) { animation-delay: 0.2s; }
    &:nth-child(3) { animation-delay: 0.4s; }
  }
}

@keyframes blink {
  0%, 80%, 100% { opacity: 0.2; }
  40% { opacity: 1; }
}

.chat-input-area {
  padding: 8px 16px 12px;
  border-top: 1px solid #e8e0d8;
  background: #faf7f4;
}

.pending-images {
  display: flex; gap: 8px; margin-bottom: 8px;
  .pending-img-wrap {
    position: relative;
    .pending-img { width: 64px; height: 64px; border-radius: 6px; border: 1px solid #e8e0d8; }
    .remove-img {
      position: absolute; top: -6px; right: -6px;
      background: #f56c6c; color: #fff; border-radius: 50%;
      width: 18px; height: 18px; cursor: pointer; font-size: 12px;
    }
  }
}

.chat-input {
  display: flex; align-items: center; gap: 0;
  .img-btn {
    font-size: 18px; padding: 8px 12px;
    border: 1px solid #dcdfe6; border-right: none; border-radius: 4px 0 0 4px;
    background: #f5f7fa; cursor: pointer;
  }
}

.analyze-upload {
  display: flex; align-items: center; gap: 8px; position: relative;
  .analyze-thumb { width: 40px; height: 40px; border-radius: 4px; border: 1px solid #e8e0d8; }
  .remove-analyze-img {
    position: absolute; top: -4px; left: 52px;
    background: #f56c6c; color: #fff; border-radius: 50%;
    width: 16px; height: 16px; cursor: pointer; font-size: 10px;
  }
  .lab-count { font-size: 12px; color: #8B4513; background: #f5f0eb; padding: 2px 6px; border-radius: 4px; }
}
</style>
