<script setup lang="ts">
import { NTag } from 'naive-ui'
import { Search } from 'lucide-vue-next'
import { useConnectionStore } from '@/stores/connection'
import ConnectionIndicator from './ConnectionIndicator.vue'

const connectionStore = useConnectionStore()

const emit = defineEmits<{
  openSearch: []
}>()
</script>

<template>
  <header class="flex items-center justify-between h-14 px-6 border-b border-surface-border bg-surface shrink-0">
    <!-- Left: page info -->
    <div class="flex items-center gap-3">
      <slot name="title" />
    </div>

    <!-- Right: search + domain ID + connection -->
    <div class="flex items-center gap-4">
      <!-- Search trigger -->
      <button
        class="flex items-center gap-2 px-3 py-1.5 text-sm text-text-muted bg-bg border border-surface-border rounded-md hover:border-primary/50 transition-colors cursor-pointer"
        @click="emit('openSearch')"
      >
        <Search :size="14" />
        <span class="hidden sm:inline">Search</span>
        <kbd class="hidden sm:inline-block ml-2 px-1.5 py-0.5 text-[10px] font-mono bg-surface border border-surface-border rounded">
          Ctrl+K
        </kbd>
      </button>

      <!-- Domain ID badge -->
      <NTag
        v-if="connectionStore.domainId !== null"
        type="info"
        size="small"
        round
      >
        Domain {{ connectionStore.domainId }}
      </NTag>

      <!-- Connection indicator -->
      <ConnectionIndicator
        :state="connectionStore.backendConnected ? 'connected' : 'disconnected'"
        label
        size="md"
      />
    </div>
  </header>
</template>
