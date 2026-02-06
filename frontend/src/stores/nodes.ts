import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { NodeSummary, NodeDetail } from '@/types'
import { fetchNodes, fetchNodeDetail } from '@/api/client'

export const useNodesStore = defineStore('nodes', () => {
  const nodes = ref<NodeSummary[]>([])
  const selectedNode = ref<NodeDetail | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const nodeCount = computed(() => nodes.value.length)

  async function loadNodes() {
    loading.value = true
    error.value = null
    try {
      const response = await fetchNodes()
      nodes.value = response.nodes
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load nodes'
    } finally {
      loading.value = false
    }
  }

  async function loadNodeDetail(namespace: string, nodeName: string) {
    loading.value = true
    error.value = null
    try {
      selectedNode.value = await fetchNodeDetail(namespace, nodeName)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load node detail'
      selectedNode.value = null
    } finally {
      loading.value = false
    }
  }

  function clearSelection() {
    selectedNode.value = null
  }

  return {
    nodes,
    selectedNode,
    loading,
    error,
    nodeCount,
    loadNodes,
    loadNodeDetail,
    clearSelection
  }
})
