<script setup lang="ts">
import { computed } from 'vue'
import VChart from 'vue-echarts'
import { use } from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useTopicsStore } from '@/stores/topics'

use([LineChart, GridComponent, TooltipComponent, CanvasRenderer])

const topicsStore = useTopicsStore()

const chartOption = computed(() => {
  const data = topicsStore.statsHistory
  const times = data.map(p => {
    const d = new Date(p.time)
    return d.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })
  })
  const values = data.map(p => Math.round(p.hz * 10) / 10)

  return {
    backgroundColor: 'transparent',
    grid: { top: 8, right: 8, bottom: 20, left: 36 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: '#1c2333',
      borderColor: '#252d3a',
      textStyle: { color: '#e2e8f0', fontSize: 11 },
      formatter: (params: any) => {
        const p = Array.isArray(params) ? params[0] : params
        return `${p.axisValue}<br/><b>${p.value} Hz</b>`
      },
    },
    xAxis: {
      type: 'category',
      data: times,
      axisLabel: { color: '#64748b', fontSize: 9 },
      axisLine: { lineStyle: { color: '#252d3a' } },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#64748b', fontSize: 9 },
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#252d3a', type: 'dashed' } },
    },
    series: [{
      type: 'line',
      smooth: true,
      showSymbol: false,
      lineStyle: { width: 2, color: '#10b981' },
      areaStyle: {
        color: {
          type: 'linear',
          x: 0, y: 0, x2: 0, y2: 1,
          colorStops: [
            { offset: 0, color: 'rgba(16, 185, 129, 0.2)' },
            { offset: 1, color: 'rgba(16, 185, 129, 0)' },
          ],
        },
      },
      data: values,
    }],
  }
})
</script>

<template>
  <div class="bg-surface border-b border-surface-border px-4 py-3">
    <div class="flex items-center justify-between mb-2">
      <span class="text-xs text-text-muted">Frequency (last 60s)</span>
      <span v-if="topicsStore.frequencyHz > 0" class="text-xs font-mono text-live">
        {{ topicsStore.frequencyHz.toFixed(1) }} Hz
      </span>
    </div>
    <VChart
      v-if="topicsStore.statsHistory.length > 1"
      :option="chartOption"
      :autoresize="true"
      style="height: 100px;"
    />
    <div v-else class="flex items-center justify-center h-[100px] text-text-muted text-xs">
      Collecting data...
    </div>
  </div>
</template>
