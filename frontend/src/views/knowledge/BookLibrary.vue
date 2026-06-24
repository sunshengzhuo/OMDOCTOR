<template>
  <div class="book-library">
    <el-card shadow="hover">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span>📚 医籍文库</span>
          <span class="total-count" v-if="total > 0">共 {{ total }} 条</span>
        </div>
      </template>

      <!-- 筛选栏 -->
      <div class="filter-bar">
        <el-select v-model="activeCategory" placeholder="全部分类" clearable @change="onFilterChange" style="width:150px">
          <el-option v-for="cat in categories" :key="cat.name" :label="`${cat.name} (${cat.count})`" :value="cat.name" />
        </el-select>
        <el-select v-model="sourceFilter" placeholder="全部出处" clearable @change="onFilterChange" style="width:170px">
          <el-option v-for="s in sources" :key="s.name" :label="`${s.name} (${s.count})`" :value="s.name" />
        </el-select>
        <el-input v-model="searchText" placeholder="搜索标题/内容" clearable @clear="onFilterChange" style="width:220px"
          @keyup.enter="onFilterChange">
          <template #prefix><el-icon><Search /></el-icon></template>
        </el-input>
        <el-button type="primary" @click="onFilterChange">查询</el-button>
      </div>

      <!-- 表格 -->
      <el-table
        :data="entries"
        v-loading="loading"
        stripe
        highlight-current-row
        @row-click="viewDetail"
        style="width:100%; cursor:pointer;"
        :max-height="tableMaxHeight"
      >
        <el-table-column prop="title" label="标题" min-width="220" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="100">
          <template #default="{ row }">
            <el-tag size="small" :type="categoryTagType(row.category)">{{ row.category }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="source" label="出处" width="130" show-overflow-tooltip />
        <el-table-column prop="content_preview" label="内容预览" min-width="300" show-overflow-tooltip />
      </el-table>

      <!-- 分页 -->
      <div class="pagination-wrap" v-if="total > pageSize">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          :page-sizes="[30, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadEntries"
          @size-change="onPageSizeChange"
        />
      </div>
    </el-card>

    <!-- 条目详情弹窗 -->
    <el-dialog v-model="detailVisible" :title="currentEntry?.title || '条目详情'" width="700px" destroy-on-close>
      <template v-if="currentEntry">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="分类">{{ currentEntry.category || '-' }}</el-descriptions-item>
          <el-descriptions-item label="出处">{{ currentEntry.source || '-' }}</el-descriptions-item>
        </el-descriptions>
        <el-divider content-position="left">内容</el-divider>
        <div class="detail-content">{{ currentEntry.content }}</div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import api from '@/utils/api'

interface SourceItem { name: string; count: number }
interface CategoryItem { name: string; count: number }
interface EntryItem {
  id: number
  title: string
  category: string
  source: string
  content_preview: string
}

const entries = ref<EntryItem[]>([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(50)
const loading = ref(false)
const tableMaxHeight = ref(600)

const activeCategory = ref('')
const searchText = ref('')
const sourceFilter = ref('')
const sources = ref<SourceItem[]>([])
const categories = ref<CategoryItem[]>([])

const detailVisible = ref(false)
const currentEntry = ref<any>(null)

// 计算表格最大高度
function calcTableHeight() {
  tableMaxHeight.value = window.innerHeight - 260
}

function categoryTagType(cat: string): string {
  const map: Record<string, string> = {
    '条文': '',
    '医案': 'success',
    '针灸经络': 'warning',
    '针灸腧穴': 'warning',
    '针灸治疗': 'warning',
    '针灸技法': 'warning',
    '方剂': 'danger',
    '经典理论': 'info',
    '诊疗规范': 'info',
  }
  return map[cat] || ''
}

let debounceTimer: ReturnType<typeof setTimeout> | null = null

function onFilterChange() {
  // 防抖：300ms 内重复触发只执行最后一次
  if (debounceTimer) clearTimeout(debounceTimer)
  debounceTimer = setTimeout(() => {
    currentPage.value = 1
    loadEntries()
  }, 300)
}

function onPageSizeChange(size: number) {
  pageSize.value = size
  currentPage.value = 1
  loadEntries()
}

async function loadCategories() {
  try {
    const stats = (await api.get('/knowledge/stats')) as any
    categories.value = stats.categories || []
  } catch {}
}

async function loadSources() {
  try {
    sources.value = (await api.get('/knowledge/sources')) as any
  } catch {}
}

async function loadEntries() {
  loading.value = true
  try {
    const params: any = {
      limit: pageSize.value,
      offset: (currentPage.value - 1) * pageSize.value,
    }
    if (activeCategory.value) params.category = activeCategory.value
    if (sourceFilter.value) params.source = sourceFilter.value
    if (searchText.value) params.search = searchText.value
    const res = (await api.get('/knowledge/entries', { params })) as any
    entries.value = res.items || []
    total.value = res.total || 0
  } catch {
    entries.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

async function viewDetail(row: EntryItem) {
  try {
    currentEntry.value = await api.get(`/knowledge/entries/${row.id}`)
    detailVisible.value = true
  } catch {}
}

onMounted(async () => {
  calcTableHeight()
  window.addEventListener('resize', calcTableHeight)
  await Promise.all([loadCategories(), loadSources()])
  loadEntries()
})

onUnmounted(() => {
  window.removeEventListener('resize', calcTableHeight)
  if (debounceTimer) clearTimeout(debounceTimer)
})
</script>

<style scoped lang="scss">
.book-library {
  .total-count {
    font-size: 14px;
    color: #999;
    font-weight: 400;
  }

  .filter-bar {
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 16px;
    flex-wrap: wrap;
  }

  .pagination-wrap {
    display: flex;
    justify-content: center;
    margin-top: 16px;
  }

  .detail-content {
    font-size: 15px;
    line-height: 1.8;
    color: #333;
    max-height: 60vh;
    overflow-y: auto;
    white-space: pre-wrap;
    padding: 8px 4px;
  }
}
</style>
