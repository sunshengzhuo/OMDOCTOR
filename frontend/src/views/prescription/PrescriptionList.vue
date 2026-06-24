<template>
  <div class="prescription-list">
    <el-card shadow="hover">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span>📋 处方列表</span>
          <el-button type="primary" size="small" @click="$router.push('/prescriptions/new')">
            <el-icon><Plus /></el-icon> 开具处方
          </el-button>
        </div>
      </template>

      <el-form :inline="true" @submit.prevent="loadPrescriptions">
        <el-form-item>
          <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="loadPrescriptions" style="width:120px">
            <el-option label="已开" value="已开" />
            <el-option label="已审核" value="已审核" />
            <el-option label="已发药" value="已发药" />
            <el-option label="已取消" value="已取消" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadPrescriptions">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="prescriptions" stripe style="width:100%" empty-text="暂无处方记录">
        <el-table-column prop="id" label="编号" width="70" />
        <el-table-column prop="formula_name" label="方名" width="160">
          <template #default="{ row }">{{ row.formula_name || '自拟方' }}</template>
        </el-table-column>
        <el-table-column label="药味" min-width="250">
          <template #default="{ row }">
            <div class="herb-tags">
              <el-tag v-for="item in (row.items || [])" :key="item.id" size="small" style="margin:2px;">
                {{ item.herb_name }} {{ item.dose }}g
                <span v-if="item.special_method" style="color:#8B4513;">({{ item.special_method }})</span>
              </el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="doses" label="剂数" width="70" />
        <el-table-column prop="preparation_method" label="煎法" width="80" />
        <el-table-column prop="status" label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="开具时间" width="160">
          <template #default="{ row }">{{ formatTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="viewDetail(row)">详情</el-button>
            <el-button v-if="row.status === '已开'" link type="success" size="small" @click="reviewPrescription(row)">审核</el-button>
            <el-button v-if="row.status === '已审核'" link type="warning" size="small" @click="dispensePrescription(row)">发药</el-button>
            <el-button link type="info" size="small" @click="printPrescription(row)">打印</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 处方详情对话框 -->
    <el-dialog v-model="detailVisible" title="处方详情" width="600px" destroy-on-close>
      <template v-if="currentPrescription">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="方名">{{ currentPrescription.formula_name || '自拟方' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="statusType(currentPrescription.status)">{{ currentPrescription.status }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="煎法">{{ currentPrescription.preparation_method }}</el-descriptions-item>
          <el-descriptions-item label="剂数">{{ currentPrescription.doses }}剂</el-descriptions-item>
          <el-descriptions-item label="服法" :span="2">{{ currentPrescription.administration || '-' }}</el-descriptions-item>
          <el-descriptions-item label="医嘱" :span="2">{{ currentPrescription.doctor_notes || '-' }}</el-descriptions-item>
        </el-descriptions>

        <el-table :data="currentPrescription.items || []" stripe style="margin-top:12px;" size="small">
          <el-table-column prop="herb_name" label="药味" width="100" />
          <el-table-column prop="dose" label="剂量(g)" width="90" />
          <el-table-column prop="special_method" label="煎法" width="80">
            <template #default="{ row }">{{ row.special_method || '-' }}</template>
          </el-table-column>
          <el-table-column prop="is_king_herb" label="君药" width="60">
            <template #default="{ row }">
              <el-icon v-if="row.is_king_herb" color="#D4A574"><Star /></el-icon>
            </template>
          </el-table-column>
          <el-table-column prop="note" label="备注" show-overflow-tooltip>
            <template #default="{ row }">{{ row.note || '-' }}</template>
          </el-table-column>
        </el-table>
      </template>
    </el-dialog>

    <!-- 打印预览 -->
    <el-dialog v-model="printVisible" title="处方打印" width="600px" destroy-on-close>
      <div ref="printRef" class="prescription-print">
        <div class="print-header">
          <h2>中医处方笺</h2>
        </div>
        <template v-if="currentPrescription">
          <div class="print-info">
            <span>处方编号: #{{ currentPrescription.id }}</span>
            <span>日期: {{ formatTime(currentPrescription.created_at) }}</span>
          </div>
          <div class="print-formula-name">{{ currentPrescription.formula_name || '自拟方' }}</div>
          <table class="print-herb-table">
            <thead>
              <tr><th>药味</th><th>剂量(g)</th><th>煎法</th><th>备注</th></tr>
            </thead>
            <tbody>
              <tr v-for="item in (currentPrescription.items || [])" :key="item.id">
                <td>{{ item.herb_name }}{{ item.is_king_herb ? ' ★' : '' }}</td>
                <td>{{ item.dose }}</td>
                <td>{{ item.special_method || '' }}</td>
                <td>{{ item.note || '' }}</td>
              </tr>
            </tbody>
          </table>
          <div class="print-footer">
            <p>剂数: {{ currentPrescription.doses }}剂</p>
            <p>煎法: {{ currentPrescription.preparation_method }}</p>
            <p v-if="currentPrescription.administration">服法: {{ currentPrescription.administration }}</p>
            <p v-if="currentPrescription.doctor_notes">医嘱: {{ currentPrescription.doctor_notes }}</p>
          </div>
        </template>
      </div>
      <template #footer>
        <el-button @click="printVisible = false">关闭</el-button>
        <el-button type="primary" @click="doPrint">打印</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Star } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'

const router = useRouter()
const prescriptions = ref<any[]>([])
const statusFilter = ref('')
const detailVisible = ref(false)
const printVisible = ref(false)
const currentPrescription = ref<any>(null)
const printRef = ref<HTMLElement>()

function statusType(status: string) {
  if (status === '已开') return 'info'
  if (status === '已审核') return 'warning'
  if (status === '已发药') return 'success'
  if (status === '已取消') return 'danger'
  return 'info'
}

function formatTime(t: string) {
  if (!t) return '-'
  return new Date(t).toLocaleString('zh-CN')
}

async function loadPrescriptions() {
  try {
    const params: any = { limit: 100 }
    if (statusFilter.value) params.status = statusFilter.value
    prescriptions.value = (await api.get('/prescriptions', { params })) as any
  } catch {}
}

function viewDetail(row: any) {
  currentPrescription.value = row
  detailVisible.value = true
}

async function reviewPrescription(row: any) {
  try {
    await ElMessageBox.confirm(`确认审核处方 #${row.id}「${row.formula_name || '自拟方'}」？`, '审核确认', {
      confirmButtonText: '确认审核',
      cancelButtonText: '取消',
      type: 'warning',
    })
    await api.put(`/prescriptions/${row.id}/review`)
    ElMessage.success('处方已审核')
    loadPrescriptions()
  } catch {}
}

async function dispensePrescription(row: any) {
  try {
    await ElMessageBox.confirm(
      `确认发药？将自动扣减库存。处方 #${row.id}「${row.formula_name || '自拟方'}」`,
      '发药确认',
      { confirmButtonText: '确认发药', cancelButtonText: '取消', type: 'warning' }
    )
    await api.put(`/prescriptions/${row.id}/dispense`)
    ElMessage.success('发药成功，库存已扣减')
    loadPrescriptions()
  } catch {}
}

function printPrescription(row: any) {
  currentPrescription.value = row
  printVisible.value = true
}

function doPrint() {
  const content = printRef.value
  if (!content) return
  const win = window.open('', '_blank')
  if (!win) { ElMessage.error('无法打开打印窗口'); return }
  win.document.write(`
    <html><head><title>中医处方笺</title>
    <style>
      body { font-family: 'SimSun', serif; margin: 40px; }
      h2 { text-align: center; margin-bottom: 20px; }
      .print-info { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 14px; }
      .print-formula-name { font-size: 18px; font-weight: bold; margin: 10px 0; text-align: center; }
      table { width: 100%; border-collapse: collapse; margin: 10px 0; }
      th, td { border: 1px solid #333; padding: 6px 10px; text-align: center; font-size: 14px; }
      th { background: #f5f0eb; }
      .print-footer { margin-top: 16px; font-size: 14px; line-height: 1.8; }
    </style></head><body>${content.innerHTML}</body></html>
  `)
  win.document.close()
  win.print()
}

onMounted(loadPrescriptions)
</script>

<style scoped lang="scss">
.prescription-list {
  .herb-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 2px;
  }
}

.prescription-print {
  font-family: 'SimSun', serif;
  padding: 20px;

  .print-header {
    text-align: center;
    border-bottom: 2px solid #8B4513;
    padding-bottom: 12px;
    h2 { margin: 0; color: #8B4513; }
  }

  .print-info {
    display: flex;
    justify-content: space-between;
    margin: 12px 0;
    font-size: 13px;
    color: #666;
  }

  .print-formula-name {
    font-size: 18px;
    font-weight: bold;
    text-align: center;
    margin: 12px 0;
  }

  .print-herb-table {
    width: 100%;
    border-collapse: collapse;
    margin: 10px 0;

    th, td {
      border: 1px solid #ccc;
      padding: 6px 10px;
      text-align: center;
      font-size: 13px;
    }

    th { background: #f5f0eb; }
  }

  .print-footer {
    margin-top: 16px;
    font-size: 13px;
    line-height: 1.8;
  }
}
</style>
