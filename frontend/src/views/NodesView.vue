<script setup lang="ts">
import { computed, watch } from 'vue'
import type { NodeSummary } from '@/types'
import { useNodesStore } from '@/stores/nodes'
import { useUrlState } from '@/composables/useUrlState'
import NodeList from '@/components/nodes/NodeList.vue'
import NodeDetail from '@/components/nodes/NodeDetail.vue'

const nodesStore = useNodesStore()
const urlNodeName = useUrlState('node')

const selectedName = computed(() => nodesStore.selectedNode?.full_name)

function handleSelect(node: NodeSummary) {
  nodesStore.loadNodeDetail(node.namespace, node.name)
  urlNodeName.value = node.full_name
}

// Load node from URL on mount
watch(urlNodeName, (name) => {
  if (name && !nodesStore.selectedNode) {
    const match = nodesStore.nodes.find(n => n.full_name === name)
    if (match) {
      nodesStore.loadNodeDetail(match.namespace, match.name)
    }
  }
}, { immediate: true })
</script>

<template>
  <div class="flex h-full -m-6">
    <!-- Master: node list (40%) -->
    <div class="w-2/5 min-w-[280px] border-r border-surface-border bg-surface">
      <NodeList :selected-name="selectedName" @select="handleSelect" />
    </div>

    <!-- Detail panel (60%) -->
    <div class="flex-1 min-w-0">
      <Transition name="fade">
        <NodeDetail :key="selectedName ?? 'empty'" />
      </Transition>
    </div>
  </div>
</template>
