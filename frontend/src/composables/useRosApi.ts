import { useNodesStore } from '@/stores/nodes'
import { useTopicsStore } from '@/stores/topics'
import { useConnectionStore } from '@/stores/connection'
import { usePolling } from './usePolling'

export function useRosApi() {
  const nodesStore = useNodesStore()
  const topicsStore = useTopicsStore()
  const connectionStore = useConnectionStore()

  // Polling for nodes (default 2s interval)
  const nodesPolling = usePolling(
    () => nodesStore.loadNodes(),
    2000,
    { immediate: false }
  )

  // Polling for topics (default 2s interval)
  const topicsPolling = usePolling(
    () => topicsStore.loadTopics(),
    2000,
    { immediate: false }
  )

  // Health check polling (5s interval)
  const healthPolling = usePolling(
    async () => { await connectionStore.checkBackendHealth() },
    5000,
    { immediate: false }
  )

  function startAllPolling() {
    healthPolling.start()
    nodesPolling.start()
    topicsPolling.start()
  }

  function stopAllPolling() {
    healthPolling.stop()
    nodesPolling.stop()
    topicsPolling.stop()
  }

  return {
    nodesStore,
    topicsStore,
    connectionStore,
    nodesPolling,
    topicsPolling,
    healthPolling,
    startAllPolling,
    stopAllPolling
  }
}
