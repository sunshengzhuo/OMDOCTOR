<template>
  <div class="constitution-scale">
    <el-page-header @back="$router.back()" content="中医体质辨识量表" />

    <el-card shadow="hover" style="margin-top: 20px;">
      <template #header>
        <span>🧬 王琦九种体质量表</span>
        <el-tag type="info" size="small" style="margin-left: 8px;">共45题</el-tag>
      </template>

      <el-alert
        title="请根据您近一年的体验和感觉回答以下问题"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      />

      <div v-for="(group, type) in questions" :key="type" class="question-group">
        <h3 class="group-title">{{ type }}</h3>
        <div v-for="(q, idx) in group" :key="q.id" class="question-item">
          <div class="question-text">{{ idx + 1 }}. {{ q.text }}</div>
          <el-radio-group v-model="answers[q.id]" class="question-options">
            <el-radio v-for="opt in 5" :key="opt" :value="opt" size="small">
              {{ optionLabels[opt - 1] }}
            </el-radio>
          </el-radio-group>
        </div>
      </div>

      <div style="text-align: center; margin-top: 24px;">
        <el-button type="primary" size="large" @click="submitScale" :loading="submitting" :disabled="answeredCount < 10">
          提交评估 (已答 {{ answeredCount }}/45)
        </el-button>
      </div>
    </el-card>

    <!-- 结果对话框 -->
    <el-dialog v-model="showResult" title="体质辨识报告" width="600px" destroy-on-close>
      <div v-if="result" class="result-content">
        <div class="result-primary">
          <span class="result-label">主要体质：</span>
          <el-tag type="warning" size="large">{{ result.primary_type }}</el-tag>
        </div>
        <p class="result-desc">{{ constitutionInfo[result.primary_type]?.description }}</p>

        <div v-if="result.secondary_types.length > 0" class="result-secondary">
          <span class="result-label">倾向体质：</span>
          <el-tag v-for="st in result.secondary_types" :key="st" size="small" style="margin-right:6px;">{{ st }}</el-tag>
        </div>

        <el-divider>各体质得分</el-divider>
        <div class="score-bars">
          <div v-for="(score, type) in result.scores" :key="type" class="score-bar-row">
            <span class="score-type">{{ type }}</span>
            <el-progress :percentage="score" :color="getScoreColor(score)" :stroke-width="16" style="flex:1" />
            <span class="score-value">{{ score }}分</span>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const route = useRoute()
const patientId = route.params.id ? Number(route.params.id) : null
const submitting = ref(false)
const showResult = ref(false)
const result = ref<any>(null)

const optionLabels = ['没有(从不)', '很少(偶尔)', '有时', '经常', '总是(一直)']

// 简化版体质量表（每种体质5道代表题）
const questions: Record<string, { id: number; text: string }[]> = {
  '平和质': [
    { id: 1, text: '您精力充沛吗？' },
    { id: 2, text: '您容易疲乏吗？' },
    { id: 3, text: '您说话声音低弱无力吗？' },
    { id: 4, text: '您感到闷闷不乐吗？' },
    { id: 5, text: '您比一般人耐受不了寒冷吗？' },
  ],
  '气虚质': [
    { id: 6, text: '您容易感到疲乏吗？' },
    { id: 7, text: '您容易气短(呼吸短促、接不上气)吗？' },
    { id: 8, text: '您容易心慌吗？' },
    { id: 9, text: '您容易头晕或站起时晕眩吗？' },
    { id: 10, text: '您比别人容易患感冒吗？' },
  ],
  '阳虚质': [
    { id: 11, text: '您手脚发凉吗？' },
    { id: 12, text: '您胃脘部、背部或腰膝部怕冷吗？' },
    { id: 13, text: '您比一般人耐受不了寒冷吗？' },
    { id: 14, text: '您吃(喝)凉的东西会感到不舒服或者怕吃凉的吗？' },
    { id: 15, text: '您受凉或吃(喝)凉的东西后容易拉肚子吗？' },
  ],
  '阴虚质': [
    { id: 16, text: '您感到手脚心发热吗？' },
    { id: 17, text: '您感觉身体、脸上发热吗？' },
    { id: 18, text: '您皮肤或口唇干吗？' },
    { id: 19, text: '您感到口干咽燥、总想喝水吗？' },
    { id: 20, text: '您感到眼睛干涩吗？' },
  ],
  '痰湿质': [
    { id: 21, text: '您感到胸闷或腹部胀满吗？' },
    { id: 22, text: '您感到身体沉重不轻松或不爽快吗？' },
    { id: 23, text: '您腹部肥满松软吗？' },
    { id: 24, text: '您额头部位油脂分泌多吗？' },
    { id: 25, text: '您上眼睑比别人肿(上眼睑有轻微隆起)吗？' },
  ],
  '湿热质': [
    { id: 26, text: '您面部或鼻部有油腻感或者油亮发光吗？' },
    { id: 27, text: '您易生痤疮或疮疖吗？' },
    { id: 28, text: '您感到口苦或嘴里有异味吗？' },
    { id: 29, text: '您大便粘滞不爽、有解不尽的感觉吗？' },
    { id: 30, text: '您小便时尿道有发热感、尿色浓(深)吗？' },
  ],
  '血瘀质': [
    { id: 31, text: '您皮肤常在不知不觉中出现青紫瘀斑吗？' },
    { id: 32, text: '您两颧部有细微红丝吗？' },
    { id: 33, text: '您身体上有哪里疼痛吗？' },
    { id: 34, text: '您面色晦暗或容易出现褐斑吗？' },
    { id: 35, text: '您容易有黑眼圈吗？' },
  ],
  '气郁质': [
    { id: 36, text: '您感到闷闷不乐、情绪低沉吗？' },
    { id: 37, text: '您容易精神紧张、焦虑不安吗？' },
    { id: 38, text: '您多愁善感、感情脆弱吗？' },
    { id: 39, text: '您容易感到害怕或受到惊吓吗？' },
    { id: 40, text: '您胁肋部或乳房胀痛吗？' },
  ],
  '特禀质': [
    { id: 41, text: '您没有感冒也会打喷嚏吗？' },
    { id: 42, text: '您没有感冒也会鼻塞、流鼻涕吗？' },
    { id: 43, text: '您有因季节变化、温度变化或异味等原因引起的咳喘吗？' },
    { id: 44, text: '您容易过敏(对药物、食物、气味、花粉或季节交替)吗？' },
    { id: 45, text: '您皮肤容易起荨麻疹(风团、风疹块、风疙瘩)吗？' },
  ],
}

