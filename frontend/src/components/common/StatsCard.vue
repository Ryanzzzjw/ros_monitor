<script setup lang="ts">
import type { Component } from 'vue'

defineProps<{
  icon: Component
  value: string | number
  label: string
  trend?: 'up' | 'down' | 'neutral'
  color?: 'primary' | 'live' | 'danger' | 'warning'
}>()
</script>

<template>
  <div class="bg-surface border border-surface-border rounded-lg p-4 flex items-start gap-3">
    <div
      class="shrink-0 w-10 h-10 rounded-lg flex items-center justify-center"
      :class="{
        'bg-primary/10 text-primary': color === 'primary' || !color,
        'bg-live-dim text-live': color === 'live',
        'bg-danger-dim text-danger': color === 'danger',
        'bg-warning/10 text-warning': color === 'warning',
      }"
    >
      <component :is="icon" :size="20" />
    </div>
    <div class="min-w-0">
      <div class="text-2xl font-semibold text-text-primary tabular-nums">
        {{ value }}
      </div>
      <div class="text-xs text-text-muted mt-0.5">
        {{ label }}
      </div>
    </div>
  </div>
</template>
