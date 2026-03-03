<script setup lang="ts">
import { computed, ref, onUnmounted } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useTopicsStore } from '@/stores/topics'
import { fetchTopicStats } from '@/api/client'

use([LineChart, GridComponent, TooltipComponent, LegendComponent, CanvasRenderer])

const topicsStore = useTopicsStore()

const MAX_POINTS = 30
const topN = 5

interface FreqDataPoint {
  time: string
  values: Record<string, number>
}

const history = ref<FreqDataPoint[]>([])
const trackedTopics = ref<string[]>([])

// Poll top-N topics for stats every 2s
let pollTimer: ReturnType<typeof setInterval> | null = null

async function pollStats() {
  const topics = topicsStore.topics.slice(0, topN)
  const now = new Date().toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })

  const values: Record<string, number> = {}
  const names: string[] = []

  for (const t of topics) {
    try {
      const stats = await fetchTopicStats(t.name)
      values[t.name] = Math.round(stats.rate_hz * 10) / 10
      names.push(t.name)
    } catch {
      values[t.name] = 0
      names.push(t.name)
    }
  }

  trackedTopics.value = names
  history.value.push({ time: now, values })
  if (history.value.length > MAX_POINTS) {
    history.value.shift()
  }
}

pollTimer = setInterval(pollStats, 2000)
pollStats()

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})

const chartOption = computed(() => {
  const times = history.value.map(p => p.time)
  const series = trackedTopics.value.map(name => ({
    name: name.length > 20 ? '...' + name.slice(-18) : name,
    type: 'line' as const,
    smooth: true,
    showSymbol: false,
    lineStyle: { width: 2 },
    data: history.value.map(p => p.values[name] ?? 0),
  }))

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
      show: trackedTopics.value.length > 0,
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
    series,
  }
})
</script>

<template>
  <div class="bg-surface border border-surface-border rounded-lg p-4">
    <h3 class="text-sm font-medium text-text-secondary mb-3">Topic Frequency (Top {{ topN }})</h3>
    <VChart
      v-if="trackedTopics.length > 0"
      :option="chartOption"
      :autoresize="true"
      style="height: 240px;"
    />
    <div v-else class="flex items-center justify-center h-60 text-text-muted text-sm">
      No topic data available
    </div>
  </div>
</template>
