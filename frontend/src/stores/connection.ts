import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ConnectionState } from '@/types'
import { checkHealth, fetchConfig } from '@/api/client'

export const useConnectionStore = defineStore('connection', () => {
  const backendConnected = ref(false)
  const wsState = ref<ConnectionState>('disconnected')
  const lastError = ref<string | null>(null)
  const domainId = ref<number | null>(null)
  const nodeName = ref<string>('')

  async function checkBackendHealth() {
    backendConnected.value = await checkHealth()
    return backendConnected.value
  }

  async function loadConfig() {
    try {
      const config = await fetchConfig()
      domainId.value = config.domain_id
      nodeName.value = config.node_name
    } catch {
      // Config endpoint unavailable — non-critical
    }
  }

  function setWsState(state: ConnectionState) {
    wsState.value = state
  }

  function setError(error: string | null) {
    lastError.value = error
  }

  return {
    backendConnected,
    wsState,
    lastError,
    domainId,
    nodeName,
    checkBackendHealth,
    loadConfig,
    setWsState,
    setError,
  }
})
