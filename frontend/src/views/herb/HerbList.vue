<template>
  <div class="herb-list">
    <el-card shadow="hover">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span>💊 药材字典</span>
          <el-button type="primary" size="small" @click="showAddDialog = true">
            <el-icon><Plus /></el-icon> 新增药材
          </el-button>
        </div>
      </template>
      <el-form :inline="true" @submit.prevent="loadHerbs">
        <el-form-item>
          <el-input v-model="searchText" placeholder="搜索药名/异名" clearable @clear="loadHerbs" style="width:200px">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-select v-model="categoryFilter" placeholder="分类筛选" clearable @change="loadHerbs" style="width:140px">
            <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadHerbs">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="herbs" stripe style="width:100%">
        <el-table-column prop="name" label="正名" width="100" />
        <el-table-column prop="aliases" label="异名" width="160">
          <template #default="{ row }">
            <span v-if="row.aliases && row.aliases.length">{{ row.aliases.join('、') }}</span>
            <span v-else class="text-muted">-</span>
          </template>
        </el-table-column>
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="nature" label="药性" width="60" />
        <el-table-column prop="flavor" label="药味" width="90" />
        <el-table-column prop="meridian_tropism" label="归经" width="120" show-overflow-tooltip />
        <el-table-column prop="efficacy" label="功效" show-overflow-tooltip />
        <el-table-column label="剂量(g)" width="100">
          <template #default="{ row }">{{ row.dosage_min }}~{{ row.dosage_max }}</template>
        </el-table-column>
        <el-table-column prop="toxicity" label="毒性" width="80">
          <template #default="{ row }">
            <el-tag :type="toxicityTag(row.toxicity)" size="small">{{ row.toxicity }}</el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="showAddDialog" title="新增药材" width="500px" destroy-on-close>
      <el-form :model="newHerb" label-width="80px">
        <el-form-item label="正名" required><el-input v-model="newHerb.name" /></el-form-item>
        <el-form-item label="异名"><el-input v-model="newHerb.aliasesStr" placeholder="逗号分隔" /></el-form-item>
        <el-form-item label="分类"><el-input v-model="newHerb.category" placeholder="如：解表药" /></el-form-item>
        <el-form-item label="药性"><el-select v-model="newHerb.nature" style="width:100%">
          <el-option v-for="n in ['寒','热','温','凉','平']" :key="n" :label="n" :value="n" />
        </el-select></el-form-item>
        <el-form-item label="药味"><el-input v-model="newHerb.flavor" /></el-form-item>
        <el-form-item label="归经"><el-input v-model="newHerb.meridian_tropism" /></el-form-item>
        <el-form-item label="功效"><el-input v-model="newHerb.efficacy" type="textarea" :rows="2" /></el-form-item>
        <el-row :gutter="12">
          <el-col :span="12"><el-form-item label="最小剂量"><el-input-number v-model="newHerb.dosage_min" :min="0" :precision="1" /></el-form-item></el-col>
          <el-col :span="12"><el-form-item label="最大剂量"><el-input-number v-model="newHerb.dosage_max" :min="0" :precision="1" /></el-form-item></el-col>
        </el-row>
        <el-form-item label="毒性"><el-select v-model="newHerb.toxicity" style="width:100%">
          <el-option v-for="t in ['无毒','有小毒','有毒','有大毒']" :key="t" :label="t" :value="t" />
        </el-select></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="addHerb">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import api from '@/utils/api'

const herbs = ref<any[]>([])
const searchText = ref('')
const categoryFilter = ref('')
const showAddDialog = ref(false)
const categories = ['解表药', '清热药', '泻下药', '祛风湿药', '化湿药', '利水渗湿药', '温里药', '理气药', '消食药', '止血药', '活血化瘀药', '化痰止咳平喘药', '安神药', '平肝息风药', '开窍药', '补虚药', '收涩药', '涌吐药']

const newHerb = ref({ name: '', aliasesStr: '', category: '', nature: '平', flavor: '', meridian_tropism: '', efficacy: '', dosage_min: 3, dosage_max: 10, toxicity: '无毒' })

function toxicityTag(t: string) {
  if (t === '有大毒') return 'danger'
  if (t === '有毒') return 'warning'
  if (t === '有小毒') return 'info'
  return 'success'
}

async function loadHerbs() {
  try {
    const params: any = {}
    if (searchText.value) params.search = searchText.value
    if (categoryFilter.value) params.category = categoryFilter.value
    herbs.value = (await api.get('/herbs', { params })) as any
  } catch {}
}

async function addHerb() {
  if (!newHerb.value.name.trim()) { ElMessage.warning('请输入药名'); return }
  try {
    const payload: any = { ...newHerb.value }
    payload.aliases = newHerb.value.aliasesStr ? newHerb.value.aliasesStr.split(/[,，、]/).map((s: string) => s.trim()).filter(Boolean) : null
    delete payload.aliasesStr
    await api.post('/herbs', payload)
    ElMessage.success('药材添加成功')
    showAddDialog.value = false
    loadHerbs()
  } catch {}
}

onMounted(loadHerbs)
</script>

<style scoped>.text-muted { color: #c0c4cc; }</style>