const constitutionInfo: Record<string, { description: string }> = {
  '平和质': { description: '阴阳气血调和，体态适中，面色润泽。精力充沛，睡眠良好，性格随和开朗。' },
  '气虚质': { description: '元气不足，疲乏气短，易感冒。宜健脾益气，适度运动。' },
  '阳虚质': { description: '阳气不足，手足不温，畏寒怕冷。宜温阳散寒，忌食生冷。' },
  '阴虚质': { description: '阴液亏少，口燥咽干，手足心热。宜滋阴降火，忌辛辣燥热。' },
  '痰湿质': { description: '痰湿凝聚，体形肥胖，腹部肥满。宜健脾化痰，少食肥甘。' },
  '湿热质': { description: '湿热内蕴，面垢油光，口苦口干。宜清热利湿，忌辛辣油腻。' },
  '血瘀质': { description: '血行不畅，肤色晦暗，舌质紫暗。宜活血化瘀，适度运动。' },
  '气郁质': { description: '气机郁滞，神情抑郁，忧虑脆弱。宜疏肝解郁，调畅情志。' },
  '特禀质': { description: '先天失常，过敏体质为主。宜益气固表，避免过敏原。' },
}

const answers = ref<Record<string, number>>({})

const answeredCount = computed(() => Object.keys(answers.value).length)

function getScoreColor(score: number): string {
  if (score >= 60) return '#F5222D'
  if (score >= 30) return '#FAAD14'
  return '#52C41A'
}

async function submitScale() {
  if (answeredCount.value < 10) {
    ElMessage.warning('请至少回答10道题目')
    return
  }
  submitting.value = true
  try {
    const endpoint = patientId ? `/patients/${patientId}/constitution` : '/diagnosis/analyze'
    const res = await api.post(endpoint, { answers: answers.value }) as any
    result.value = res
    showResult.value = true
  } catch {}
  submitting.value = false
}
</script>

<style scoped lang="scss">
.question-group {
  margin-bottom: 24px;

  .group-title {
    font-size: 16px;
    font-weight: 600;
    color: #8B4513;
    margin-bottom: 12px;
    padding-left: 8px;
    border-left: 3px solid #8B4513;
  }
}

.question-item {
  margin-bottom: 16px;
  padding: 8px 12px;
  border-radius: 8px;
  background: #faf8f6;

  .question-text {
    font-size: 14px;
    margin-bottom: 8px;
    color: #333;
  }

  .question-options {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }
}

.result-content {
  .result-primary {
    font-size: 18px;
    margin-bottom: 12px;
  }
  .result-desc {
    color: #666;
    font-size: 14px;
    margin-bottom: 16px;
  }
  .result-secondary {
    margin-bottom: 16px;
  }
  .result-label {
    font-weight: 600;
    margin-right: 8px;
  }
  .score-bars {
    .score-bar-row {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 8px;
      .score-type { width: 60px; text-align: right; font-size: 13px; }
      .score-value { width: 50px; font-size: 13px; color: #666; }
    }
  }
}
</style>
