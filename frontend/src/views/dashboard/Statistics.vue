<template>
  <div class="statistics-page">
    <el-card shadow="hover">
      <template #header>
        <div style="display:flex;justify-content:space-between;align-items:center;">
          <span>📊 统计报表</span>
          <el-radio-group v-model="period" size="small" @change="loadAll">
            <el-radio-button :value="7">近7天</el-radio-button>
            <el-radio-button :value="30">近30天</el-radio-button>
            <el-radio-button :value="90">近90天</el-radio-button>
          </el-radio-group>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-change="onTabChange">
        <!-- 就诊统计 -->
        <el-tab-pane label="就诊趋势" name="visits">
          <div ref="visitChartRef" style="height:350px;"></div>
          <el-divider />
          <h4>常见证型 TOP10</h4>
          <el-table :data="syndromeStats" stripe size="small" v-if="syndromeStats.length">
            <el-table-column type="index" label="排名" width="60" />
            <el-table-column prop="name" label="证型" />
            <el-table-column prop="count" label="频次" width="80" />
          </el-table>
          <el-empty v-else description="暂无数据" :image-size="60" />
        </el-tab-pane>

        <!-- 用药统计 -->
        <el-tab-pane label="用药分析" name="herbs">
          <div ref="herbChartRef" style="height:350px;"></div>
          <el-divider />
          <el-table :data="herbUsage" stripe size="small">
            <el-table-column type="index" label="排名" width="60" />
            <el-table-column prop="name" label="药味" width="120" />
            <el-table-column prop="usage_count" label="使用次数" width="100" />
            <el-table-column prop="total_dose" label="总用量(g)" width="100" />
          </el-table>
        </el-tab-pane>

        <!-- 处方统计 -->
        <el-tab-pane label="处方统计" name="prescriptions">
          <el-row :gutter="20">
            <el-col :span="12">
              <div ref="prescriptionStatusRef" style="height:300px;"></div>
            </el-col>
            <el-col :span="12">
              <div ref="formulaChartRef" style="height:300px;"></div>
            </el-col>
          </el-row>
          <el-divider />
          <el-descriptions :column="3" border>
            <el-descriptions-item label="统计周期">近{{ period }}天</el-descriptions-item>
            <el-descriptions-item label="处方总数">{{ prescriptionStats.total || 0 }}</el-descriptions-item>
          </el-descriptions>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import api from '@/utils/api'

const period = ref(30)
const activeTab = ref('visits')

const visitChartRef = ref<HTMLElement>()
const herbChartRef = ref<HTMLElement>()
const prescriptionStatusRef = ref<HTMLElement>()
const formulaChartRef = ref<HTMLElement>()

const dailyStats = ref<any[]>([])
const syndromeStats = ref<any[]>([])
const herbUsage = ref<any[]>([])
const prescriptionStats = ref<any>({ total: 0, status_stats: [], formula_stats: [] })

const chartInstances: any[] = []

async function loadAll() {
  await Promise.all([
    loadVisitStats(),
    loadHerbStats(),
    loadPrescriptionStats(),
  ])
}

async function loadVisitStats() {
  try {
    const res = await api.get('/stats/visits', { params: { days: period.value } }) as any
    dailyStats.value = res.daily_stats || []
    syndromeStats.value = res.syndrome_stats || []
    await nextTick()
    renderVisitChart()
  } catch {}
}

async function loadHerbStats() {
  try {
    const res = await api.get('/stats/herbs', { params: { days: period.value } }) as any
    herbUsage.value = res.herb_usage || []
    if (activeTab.value === 'herbs') {
      await nextTick()
      renderHerbChart()
    }
  } catch {}
}

async function loadPrescriptionStats() {
  try {
    const res = await api.get('/stats/prescriptions', { params: { days: period.value } }) as any
    prescriptionStats.value = res || {}
    if (activeTab.value === 'prescriptions') {
      await nextTick()
      renderPrescriptionCharts()
    }
  } catch {}
}

