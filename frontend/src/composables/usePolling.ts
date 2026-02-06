import { ref, onUnmounted, watch, type Ref } from 'vue'

export interface UsePollingOptions {
  immediate?: boolean
  enabled?: Ref<boolean>
}

export function usePolling(
  callback: () => Promise<void>,
  intervalMs: number,
  options: UsePollingOptions = {}
) {
  const { immediate = true, enabled } = options

  const isPolling = ref(false)
  let intervalId: ReturnType<typeof setInterval> | null = null

  async function poll() {
    try {
      await callback()
    } catch (e) {
      console.error('Polling error:', e)
    }
  }

  function start() {
    if (intervalId !== null) {
      return
    }
    isPolling.value = true
    if (immediate) {
      poll()
    }
    intervalId = setInterval(poll, intervalMs)
  }

  function stop() {
    if (intervalId !== null) {
      clearInterval(intervalId)
      intervalId = null
    }
    isPolling.value = false
  }

  // Watch enabled ref if provided
  if (enabled) {
    watch(enabled, (newVal) => {
      if (newVal) {
        start()
      } else {
        stop()
      }
    }, { immediate: true })
  }

  onUnmounted(() => {
    stop()
  })

  return {
    isPolling,
    start,
    stop,
    poll
  }
}
