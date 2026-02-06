import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ConnectionState } from '@/types'
import { checkHealth } from '@/api/client'

export const useConnectionStore = defineStore('connection', () => {
  const backendConnected = ref(false)
  const wsState = ref<ConnectionState>('disconnected')
  const lastError = ref<string | null>(null)

  async function checkBackendHealth() {
    backendConnected.value = await checkHealth()
    return backendConnected.value
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
    checkBackendHealth,
    setWsState,
    setError
  }
})