function onTabChange(tab: string) {
  nextTick(() => {
    if (tab === 'herbs') renderHerbChart()
    if (tab === 'prescriptions') renderPrescriptionCharts()
  })
}

function renderVisitChart() {
  if (!visitChartRef.value || dailyStats.value.length === 0) return
  import('echarts').then((echarts) => {
    const chart = echarts.init(visitChartRef.value!)
    chartInstances.push(chart)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 50, right: 20, top: 20, bottom: 40 },
      xAxis: {
        type: 'category',
        data: dailyStats.value.map((d: any) => d.date.slice(5)),
        axisLabel: { rotate: 45, color: '#666', fontSize: 11 },
      },
      yAxis: { type: 'value', minInterval: 1 },
      series: [{
        type: 'line',
        data: dailyStats.value.map((d: any) => d.count),
        smooth: true,
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(139,69,19,0.3)' },
            { offset: 1, color: 'rgba(139,69,19,0.05)' },
          ]),
        },
        lineStyle: { color: '#8B4513', width: 2 },
        itemStyle: { color: '#8B4513' },
      }],
    })
    window.addEventListener('resize', () => chart.resize())
  })
}

function renderHerbChart() {
  if (!herbChartRef.value || herbUsage.value.length === 0) return
  import('echarts').then((echarts) => {
    const chart = echarts.init(herbChartRef.value!)
    chartInstances.push(chart)
    const top15 = herbUsage.value.slice(0, 15)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 100, right: 20, top: 10, bottom: 20 },
      xAxis: { type: 'value' },
      yAxis: {
        type: 'category',
        data: top15.map((h: any) => h.name).reverse(),
        axisLabel: { color: '#333' },
      },
      series: [{
        type: 'bar',
        data: top15.map((h: any) => h.usage_count).reverse(),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#D4A574' },
            { offset: 1, color: '#8B4513' },
          ]),
          borderRadius: [0, 4, 4, 0],
        },
      }],
    })
    window.addEventListener('resize', () => chart.resize())
  })
}

function renderPrescriptionCharts() {
  import('echarts').then((echarts) => {
    // 状态饼图
    if (prescriptionStatusRef.value && prescriptionStats.value.status_stats?.length) {
      const chart1 = echarts.init(prescriptionStatusRef.value!)
      chartInstances.push(chart1)
      const colorMap: Record<string, string> = { '已开': '#FAAD14', '已审核': '#1890FF', '已发药': '#52C41A', '已取消': '#F5222D' }
      chart1.setOption({
        tooltip: { trigger: 'item' },
        legend: { bottom: 0 },
        series: [{
          type: 'pie',
          radius: ['40%', '65%'],
          data: prescriptionStats.value.status_stats.map((s: any) => ({
            name: s.status,
            value: s.count,
            itemStyle: { color: colorMap[s.status] || '#999' },
          })),
          label: { formatter: '{b}: {c}' },
        }],
      })
      window.addEventListener('resize', () => chart1.resize())
    }

    // 方剂柱图
    if (formulaChartRef.value && prescriptionStats.value.formula_stats?.length) {
      const chart2 = echarts.init(formulaChartRef.value!)
      chartInstances.push(chart2)
      chart2.setOption({
        tooltip: { trigger: 'axis' },
        grid: { left: 80, right: 20, top: 10, bottom: 20 },
        xAxis: { type: 'value' },
        yAxis: {
          type: 'category',
          data: prescriptionStats.value.formula_stats.map((f: any) => f.name).reverse(),
        },
        series: [{
          type: 'bar',
          data: prescriptionStats.value.formula_stats.map((f: any) => f.count).reverse(),
          itemStyle: {
            color: '#8B4513',
            borderRadius: [0, 4, 4, 0],
          },
        }],
      })
      window.addEventListener('resize', () => chart2.resize())
    }
  })
}

onMounted(loadAll)
</script>
