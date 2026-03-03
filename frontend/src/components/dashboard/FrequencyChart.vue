<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useTopicsStore } from '@/stores/topics'

use([LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const topicsStore = useTopicsStore()

const currentTopic = computed(() => topicsStore.latestStats?.topic ?? '')

const chartOption = computed(() => {
  const history = topicsStore.statsHistory
  const times = history.map((p) => {
    const d = new Date(p.time)
    return d.toLocaleTimeString('en-US', {
      hour12: false,
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  })
  const values = history.map((p) => Math.round(p.hz * 10) / 10)
  const seriesName = currentTopic.value
    ? (currentTopic.value.length > 20 ? `...${currentTopic.value.slice(-18)}` : currentTopic.value)
    : 'Active Topic'

  return {
    backgroundColor: 'transparent',
    grid: { top: 30, right: 16, bottom: 24, left: 44 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1c2333',
      borderColor: '#252d3a',
      textStyle: { color: '#e2e8f0', fontSize: 12 },
    },
    legend: {
      show: history.length > 0,
      bottom: 0,
      textStyle: { color: '#94a3b8', fontSize: 10 },
      itemWidth: 12,
      itemHeight: 2,
    },
    xAxis: {
      type: 'category',
      data: times,
      axisLabel: { color: '#64748b', fontSize: 10 },
      axisLine: { lineStyle: { color: '#252d3a' } },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value',
      name: 'Hz',
      nameTextStyle: { color: '#64748b', fontSize: 10 },
      axisLabel: { color: '#64748b', fontSize: 10 },
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#252d3a', type: 'dashed' } },
    },
    series: [{
      name: seriesName,
      type: 'line' as const,
      smooth: true,
      showSymbol: false,
      lineStyle: { width: 2 },
      data: values,
    }],
  }
})
</script>

<template>
  <div class="bg-surface border border-surface-border rounded-lg p-4">
    <h3 class="text-sm font-medium text-text-secondary mb-3">Topic Frequency (Active Stream)</h3>
    <VChart
      v-if="topicsStore.statsHistory.length > 1"
      :option="chartOption"
      :autoresize="true"
      style="height: 240px;"
    />
    <div v-else class="flex items-center justify-center h-60 text-text-muted text-sm">
      Connect to a topic stream to view frequency data
    </div>
  </div>
</template>
