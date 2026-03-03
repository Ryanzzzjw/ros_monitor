<script setup lang="ts">
import { computed } from 'vue'
import type { ConnectionState } from '@/types'

const props = withDefaults(defineProps<{
  state: ConnectionState
  size?: 'sm' | 'md'
  label?: boolean
}>(), {
  size: 'sm',
  label: false,
})

const dotClass = computed(() => {
  const base = props.size === 'md' ? 'w-2.5 h-2.5' : 'w-2 h-2'
  switch (props.state) {
    case 'connected':
      return `${base} bg-live rounded-full animate-pulse-live`
    case 'connecting':
      return `${base} bg-warning rounded-full animate-pulse`
    case 'error':
      return `${base} bg-danger rounded-full`
    default:
      return `${base} bg-text-muted rounded-full`
  }
})

const labelText = computed(() => {
  switch (props.state) {
    case 'connected': return 'Connected'
    case 'connecting': return 'Connecting'
    case 'error': return 'Error'
    default: return 'Disconnected'
  }
})
</script>

<template>
  <span class="inline-flex items-center gap-1.5">
    <span :class="dotClass" />
    <span
      v-if="label"
      class="text-xs"
      :class="{
        'text-live': state === 'connected',
        'text-warning': state === 'connecting',
        'text-danger': state === 'error',
        'text-text-muted': state === 'disconnected',
      }"
    >
      {{ labelText }}
    </span>
  </span>
</template>
