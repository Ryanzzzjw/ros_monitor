<script setup lang="ts">
import { NInput, NButton, NTag } from 'naive-ui'
import { Pause, Play, Trash2, Filter } from 'lucide-vue-next'
import { useTopicsStore } from '@/stores/topics'

const topicsStore = useTopicsStore()
</script>

<template>
  <div class="flex items-center gap-2 px-4 py-2 border-b border-surface-border bg-surface">
    <!-- Pause/Resume -->
    <NButton
      :type="topicsStore.paused ? 'primary' : 'default'"
      size="small"
      quaternary
      @click="topicsStore.togglePause()"
    >
      <template #icon>
        <component :is="topicsStore.paused ? Play : Pause" :size="14" />
      </template>
      {{ topicsStore.paused ? 'Resume' : 'Pause' }}
    </NButton>

    <!-- JSON filter -->
    <NInput
      v-model:value="topicsStore.jsonFilter"
      placeholder="Field filter (e.g. position.x)"
      size="small"
      class="max-w-[200px]"
      clearable
    >
      <template #prefix>
        <Filter :size="12" class="text-text-muted" />
      </template>
    </NInput>

    <!-- Clear -->
    <NButton size="small" quaternary @click="topicsStore.clearMessages()">
      <template #icon>
        <Trash2 :size="14" />
      </template>
    </NButton>

    <!-- Spacer -->
    <div class="flex-1" />

    <!-- Stats -->
    <NTag v-if="topicsStore.frequencyHz > 0" type="success" size="small" :bordered="false">
      {{ topicsStore.frequencyHz.toFixed(1) }} Hz
    </NTag>
    <NTag v-if="topicsStore.dropCount > 0" type="warning" size="small" :bordered="false">
      {{ topicsStore.dropCount }} dropped
    </NTag>
    <span class="text-xs text-text-muted">
      {{ topicsStore.displayedMessages.length }} msgs
    </span>
  </div>
</template>
