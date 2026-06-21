<template>
  <div class="dashboard">
    <div class="page-header">
      <h1>分析仪表盘</h1>
      <p class="subtitle">查看您的 Claude 使用统计数据</p>
    </div>

    <div class="stats-cards">
      <div class="stat-card">
        <div class="stat-icon sessions">💬</div>
        <div class="stat-content">
          <div class="stat-value">{{ summary.total_sessions }}</div>
          <div class="stat-label">总会话数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon messages">📝</div>
        <div class="stat-content">
          <div class="stat-value">{{ summary.total_messages }}</div>
          <div class="stat-label">总消息数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon tokens">🔢</div>
        <div class="stat-content">
          <div class="stat-value">{{ formatNumber(summary.total_tokens) }}</div>
          <div class="stat-label">总 Token 数</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon date">📅</div>
        <div class="stat-content">
          <div class="stat-value date-value">{{ dateRange }}</div>
          <div class="stat-label">数据时间范围</div>
        </div>
      </div>
    </div>

    <div class="filter-bar">
      <div class="filter-item">
        <label>时间范围：</label>
        <select v-model="days" class="filter-select">
          <option :value="7">最近 7 天</option>
          <option :value="30">最近 30 天</option>
          <option :value="90">最近 90 天</option>
          <option :value="365">最近一年</option>
        </select>
      </div>
    </div>

    <div class="charts-grid">
      <div class="chart-card card">
        <h3>每日会话数量</h3>
        <div class="chart-wrapper">
          <ChartView :option="dailySessionsOption" />
        </div>
      </div>

      <div class="chart-card card">
        <h3>每日 Token 消耗</h3>
        <div class="chart-wrapper">
          <ChartView :option="dailyTokensOption" />
        </div>
      </div>

      <div class="chart-card card">
        <h3>模型使用分布</h3>
        <div class="chart-wrapper">
          <ChartView :option="modelDistributionOption" />
        </div>
      </div>

      <div class="chart-card card">
        <h3>每日使用时间分布</h3>
        <div class="chart-wrapper">
          <ChartView :option="hourlyDistributionOption" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import ChartView from '@/components/ChartView.vue'
import {
  getStatsSummary,
  getDailySessions,
  getDailyTokens,
  getModelDistribution,
  getHourlyDistribution,
} from '@/api/stats'

const days = ref(30)
const summary = ref({
  total_sessions: 0,
  total_messages: 0,
  total_tokens: 0,
  total_input_tokens: 0,
  total_output_tokens: 0,
  date_range_start: null,
  date_range_end: null,
})

const dailySessions = ref([])
const dailyTokens = ref([])
const modelDistribution = ref([])
const hourlyDistribution = ref([])

const dateRange = computed(() => {
  if (summary.value.date_range_start && summary.value.date_range_end) {
    return `${summary.value.date_range_start} ~ ${summary.value.date_range_end}`
  }
  return '暂无数据'
})

const formatNumber = (num) => {
  if (!num) return '0'
  if (num >= 1000000) return (num / 1000000).toFixed(2) + 'M'
  if (num >= 1000) return (num / 1000).toFixed(1) + 'K'
  return num.toString()
}

const dailySessionsOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '10%',
    containLabel: true,
  },
  xAxis: {
    type: 'category',
    data: dailySessions.value.map((d) => d.date.slice(5)),
    axisLabel: { fontSize: 10, rotate: 45 },
  },
  yAxis: {
    type: 'value',
    name: '会话数',
    nameTextStyle: { fontSize: 12 },
  },
  series: [
    {
      name: '会话数',
      type: 'bar',
      data: dailySessions.value.map((d) => d.count),
      itemStyle: {
        color: {
          type: 'linear',
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: '#89b4fa' },
            { offset: 1, color: '#b4befe' },
          ],
        },
        borderRadius: [4, 4, 0, 0],
      },
    },
  ],
}))

const dailyTokensOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'cross' },
  },
  legend: {
    data: ['输入 Token', '输出 Token'],
    top: 0,
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '15%',
    containLabel: true,
  },
  xAxis: {
    type: 'category',
    data: dailyTokens.value.map((d) => d.date.slice(5)),
    axisLabel: { fontSize: 10, rotate: 45 },
  },
  yAxis: {
    type: 'value',
    name: 'Token 数',
    nameTextStyle: { fontSize: 12 },
  },
  series: [
    {
      name: '输入 Token',
      type: 'line',
      stack: 'Total',
      areaStyle: { opacity: 0.3 },
      data: dailyTokens.value.map((d) => d.input_tokens),
      color: '#a6e3a1',
    },
    {
      name: '输出 Token',
      type: 'line',
      stack: 'Total',
      areaStyle: { opacity: 0.3 },
      data: dailyTokens.value.map((d) => d.output_tokens),
      color: '#f9e2af',
    },
  ],
}))

const modelDistributionOption = computed(() => ({
  tooltip: {
    trigger: 'item',
    formatter: '{b}: {c} 个 ({d}%)',
  },
  legend: {
    orient: 'vertical',
    right: '5%',
    top: 'center',
    fontSize: 12,
  },
  series: [
    {
      name: '模型分布',
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['35%', '50%'],
      avoidLabelOverlap: false,
      itemStyle: {
        borderRadius: 8,
        borderColor: '#fff',
        borderWidth: 2,
      },
      label: {
        show: false,
        position: 'center',
      },
      emphasis: {
        label: {
          show: true,
          fontSize: 16,
          fontWeight: 'bold',
        },
      },
      labelLine: {
        show: false,
      },
      data: modelDistribution.value.map((d) => ({
        value: d.count,
        name: d.model,
      })),
      color: ['#89b4fa', '#a6e3a1', '#f9e2af', '#fab387', '#cba6f7', '#f38ba8'],
    },
  ],
}))

const hourlyDistributionOption = computed(() => ({
  tooltip: {
    trigger: 'axis',
    axisPointer: { type: 'shadow' },
    formatter: (params) => {
      const d = params[0]
      return `${d.axisValue}时: ${d.value} 个会话`
    },
  },
  grid: {
    left: '3%',
    right: '4%',
    bottom: '3%',
    top: '10%',
    containLabel: true,
  },
  xAxis: {
    type: 'category',
    data: hourlyDistribution.value.map((d) => String(d.hour).padStart(2, '0')),
    axisLabel: { fontSize: 10 },
    name: '小时',
    nameTextStyle: { fontSize: 12 },
  },
  yAxis: {
    type: 'value',
    name: '会话数',
    nameTextStyle: { fontSize: 12 },
  },
  series: [
    {
      name: '会话数',
      type: 'bar',
      data: hourlyDistribution.value.map((d) => d.count),
      itemStyle: {
        color: (params) => {
          const hour = params.dataIndex
          if (hour >= 9 && hour < 18) return '#89b4fa'
          if (hour >= 18 && hour < 22) return '#fab387'
          return '#6c7086'
        },
        borderRadius: [4, 4, 0, 0],
      },
    },
  ],
}))

const loadData = async () => {
  try {
    const [summaryRes, dailySess, dailyTok, modelDist, hourlyDist] =
      await Promise.all([
        getStatsSummary(),
        getDailySessions(days.value),
        getDailyTokens(days.value),
        getModelDistribution(days.value),
        getHourlyDistribution(days.value),
      ])
    summary.value = summaryRes
    dailySessions.value = dailySess
    dailyTokens.value = dailyTok
    modelDistribution.value = modelDist
    hourlyDistribution.value = hourlyDist
  } catch (err) {
    console.error('Failed to load stats:', err)
  }
}

watch(days, loadData)

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 4px;
}

.subtitle {
  color: #666;
  font-size: 14px;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.sessions {
  background: #e0e7ff;
}
.stat-icon.messages {
  background: #dcfce7;
}
.stat-icon.tokens {
  background: #fef3c7;
}
.stat-icon.date {
  background: #fce7f3;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #111;
  margin-bottom: 4px;
}

.stat-value.date-value {
  font-size: 13px;
}

.stat-label {
  font-size: 13px;
  color: #666;
}

.filter-bar {
  background: #fff;
  border-radius: 12px;
  padding: 16px 20px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-item label {
  font-size: 14px;
  color: #555;
}

.filter-select {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background: #fff;
  cursor: pointer;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.chart-card {
  padding: 20px;
}

.chart-card h3 {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #333;
}

.chart-wrapper {
  height: 300px;
}
</style>
