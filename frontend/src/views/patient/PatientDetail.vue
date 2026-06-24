<template>
  <div class="patient-detail" v-loading="loading">
    <el-page-header @back="$router.push('/patients')" :content="patient?.name || '加载中...'">
      <template #extra>
        <el-button type="primary" @click="$router.push(`/patients/${patientId}/visit`)">
          <el-icon><EditPen /></el-icon> 新增就诊
        </el-button>
        <el-button @click="$router.push(`/constitution/${patientId}`)">
          <el-icon><TrendCharts /></el-icon> 体质辨识
        </el-button>
      </template>
    </el-page-header>

    <el-row :gutter="20" style="margin-top: 20px;">
      <!-- 基本信息 -->
      <el-col :span="8">
        <el-card shadow="hover">
          <template #header><span>📋 基本信息</span></template>
          <el-descriptions :column="1" border size="small" v-if="patient">
            <el-descriptions-item label="姓名">{{ patient.name }}</el-descriptions-item>
            <el-descriptions-item label="性别">{{ patient.gender }}</el-descriptions-item>
            <el-descriptions-item label="出生日期">{{ patient.birth_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="电话">{{ patient.phone || '-' }}</el-descriptions-item>
            <el-descriptions-item label="身份证号">{{ patient.id_card || '-' }}</el-descriptions-item>
            <el-descriptions-item label="地址">{{ patient.address || '-' }}</el-descriptions-item>
            <el-descriptions-item label="过敏史">
              <el-tag v-if="patient.allergy_history" type="danger" size="small">{{ patient.allergy_history }}</el-tag>
              <span v-else>无</span>
            </el-descriptions-item>
            <el-descriptions-item label="既往史">{{ patient.medical_history || '无' }}</el-descriptions-item>
            <el-descriptions-item label="体质">
              <el-tag v-if="patient.constitution_type" type="warning">{{ patient.constitution_type }}</el-tag>
              <span v-else class="text-muted">未评估</span>
            </el-descriptions-item>
            <el-descriptions-item label="备注">{{ patient.notes || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <!-- 就诊历史 -->
      <el-col :span="16">
        <el-card shadow="hover">
          <template #header><span>🏥 就诊记录</span></template>
          <el-timeline v-if="visits.length > 0">
            <el-timeline-item
              v-for="visit in visits"
              :key="visit.id"
              :timestamp="visit.visit_date"
              placement="top"
            >
              <el-card shadow="never" class="visit-card">
                <div class="visit-header">
                  <strong>主诉：</strong>{{ visit.chief_complaint }}
                </div>
                <div v-if="visit.tcm_disease || visit.tcm_syndrome" class="visit-diagnosis">
                  <el-tag type="primary" size="small">{{ visit.tcm_disease }}</el-tag>
                  <el-tag type="warning" size="small">{{ visit.tcm_syndrome }}</el-tag>
                  <el-tag type="info" size="small">{{ visit.treatment_method }}</el-tag>
                </div>
                <div v-if="visit.tongue_body || visit.pulse" class="visit-sizhen">
                  <span v-if="visit.tongue_body">舌质: {{ visit.tongue_body }}</span>
                  <span v-if="visit.tongue_coat">舌苔: {{ visit.tongue_coat }}</span>
                  <span v-if="visit.pulse">脉象: {{ visit.pulse }}</span>
                </div>
              </el-card>
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无就诊记录" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { EditPen, TrendCharts } from '@element-plus/icons-vue'
import api from '@/utils/api'

const route = useRoute()
const patientId = Number(route.params.id)
const patient = ref<any>(null)
const visits = ref<any[]>([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const [p, v] = await Promise.all([
      api.get(`/patients/${patientId}`),
      api.get(`/patients/${patientId}/visits`),
    ])
    patient.value = p
    visits.value = v as any
  } catch {}
  loading.value = false
})
</script>

<style scoped>
.text-muted { color: #c0c4cc; }
.visit-card { margin-bottom: 4px; }
.visit-header { font-size: 14px; }
.visit-diagnosis { margin-top: 8px; display: flex; gap: 6px; }
.visit-sizhen { margin-top: 8px; font-size: 13px; color: #666; display: flex; gap: 12px; }
</style>
