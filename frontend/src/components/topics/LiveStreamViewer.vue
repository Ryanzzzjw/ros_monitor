<script setup lang="ts">
import { ref, watch } from 'vue'
import { NCode, NScrollbar } from 'naive-ui'
import { useTopicsStore } from '@/stores/topics'
import type { StreamMessage } from '@/types'

const topicsStore = useTopicsStore()
const expandedId = ref<number | null>(null)

function toggleExpand(msg: StreamMessage) {
  expandedId.value = expandedId.value === msg.id ? null : msg.id
}

function formatTime(ts: number): string {
  const d = new Date(ts * 1000)
  const base = d.toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
  const ms = String(d.getMilliseconds()).padStart(3, '0')
  return `${base}.${ms}`
}

/** Apply JSON filter to preview */
function getPreview(msg: StreamMessage): string {
  const filter = topicsStore.jsonFilter.trim()
  if (!filter) return msg.preview

  try {
    const parts = filter.split('.').filter(Boolean)
    let current: unknown = msg.data
    for (const part of parts) {
      if (current === null || current === undefined) return 'undefined'
      if (typeof current === 'object') {
        current = (current as Record<string, unknown>)[part]
      } else {
        return 'undefined'
      }
    }
    return typeof current === 'object' ? JSON.stringify(current) : String(current)
  } catch {
    return msg.preview
  }
}

// Auto-scroll to bottom
const scrollRef = ref<InstanceType<typeof NScrollbar> | null>(null)
const shouldAutoScroll = ref(true)

watch(
  () => topicsStore.displayedMessages.length,
  () => {
    if (shouldAutoScroll.value && !topicsStore.paused) {
      requestAnimationFrame(() => {
        scrollRef.value?.scrollTo({ top: 999999, behavior: 'smooth' })
      })
    }
  }
)
</script>

<template>
  <div class="flex-1 min-h-0">
    <NScrollbar ref="scrollRef" class="h-full">
      <div v-if="topicsStore.displayedMessages.length === 0" class="flex items-center justify-center h-full text-text-muted text-sm py-12">
        Waiting for messages...
      </div>

      <div v-else class="divide-y divide-surface-border">
        <div
          v-for="msg in topicsStore.displayedMessages"
          :key="msg.id"
          class="px-3 py-1 hover:bg-surface-hover cursor-pointer transition-colors text-xs"
          @click="toggleExpand(msg)"
        >
          <!-- Compact row -->
          <div class="flex items-center gap-3 h-7">
            <span class="text-text-muted tabular-nums w-10 shrink-0">#{{ msg.seq }}</span>
            <span class="text-text-muted tabular-nums w-20 shrink-0 font-mono">{{ formatTime(msg.timestamp) }}</span>
            <span class="text-text-primary font-mono truncate flex-1">{{ getPreview(msg) }}</span>
          </div>

          <!-- Expanded detail -->
          <div v-if="expandedId === msg.id" class="mt-1 mb-2 ml-[7.5rem]">
            <NCode
              :code="JSON.stringify(msg.data, null, 2)"
              language="json"
              class="text-xs"
            />
          </div>
        </div>
      </div>
    </NScrollbar>
  </div>
</template>
