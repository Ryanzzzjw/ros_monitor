<script setup lang="ts">
import { computed } from 'vue'
import { Server, Radio } from 'lucide-vue-next'
import { useNodesStore } from '@/stores/nodes'
import { useTopicsStore } from '@/stores/topics'

const nodesStore = useNodesStore()
const topicsStore = useTopicsStore()

interface ActivityItem {
  type: 'node' | 'topic'
  name: string
  detail: string
}

const activities = computed<ActivityItem[]>(() => {
  const items: ActivityItem[] = []

  for (const node of nodesStore.nodes.slice(0, 8)) {
    items.push({
      type: 'node',
      name: node.name,
      detail: node.namespace,
    })
  }

  for (const topic of topicsStore.topics.slice(0, 8)) {
    items.push({
      type: 'topic',
      name: topic.name,
      detail: topic.types[0] || '',
    })
  }

  return items.slice(0, 12)
})
</script>

<template>
  <div class="bg-surface border border-surface-border rounded-lg p-4">
    <h3 class="text-sm font-medium text-text-secondary mb-3">Active Resources</h3>

    <div v-if="activities.length === 0" class="text-text-muted text-sm py-8 text-center">
      No ROS nodes or topics detected
    </div>

    <div v-else class="space-y-1">
      <div
        v-for="(item, idx) in activities"
        :key="`${item.type}-${item.name}-${idx}`"
        class="flex items-center gap-2.5 px-2 py-1.5 rounded hover:bg-surface-hover transition-colors"
      >
        <component
          :is="item.type === 'node' ? Server : Radio"
          :size="14"
          :class="item.type === 'node' ? 'text-primary' : 'text-live'"
        />
        <span class="text-sm text-text-primary truncate font-mono">{{ item.name }}</span>
        <span class="text-xs text-text-muted truncate ml-auto">{{ item.detail }}</span>
      </div>
    </div>
  </div>
</template>
