/**
 * Web Worker for off-main-thread JSON parsing and field filtering.
 * Handles high-frequency topic messages without blocking UI.
 */

export interface WorkerRequest {
  type: 'parse'
  id: number
  raw: string
  filter?: string
}

export interface WorkerResponse {
  type: 'parsed'
  id: number
  data: unknown
  preview: string
  filtered?: unknown
}

const ctx = self as unknown as Worker

ctx.addEventListener('message', (e: MessageEvent<WorkerRequest>) => {
  const { type, id, raw, filter } = e.data

  if (type === 'parse') {
    try {
      const data = JSON.parse(raw)
      let preview: string
      let filtered: unknown = undefined

      if (filter) {
        filtered = extractByPath(data, filter)
        preview = JSON.stringify(filtered, null, 2)
      } else {
        preview = JSON.stringify(data, null, 2)
      }

      const response: WorkerResponse = { type: 'parsed', id, data, preview, filtered }
      ctx.postMessage(response)
    } catch {
      const response: WorkerResponse = {
        type: 'parsed',
        id,
        data: raw,
        preview: String(raw),
      }
      ctx.postMessage(response)
    }
  }
})

/**
 * Extract a value by dot-separated path (e.g., "position.x").
 * Supports array indexing with numeric segments.
 */
function extractByPath(obj: unknown, path: string): unknown {
  const parts = path.split('.').filter(Boolean)
  let current: unknown = obj

  for (const part of parts) {
    if (current === null || current === undefined) return undefined
    if (typeof current === 'object') {
      current = (current as Record<string, unknown>)[part]
    } else {
      return undefined
    }
  }

  return current
}
