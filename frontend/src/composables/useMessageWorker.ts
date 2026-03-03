import { ref, onUnmounted } from 'vue'
import type { WorkerRequest, WorkerResponse } from '@/workers/message-parser.worker'

export function useMessageWorker() {
  const worker = ref<Worker | null>(null)
  let idCounter = 0
  const pendingCallbacks = new Map<number, (resp: WorkerResponse) => void>()

  function init() {
    if (worker.value) return
    worker.value = new Worker(
      new URL('@/workers/message-parser.worker.ts', import.meta.url),
      { type: 'module' }
    )
    worker.value.addEventListener('message', (e: MessageEvent<WorkerResponse>) => {
      const cb = pendingCallbacks.get(e.data.id)
      if (cb) {
        cb(e.data)
        pendingCallbacks.delete(e.data.id)
      }
    })
  }

  function parse(raw: string, filter?: string): Promise<WorkerResponse> {
    init()
    return new Promise((resolve) => {
      const id = ++idCounter
      pendingCallbacks.set(id, resolve)
      const msg: WorkerRequest = { type: 'parse', id, raw, filter }
      worker.value!.postMessage(msg)
    })
  }

  function terminate() {
    worker.value?.terminate()
    worker.value = null
    pendingCallbacks.clear()
  }

  onUnmounted(terminate)

  return { parse, terminate }
}
