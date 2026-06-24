<template>
  <div class="patient-list">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>👥 患者管理</span>
          <el-button type="primary" @click="showAddDialog = true">
            <el-icon><Plus /></el-icon> 新增患者
          </el-button>
        </div>
      </template>

      <!-- 搜索栏 -->
      <el-form :inline="true" @submit.prevent="loadPatients">
        <el-form-item>
          <el-input v-model="searchText" placeholder="搜索姓名/电话" clearable @clear="loadPatients" style="width: 240px;">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadPatients">查询</el-button>
        </el-form-item>
      </el-form>

      <!-- 患者表格 -->
      <el-table :data="patients" stripe style="width: 100%" @row-click="goDetail">
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="姓名" width="100" />
        <el-table-column prop="gender" label="性别" width="60" />
        <el-table-column prop="phone" label="电话" width="130" />
        <el-table-column prop="birth_date" label="出生日期" width="110" />
        <el-table-column prop="constitution_type" label="体质" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.constitution_type" size="small" type="warning">{{ row.constitution_type }}</el-tag>
            <span v-else class="text-muted">未评估</span>
          </template>
        </el-table-column>
        <el-table-column prop="notes" label="备注" show-overflow-tooltip />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click.stop="goDetail(row)">详情</el-button>
            <el-button link type="primary" @click.stop="startVisit(row)">就诊</el-button>
            <el-button link type="danger" @click.stop="deletePatient(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="total, prev, pager, next"
          @current-change="loadPatients"
        />
      </div>
    </el-card>

    <!-- 新增患者对话框 -->
    <el-dialog v-model="showAddDialog" title="新增患者" width="500px" destroy-on-close>
      <el-form :model="newPatient" label-width="80px" label-position="right">
        <el-form-item label="姓名" required>
          <el-input v-model="newPatient.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="newPatient.gender">
            <el-radio value="男">男</el-radio>
            <el-radio value="女">女</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="出生日期">
          <el-date-picker v-model="newPatient.birth_date" type="date" value-format="YYYY-MM-DD" placeholder="选择日期" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="newPatient.phone" placeholder="请输入电话" />
        </el-form-item>
        <el-form-item label="身份证号">
          <el-input v-model="newPatient.id_card" placeholder="请输入身份证号" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="newPatient.address" placeholder="请输入地址" />
        </el-form-item>
        <el-form-item label="过敏史">
          <el-input v-model="newPatient.allergy_history" type="textarea" :rows="2" placeholder="如：青霉素过敏" />
        </el-form-item>
        <el-form-item label="既往史">
          <el-input v-model="newPatient.medical_history" type="textarea" :rows="2" placeholder="重要疾病史" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="newPatient.notes" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="addPatient" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import api from '@/utils/api'

const router = useRouter()
const patients = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const searchText = ref('')
const showAddDialog = ref(false)
const submitting = ref(false)

const newPatient = ref({
  name: '',
  gender: '男',
  birth_date: '',
  phone: '',
  id_card: '',
  address: '',
  allergy_history: '',
  medical_history: '',
  notes: '',
})

async function loadPatients() {
  try {
    const params: any = { page: page.value, page_size: pageSize.value }
    if (searchText.value) params.search = searchText.value
    const res = await api.get('/patients', { params }) as any
    patients.value = res.items || []
    total.value = res.total || 0
  } catch {}
}

function goDetail(row: any) {
  router.push(`/patients/${row.id}`)
}

function startVisit(row: any) {
  router.push({ path: `/patients/${row.id}/visit`, query: { name: row.name } })
}

async function addPatient() {
  if (!newPatient.value.name.trim()) {
    ElMessage.warning('请输入患者姓名')
    return
  }
  submitting.value = true
  try {
    await api.post('/patients', newPatient.value)
    ElMessage.success('患者添加成功')
    showAddDialog.value = false
    newPatient.value = { name: '', gender: '男', birth_date: '', phone: '', id_card: '', address: '', allergy_history: '', medical_history: '', notes: '' }
    loadPatients()
  } catch {
    // 已被拦截器处理
  } finally {
    submitting.value = false
  }
}

async function deletePatient(row: any) {
  await ElMessageBox.confirm(`确定删除患者 "${row.name}" 吗？`, '确认删除', { type: 'warning' })
  try {
    await api.delete(`/patients/${row.id}`)
    ElMessage.success('删除成功')
    loadPatients()
  } catch {}
}

onMounted(loadPatients)
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
.text-muted {
  color: #c0c4cc;
  font-size: 13px;
}
</style>
