<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="4" v-for="card in statCards" :key="card.title">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-card-body">
            <div class="stat-icon" :style="{ backgroundColor: card.color + '20', color: card.color }">
              <el-icon :size="28"><component :is="card.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ card.value }}</div>
              <div class="stat-title">{{ card.title }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区 -->
    <el-row :gutter="20" style="margin-top:20px;">
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header><span>📈 近7日就诊趋势</span></template>
          <div ref="visitChartRef" style="height:280px;"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <span>⚠️ 库存预警</span>
              <el-tag :type="alerts.length > 0 ? 'danger' : 'success'" size="small">
                {{ alerts.length > 0 ? `${alerts.length} 项预警` : '库存正常' }}
              </el-tag>
            </div>
          </template>
          <el-empty v-if="alerts.length === 0" description="暂无预警" :image-size="60" />
          <div v-else class="alert-list">
            <div v-for="alert in alerts" :key="alert.herb_id" class="alert-item">
              <el-tag type="danger" size="small">{{ alert.alert_type }}</el-tag>
              <span class="alert-herb">{{ alert.herb_name }}</span>
              <span class="alert-qty">{{ alert.current_quantity }}g / 最低{{ alert.min_stock }}g</span>
              <el-button link type="primary" size="small" @click="$router.push('/herbs/inventory')">处理</el-button>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 快捷操作 + 待办 -->
    <el-row :gutter="20" style="margin-top:20px;">
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header><span>🏥 快捷操作</span></template>
          <el-row :gutter="16">
            <el-col :span="6" v-for="action in quickActions" :key="action.title">
              <div class="quick-action" @click="$router.push(action.route)">
                <el-icon :size="28" :color="action.color"><component :is="action.icon" /></el-icon>
                <div class="action-title">{{ action.title }}</div>
                <div class="action-desc">{{ action.desc }}</div>
              </div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header>
            <div style="display:flex;justify-content:space-between;align-items:center;">
              <span>📋 待办事项</span>
            </div>
          </template>
          <div class="todo-list">
            <div v-if="pendingCount > 0" class="todo-item">
              <el-tag type="warning" size="small">待审核</el-tag>
              <span>{{ pendingCount }} 张处方待审核</span>
              <el-button link type="primary" size="small" @click="$router.push('/prescriptions')">去处理</el-button>
            </div>
            <div v-if="alerts.length > 0" class="todo-item">
              <el-tag type="danger" size="small">库存预警</el-tag>
              <span>{{ alerts.length }} 种药材库存不足</span>
              <el-button link type="primary" size="small" @click="$router.push('/herbs/inventory')">去处理</el-button>
            </div>
            <el-empty v-if="pendingCount === 0 && alerts.length === 0" description="暂无待办事项" :image-size="60" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { User, FirstAidKit, Document, ChatDotRound, Warning } from '@element-plus/icons-vue'
import api from '@/utils/api'

const statCards = ref([
  { title: '今日就诊', value: 0, icon: 'User', color: '#8B4513' },
  { title: '患者总数', value: 0, icon: 'User', color: '#52C41A' },
  { title: '今日处方', value: 0, icon: 'Document', color: '#1890FF' },
  { title: '药品总数', value: 0, icon: 'FirstAidKit', color: '#13C2C2' },
  { title: '待审核', value: 0, icon: 'Warning', color: '#FAAD14' },
  { title: '库存预警', value: 0, icon: 'Warning', color: '#F5222D' },
])

const quickActions = [
  { title: '新增患者', desc: '录入信息', route: '/patients', icon: 'User', color: '#8B4513' },
  { title: '开具处方', desc: '选方/自拟', route: '/prescriptions/new', icon: 'Document', color: '#1890FF' },
  { title: '智能问诊', desc: 'AI辨证', route: '/diagnosis', icon: 'ChatDotRound', color: '#722ED1' },
  { title: '体质辨识', desc: '九种体质', route: '/constitution', icon: 'TrendCharts', color: '#13C2C2' },
  { title: '药材入库', desc: '入库登记', route: '/herbs/inventory', icon: 'Box', color: '#52C41A' },
  { title: '知识检索', desc: '典籍查询', route: '/knowledge', icon: 'Search', color: '#FAAD14' },
  { title: '经典方库', desc: '方剂浏览', route: '/classic-formulas', icon: 'Notebook', color: '#8B4513' },
  { title: '系统设置', desc: '配置管理', route: '/settings', icon: 'Setting', color: '#999' },
]

const alerts = ref<any[]>([])
const pendingCount = ref(0)
const visitChartRef = ref<HTMLElement>()
const visitTrend = ref<any[]>([])

async function loadDashboard() {
  try {
    const [dashData, alertsData] = await Promise.all([
      api.get('/stats/dashboard') as any,
      api.get('/herbs/inventory/alerts') as any,
    ])
    statCards.value[0].value = dashData.today_visits || 0
    statCards.value[1].value = dashData.total_patients || 0
    statCards.value[2].value = dashData.today_prescriptions || 0
    statCards.value[3].value = dashData.total_herbs || 0
    statCards.value[4].value = dashData.pending_prescriptions || 0
    statCards.value[5].value = dashData.low_stock_count || 0

    pendingCount.value = dashData.pending_prescriptions || 0
    alerts.value = alertsData || []
    visitTrend.value = dashData.visit_trend || []

    // 绘制图表
    await nextTick()
    renderVisitChart()
  } catch {
    // 后端未启动
  }
}

function renderVisitChart() {
  if (!visitChartRef.value || visitTrend.value.length === 0) return

  // 动态导入 ECharts
  import('echarts').then((echarts) => {
    const chart = echarts.init(visitChartRef.value!)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 40, right: 20, top: 20, bottom: 30 },
      xAxis: {
        type: 'category',
        data: visitTrend.value.map((d: any) => d.date),
        axisLabel: { color: '#666' },
      },
      yAxis: {
        type: 'value',
        minInterval: 1,
        axisLabel: { color: '#666' },
      },
      series: [{
        type: 'bar',
        data: visitTrend.value.map((d: any) => d.count),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#8B4513' },
            { offset: 1, color: '#D4A574' },
          ]),
          borderRadius: [4, 4, 0, 0],
        },
        barWidth: '40%',
      }],
    })
    // 响应式
    window.addEventListener('resize', () => chart.resize())
  })
}

onMounted(loadDashboard)
</script>

<style scoped lang="scss">
.dashboard {
  .stat-card {
    .stat-card-body {
      display: flex;
      align-items: center;
      gap: 12px;

      .stat-icon {
        width: 48px;
        height: 48px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
      }

      .stat-info {
        .stat-value {
          font-size: 24px;
          font-weight: 700;
          color: #333;
        }
        .stat-title {
          font-size: 12px;
          color: #999;
          margin-top: 2px;
        }
      }
    }
  }

  .quick-action {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16px 8px;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      background: #f5f0eb;
      transform: translateY(-2px);
    }

    .action-title {
      font-size: 13px;
      font-weight: 600;
      margin-top: 6px;
    }

    .action-desc {
      font-size: 11px;
      color: #999;
      margin-top: 2px;
    }
  }

  .alert-list, .todo-list {
    .alert-item, .todo-item {
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 0;
      border-bottom: 1px solid #f0f0f0;

      .alert-herb, span:nth-child(2) {
        font-weight: 500;
        flex: 1;
      }

      .alert-qty {
        font-size: 13px;
        color: #999;
      }
    }
  }
}
</style>
