<template>
  <div class="classic-formula-lib">
    <el-card shadow="hover">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span>📖 经典方库</span>
        </div>
      </template>

      <el-form :inline="true" @submit.prevent="loadFormulas">
        <el-form-item>
          <el-input v-model="searchText" placeholder="搜索方名/功效" clearable @clear="loadFormulas" style="width:220px">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-select v-model="sourceFilter" placeholder="出处筛选" clearable @change="loadFormulas" style="width:140px">
            <el-option v-for="s in sources" :key="s" :label="s" :value="s" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadFormulas">查询</el-button>
        </el-form-item>
      </el-form>

      <el-row :gutter="16">
        <el-col :span="8" v-for="formula in formulas" :key="formula.id">
          <el-card shadow="hover" class="formula-card" @click="viewFormula(formula)">
            <div class="formula-name">{{ formula.name }}</div>
            <div class="formula-source" v-if="formula.source">
              <el-tag size="small" type="info">{{ formula.source }}</el-tag>
            </div>
            <div class="formula-efficacy" v-if="formula.efficacy">{{ formula.efficacy }}</div>
            <div class="formula-composition" v-if="formula.composition?.herbs">
              <span v-for="(h, idx) in formula.composition.herbs" :key="idx" class="herb-chip">
                {{ h.herb }}{{ h.dose ? h.dose + 'g' : '' }}
              </span>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </el-card>

    <!-- 方剂详情 -->
    <el-dialog v-model="detailVisible" :title="currentFormula?.name || '方剂详情'" width="620px" destroy-on-close>
      <template v-if="currentFormula">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="方名">{{ currentFormula.name }}</el-descriptions-item>
          <el-descriptions-item label="出处">{{ currentFormula.source || '-' }}</el-descriptions-item>
          <el-descriptions-item label="功效" :span="2">{{ currentFormula.efficacy || '-' }}</el-descriptions-item>
          <el-descriptions-item label="主治" :span="2">{{ currentFormula.indications || '-' }}</el-descriptions-item>
          <el-descriptions-item label="用法" :span="2">{{ currentFormula.usage || '-' }}</el-descriptions-item>
        </el-descriptions>

        <el-divider content-position="left">组成</el-divider>
        <div class="formula-herbs" v-if="currentFormula.composition?.herbs">
          <el-table :data="currentFormula.composition.herbs" stripe size="small">
            <el-table-column prop="herb" label="药味" width="100" />
            <el-table-column prop="dose" label="剂量" width="80">
              <template #default="{ row }">{{ row.dose ? row.dose + 'g' : '-' }}</template>
            </el-table-column>
            <el-table-column prop="special_method" label="煎法" width="80">
              <template #default="{ row }">{{ row.special_method || '-' }}</template>
            </el-table-column>
            <el-table-column prop="note" label="备注" show-overflow-tooltip>
              <template #default="{ row }">{{ row.note || '-' }}</template>
            </el-table-column>
          </el-table>
        </div>

        <!-- 加减变化 -->
        <template v-if="currentFormula.modifications?.changes?.length">
          <el-divider content-position="left">加减变化</el-divider>
          <div class="formula-modifications">
            <div v-for="(mod, idx) in currentFormula.modifications.changes" :key="idx" class="mod-item">
              <div class="mod-condition">
                <el-tag size="small" type="warning">{{ mod.condition || `变化${idx + 1}` }}</el-tag>
              </div>
              <div class="mod-detail">
                <span v-if="mod.add" class="mod-add">+ {{ mod.add }}</span>
                <span v-if="mod.remove" class="mod-remove">- {{ mod.remove }}</span>
              </div>
            </div>
          </div>
        </template>

        <div style="margin-top:16px;text-align:right;">
          <el-button type="primary" @click="useInPrescription(currentFormula)">
            引入到处方编辑器
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search } from '@element-plus/icons-vue'
import { useRouter } from 'vue-router'
import api from '@/utils/api'

const router = useRouter()
const formulas = ref<any[]>([])
const searchText = ref('')
const sourceFilter = ref('')
const detailVisible = ref(false)
const currentFormula = ref<any>(null)

const sources = computed(() => {
  const set = new Set(formulas.value.map((f: any) => f.source).filter(Boolean))
  return Array.from(set)
})

async function loadFormulas() {
  try {
    const params: any = {}
    if (searchText.value) params.search = searchText.value
    if (sourceFilter.value) params.source = sourceFilter.value
    formulas.value = (await api.get('/prescriptions/classic-formulas', { params })) as any
  } catch {}
}

function viewFormula(formula: any) {
  currentFormula.value = formula
  detailVisible.value = true
}

function useInPrescription(formula: any) {
  detailVisible.value = false
  // 跳转到处方编辑器，通过 router query 传递 formula_id
  router.push({ path: '/prescriptions/new', query: { formula_id: formula.id } })
}

onMounted(loadFormulas)
</script>

<style scoped lang="scss">
.classic-formula-lib {
  .formula-card {
    margin-bottom: 16px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(139, 69, 19, 0.15);
    }

    .formula-name {
      font-size: 16px;
      font-weight: 700;
      color: #8B4513;
      margin-bottom: 6px;
    }

    .formula-source {
      margin-bottom: 6px;
    }

    .formula-efficacy {
      font-size: 13px;
      color: #666;
      margin-bottom: 8px;
    }

    .formula-composition {
      .herb-chip {
        display: inline-block;
        padding: 2px 6px;
        background: #f5f0eb;
        border-radius: 4px;
        font-size: 12px;
        margin: 2px;
        color: #8B4513;
      }
    }
  }
}

.formula-modifications {
  .mod-item {
    padding: 8px 0;
    border-bottom: 1px dashed #e8e0d8;

    .mod-detail {
      margin-top: 4px;
      font-size: 13px;

      .mod-add { color: #52c41a; margin-right: 12px; }
      .mod-remove { color: #f56c6c; }
    }
  }
}
</style>
