<template>
  <div class="settings-page">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span>🏥 诊所信息</span></template>
          <el-form label-width="100px">
            <el-form-item label="诊所名称"><el-input v-model="clinicName" placeholder="请输入诊所名称" /></el-form-item>
            <el-form-item label="医师姓名"><el-input v-model="doctorName" placeholder="请输入医师姓名" /></el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span>🤖 AI 配置</span></template>
          <el-form label-width="100px">
            <el-form-item label="API Key">
              <el-input v-model="deepseekKey" type="password" show-password :placeholder="hasKey ? '已配置，输入新值可替换' : '输入 API Key'" />
            </el-form-item>
            <el-form-item label="对话模型">
              <el-select v-model="deepseekModel" style="width:100%">
                <el-option label="deepseek-chat" value="deepseek-chat" />
                <el-option label="deepseek-reasoner" value="deepseek-reasoner" />
                <el-option label="deepseek-v4-pro" value="deepseek-v4-pro" />
                <el-option label="deepseek-v4-flash" value="deepseek-v4-flash" />
              </el-select>
            </el-form-item>
            <el-form-item label="Base URL">
              <el-input v-model="deepseekBaseUrl" placeholder="https://api.deepseek.com" />
            </el-form-item>

            <el-divider content-position="left">📷 图片识别（Vision）</el-divider>
            <el-form-item label="Vision 模型">
              <el-input v-model="visionModel" placeholder="如 Pro/deepseek-ai/DeepSeek-VL2" style="width:100%" />
              <div style="font-size:12px;color:#999;margin-top:4px;">
                DeepSeek 官方 API 不支持图片识别，需配置第三方 Vision 端点（如硅基流动）
              </div>
            </el-form-item>
            <el-form-item label="Vision URL">
              <el-input v-model="visionBaseUrl" placeholder="如 https://api.siliconflow.cn/v1" />
            </el-form-item>
            <el-form-item label="Vision Key">
              <el-input v-model="visionKey" type="password" show-password :placeholder="hasVisionKey ? '已配置，输入新值可替换' : '留空则复用上方 API Key'" />
            </el-form-item>
            <el-form-item>
              <el-tag v-if="visionConfigured" type="success" size="small">✅ 图片识别已启用</el-tag>
              <el-tag v-else type="warning" size="small">⚠️ 未配置 Vision 模型，上传图片将仅作文字分析</el-tag>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="saveConfig">保存配置</el-button>
              <el-button @click="testConnection" :loading="testing">测试连接</el-button>
            </el-form-item>
            <el-form-item>
              <el-tag :type="connectionStatus.type" size="small">{{ connectionStatus.text }}</el-tag>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span>💾 数据管理</span></template>
          <el-form label-width="100px">
            <el-form-item label="数据备份">
              <el-button type="primary" @click="exportData" :loading="exporting">
                <el-icon><Download /></el-icon> 导出备份
              </el-button>
              <span style="font-size:12px;color:#999;margin-left:8px;">导出为 SQLite 数据库文件</span>
            </el-form-item>
            <el-form-item label="数据恢复">
              <el-upload
                :auto-upload="false"
                :show-file-list="false"
                accept=".db,.json"
                @change="onImportFile"
              >
                <el-button type="warning">
                  <el-icon><Upload /></el-icon> 导入恢复
                </el-button>
              </el-upload>
              <span style="font-size:12px;color:#999;margin-left:8px;">选择备份文件恢复数据</span>
            </el-form-item>
            <el-form-item label="重置数据">
              <el-popconfirm title="确定要清空所有数据？此操作不可撤销！" @confirm="resetData">
                <template #reference>
                  <el-button type="danger">清空数据库</el-button>
                </template>
              </el-popconfirm>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover">
          <template #header><span>ℹ️ 系统信息</span></template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="应用名称">中医诊所管理平台</el-descriptions-item>
            <el-descriptions-item label="版本">v0.2.0</el-descriptions-item>
            <el-descriptions-item label="技术栈">Electron + FastAPI + Vue3</el-descriptions-item>
            <el-descriptions-item label="AI 引擎">
              <el-tag :type="hasKey ? 'success' : 'info'" size="small">
                {{ hasKey ? 'DeepSeek 已配置' : '未配置' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="向量库">
              <el-tag :type="vectorAvailable ? 'success' : 'info'" size="small">
                {{ vectorAvailable ? 'ChromaDB 已启用' : 'ChromaDB 未安装' }}
              </el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Upload } from '@element-plus/icons-vue'
import api from '@/utils/api'

const clinicName = ref('')
const doctorName = ref('')
const deepseekKey = ref('')
const hasKey = ref(false)
const deepseekModel = ref('deepseek-chat')
const deepseekBaseUrl = ref('https://api.deepseek.com')
const visionModel = ref('')
const visionBaseUrl = ref('')
const visionKey = ref('')
const hasVisionKey = ref(false)
const visionConfigured = ref(false)
const testing = ref(false)
const exporting = ref(false)
const vectorAvailable = ref(false)

const connectionStatus = ref({ type: 'info' as 'success' | 'danger' | 'info', text: '未测试' })

onMounted(async () => {
  try {
    const res = await api.get('/config') as any
    deepseekModel.value = res.deepseek_model || 'deepseek-chat'
    deepseekBaseUrl.value = res.deepseek_base_url || 'https://api.deepseek.com'
    if (res.deepseek_configured) {
      hasKey.value = true
      connectionStatus.value = { type: 'success', text: '已配置' }
    }
    visionModel.value = res.deepseek_vision_model || ''
    visionBaseUrl.value = res.deepseek_vision_base_url || ''
    hasVisionKey.value = res.vision_key_configured || false
    visionConfigured.value = res.vision_configured || false
  } catch {}

  try {
    const res = await api.get('/diagnosis/status') as any
    vectorAvailable.value = res.vector_store_available || false
  } catch {}
})

async function saveConfig() {
  try {
    const params: any = {
      deepseek_model: deepseekModel.value,
      deepseek_base_url: deepseekBaseUrl.value,
    }
    // 只有用户实际输入了新key才发送
    if (deepseekKey.value) {
      params.deepseek_api_key = deepseekKey.value
    }
    if (visionModel.value) {
      params.deepseek_vision_model = visionModel.value
    }
    if (visionBaseUrl.value) {
      params.deepseek_vision_base_url = visionBaseUrl.value
    }
    if (visionKey.value) {
      params.deepseek_vision_api_key = visionKey.value
    }
    await api.put('/config', null, { params })
    visionConfigured.value = !!visionModel.value
    hasVisionKey.value = !!visionKey.value || hasVisionKey.value
    ElMessage.success('配置已保存')
    connectionStatus.value = { type: 'success', text: '配置已保存' }
  } catch {}
}

async function testConnection() {
  if (!deepseekKey.value && !hasKey.value) {
    ElMessage.warning('请先输入 API Key')
    return
  }

  testing.value = true
  connectionStatus.value = { type: 'info', text: '测试中...' }

  try {
    // 先保存配置
    await api.put('/config', null, {
      params: {
        deepseek_api_key: deepseekKey.value,
        deepseek_model: deepseekModel.value,
        deepseek_base_url: deepseekBaseUrl.value,
      },
    })

    // 发送简单消息测试
    const res = await api.post('/diagnosis/chat', { message: '你好' }) as any
    if (res.reply && !res.reply.includes('未配置') && !res.reply.includes('失败')) {
      connectionStatus.value = { type: 'success', text: '✅ 连接成功' }
      ElMessage.success('DeepSeek API 连接成功')
    } else {
      connectionStatus.value = { type: 'danger', text: '❌ 连接失败' }
    }
  } catch {
    connectionStatus.value = { type: 'danger', text: '❌ 连接失败' }
    ElMessage.error('连接测试失败，请检查 API Key')
  } finally {
    testing.value = false
  }
}

async function exportData() {
  exporting.value = true
  try {
    const res = await api.get('/backup/export', { responseType: 'blob' }) as any
    const url = window.URL.createObjectURL(new Blob([res]))
    const link = document.createElement('a')
    link.href = url
    link.download = `tcm_backup_${new Date().toISOString().slice(0, 10)}.db`
    link.click()
    window.URL.revokeObjectURL(url)
    ElMessage.success('数据备份已下载')
  } catch {
    // 降级方案：提示手动备份
    ElMessage.info('请手动备份数据库文件: backend/tcm_doctor.db')
  } finally {
    exporting.value = false
  }
}

async function onImportFile(file: any) {
  try {
    await ElMessageBox.confirm('导入数据将覆盖当前数据，确定继续？', '数据恢复确认', {
      confirmButtonText: '确定导入',
      cancelButtonText: '取消',
      type: 'warning',
    })
    const formData = new FormData()
    formData.append('file', file.raw)
    await api.post('/backup/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    ElMessage.success('数据恢复成功，请重启应用')
  } catch {
    // 用户取消或接口未实现
  }
}

async function resetData() {
  try {
    await api.post('/backup/reset')
    ElMessage.success('数据已清空')
  } catch {}
}
</script>
