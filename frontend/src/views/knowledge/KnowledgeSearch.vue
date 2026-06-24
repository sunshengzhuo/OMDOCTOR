<template>
  <div class="knowledge-search">
    <el-card shadow="hover">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span>📚 知识检索</span>
          <el-button size="small" @click="showAddDialog = true">
            <el-icon><Plus /></el-icon> 新增条目
          </el-button>
        </div>
      </template>

      <el-form :inline="true" @submit.prevent="doSearch">
        <el-form-item>
          <el-input v-model="searchText" placeholder="输入关键词或自然语言描述" clearable style="width:360px"
            @keyup.enter="doSearch" size="large">
            <template #prefix><el-icon><Search /></el-icon></template>
          </el-input>
        </el-form-item>
        <el-form-item>
          <el-select v-model="categoryFilter" placeholder="分类筛选" clearable style="width:140px" @change="doSearch">
            <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" @click="doSearch" :loading="searching">检索</el-button>
        </el-form-item>
      </el-form>

      <!-- 搜索结果 -->
      <div v-if="results.length > 0" class="search-results">
        <div v-for="r in results" :key="r.id" class="result-item" @click="viewDetail(r)">
          <div class="result-header">
            <el-tag size="small" :type="r.match_type === '语义' ? 'success' : 'info'">
              {{ r.match_type === '语义' ? '🧠 语义匹配' : '🔍 关键词' }}
            </el-tag>
            <el-tag v-if="r.category" size="small" type="warning">{{ r.category }}</el-tag>
            <span v-if="r.score" class="result-score">相似度: {{ (r.score * 100).toFixed(1) }}%</span>
          </div>
          <div class="result-title">{{ r.title }}</div>
          <div class="result-content">{{ r.content }}</div>
          <div v-if="r.source" class="result-source">出处: {{ r.source }}</div>
        </div>
      </div>

      <el-empty v-else-if="searched" description="未找到相关知识" :image-size="80" />
      <el-empty v-else description="输入关键词开始检索" :image-size="80" />
    </el-card>

    <!-- 知识库统计 -->
    <el-card shadow="hover" style="margin-top:16px;">
      <template #header><span>📊 知识库概况</span></template>
      <el-row :gutter="20">
        <el-col :span="8">
          <el-statistic title="知识条目" :value="stats.total_entries" />
        </el-col>
        <el-col :span="8">
          <el-statistic title="分类数" :value="stats.categories?.length || 0" />
        </el-col>
        <el-col :span="8">
          <div>
            <div style="font-size:12px;color:#999;margin-bottom:4px;">向量索引</div>
            <el-tag :type="stats.vector_store?.available ? 'success' : 'info'" size="small">
              {{ stats.vector_store?.available ? `已索引 ${stats.vector_store?.count || 0} 条` : '未启用' }}
            </el-tag>
          </div>
        </el-col>
      </el-row>
      <div style="margin-top:12px;">
        <el-button size="small" @click="rebuildIndex">重建向量索引</el-button>
      </div>
      <div v-if="stats.categories?.length" style="margin-top:12px;">
        <el-tag v-for="c in stats.categories" :key="c.name" style="margin:4px;">
          {{ c.name }} ({{ c.count }})
        </el-tag>
      </div>
    </el-card>

    <!-- 条目详情 -->
    <el-dialog v-model="detailVisible" :title="currentEntry?.title || '条目详情'" width="650px" destroy-on-close>
      <template v-if="currentEntry">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="分类">{{ currentEntry.category }}</el-descriptions-item>
          <el-descriptions-item label="出处">{{ currentEntry.source || '-' }}</el-descriptions-item>
        </el-descriptions>
        <div class="entry-content" style="margin-top:12px;white-space:pre-wrap;line-height:1.8;">
          {{ currentEntry.content }}
        </div>
      </template>
    </el-dialog>

    <!-- 新增条目对话框 -->
    <el-dialog v-model="showAddDialog" title="📝 新增知识条目" width="600px" destroy-on-close>
      <el-form :model="newEntry" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="newEntry.title" placeholder="如：太阳病提纲" />
        </el-form-item>
        <el-form-item label="分类" required>
          <el-select v-model="newEntry.category" filterable allow-create placeholder="选择或输入分类" style="width:100%">
            <el-option v-for="c in categories" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="出处">
          <el-input v-model="newEntry.source" placeholder="如：伤寒论·辨太阳病脉证并治上" />
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input v-model="newEntry.content" type="textarea" :rows="8" placeholder="知识内容" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="addEntry">添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'
import api from '@/utils/api'

const searchText = ref('')
const categoryFilter = ref('')
const results = ref<any[]>([])
const searching = ref(false)
const searched = ref(false)
const categories = ['条文', '方剂', '药材', '医案', '诊疗规范', '经典理论', '治法']
const stats = ref<any>({ total_entries: 0, categories: [], vector_store: {} })
const detailVisible = ref(false)
const currentEntry = ref<any>(null)
const showAddDialog = ref(false)

const newEntry = ref({ title: '', category: '', source: '', content: '' })

async function doSearch() {
  if (!searchText.value.trim()) return
  searching.value = true
  searched.value = true
  try {
    const params: any = { q: searchText.value, limit: 20 }
    if (categoryFilter.value) params.category = categoryFilter.value
    results.value = (await api.get('/knowledge/search', { params })) as any
  } catch {} finally {
    searching.value = false
  }
}

async function viewDetail(r: any) {
  try {
    // 如果是知识库条目，获取完整内容
    if (r.id && typeof r.id === 'number') {
      currentEntry.value = await api.get(`/knowledge/entries/${r.id}`) as any
    } else {
      currentEntry.value = r
    }
    detailVisible.value = true
  } catch {
    currentEntry.value = r
    detailVisible.value = true
  }
}

async function loadStats() {
  try {
    stats.value = (await api.get('/knowledge/stats')) as any
  } catch {}
}

async function rebuildIndex() {
  try {
    const res = await api.post('/knowledge/rebuild-index') as any
    ElMessage.success(res.message || '索引重建完成')
    loadStats()
  } catch {}
}

async function addEntry() {
  if (!newEntry.value.title || !newEntry.value.category || !newEntry.value.content) {
    ElMessage.warning('请填写必填项')
    return
  }
  try {
    await api.post('/knowledge/entries', null, {
      params: {
        title: newEntry.value.title,
        category: newEntry.value.category,
        content: newEntry.value.content,
        source: newEntry.value.source || undefined,
      },
    })
    ElMessage.success('知识条目已添加')
    showAddDialog.value = false
    newEntry.value = { title: '', category: '', source: '', content: '' }
    loadStats()
  } catch {}
}

onMounted(loadStats)
</script>

<style scoped lang="scss">
.knowledge-search {
  .search-results {
    .result-item {
      padding: 14px;
      border: 1px solid #e8e0d8;
      border-radius: 8px;
      margin-bottom: 12px;
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        background: #faf5f0;
        border-color: #D4A574;
      }

      .result-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 6px;

        .result-score {
          margin-left: auto;
          font-size: 12px;
          color: #52c41a;
        }
      }

      .result-title {
        font-size: 15px;
        font-weight: 600;
        color: #333;
        margin-bottom: 6px;
      }

      .result-content {
        font-size: 13px;
        color: #666;
        line-height: 1.6;
      }

      .result-source {
        margin-top: 6px;
        font-size: 12px;
        color: #999;
      }
    }
  }
}
</style>
