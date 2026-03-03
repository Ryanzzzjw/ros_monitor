import { ref, onUnmounted, type Ref } from 'vue'
import type { ConnectionState, WSEnvelope, WSDataPayload, WSStatsPayload } from '@/types'
import { useConnectionStore } from '@/stores/connection'
import { useTopicsStore } from '@/stores/topics'

export interface UseWebSocketOptions {
  onMessage?: (envelope: WSEnvelope<WSDataPayload>) => void
  onStats?: (stats: WSStatsPayload) => void
  onError?: (error: string) => void
  onStateChange?: (state: ConnectionState) => void
  /** Enable auto-reconnect with exponential backoff (default: true) */
  autoReconnect?: boolean
  /** Max reconnect attempts before giving up (default: 10) */
  maxReconnectAttempts?: number
}

const BASE_RECONNECT_DELAY = 1000
const MAX_RECONNECT_DELAY = 30000

export function useWebSocket(topicName: Ref<string>, messageType: Ref<string>, options: UseWebSocketOptions = {}) {
  const { autoReconnect = true, maxReconnectAttempts = 10 } = options

  const connectionStore = useConnectionStore()
  const topicsStore = useTopicsStore()

  const ws = ref<WebSocket | null>(null)
  const state = ref<ConnectionState>('disconnected')
  const subscribed = ref(false)

  // Reconnect state
  const reconnectAttempt = ref(0)
  const reconnectCountdown = ref(0)
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let countdownTimer: ReturnType<typeof setInterval> | null = null
  let intentionalClose = false

  // Frequency tracking (sliding window)
  const frequencyHz = ref(0)
  const messageTimestamps: number[] = []
  const FREQ_WINDOW_MS = 5000

  function getWsUrl(topic: string): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const cleanTopic = topic.startsWith('/') ? topic.slice(1) : topic
    return `${protocol}//${host}/ws/topics/${cleanTopic}`
  }

  function updateFrequency() {
    const now = Date.now()
    messageTimestamps.push(now)
    // Remove timestamps outside window
    while (messageTimestamps.length > 0 && messageTimestamps[0] < now - FREQ_WINDOW_MS) {
      messageTimestamps.shift()
    }
    frequencyHz.value = Math.round((messageTimestamps.length / (FREQ_WINDOW_MS / 1000)) * 10) / 10
  }

  function connect() {
    if (ws.value?.readyState === WebSocket.OPEN) {
      return
    }

    intentionalClose = false
    clearReconnectTimers()

    const url = getWsUrl(topicName.value)
    state.value = 'connecting'
    connectionStore.setWsState('connecting')
    options.onStateChange?.('connecting')

    ws.value = new WebSocket(url)

    ws.value.onopen = () => {
      state.value = 'connected'
      reconnectAttempt.value = 0
      reconnectCountdown.value = 0
      connectionStore.setWsState('connected')
      options.onStateChange?.('connected')
      subscribe()
    }

    ws.value.onmessage = (event) => {
      try {
        const envelope = JSON.parse(event.data) as WSEnvelope<unknown>
        handleEnvelope(envelope)
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e)
      }
    }

    ws.value.onerror = () => {
      state.value = 'error'
      connectionStore.setWsState('error')
      connectionStore.setError('WebSocket connection error')
      options.onStateChange?.('error')
      options.onError?.('WebSocket connection error')
    }

    ws.value.onclose = () => {
      state.value = 'disconnected'
      subscribed.value = false
      connectionStore.setWsState('disconnected')
      options.onStateChange?.('disconnected')

      // Auto-reconnect if enabled and not intentionally closed
      if (autoReconnect && !intentionalClose && reconnectAttempt.value < maxReconnectAttempts) {
        scheduleReconnect()
      }
    }
  }

  function scheduleReconnect() {
    const delay = Math.min(
      BASE_RECONNECT_DELAY * Math.pow(2, reconnectAttempt.value),
      MAX_RECONNECT_DELAY
    )
    reconnectAttempt.value++
    reconnectCountdown.value = Math.ceil(delay / 1000)

    // Countdown display
    countdownTimer = setInterval(() => {
      reconnectCountdown.value = Math.max(0, reconnectCountdown.value - 1)
    }, 1000)

    reconnectTimer = setTimeout(() => {
      clearReconnectTimers()
      connect()
    }, delay)
  }

  function clearReconnectTimers() {
    if (reconnectTimer) {
      clearTimeout(reconnectTimer)
      reconnectTimer = null
    }
    if (countdownTimer) {
      clearInterval(countdownTimer)
      countdownTimer = null
    }
    reconnectCountdown.value = 0
  }

  function handleEnvelope(envelope: WSEnvelope<unknown>) {
    switch (envelope.type) {
      case 'data':
        updateFrequency()
        topicsStore.handleMessage(envelope as WSEnvelope<WSDataPayload>)
        options.onMessage?.(envelope as WSEnvelope<WSDataPayload>)
        break
      case 'stats':
        topicsStore.handleStats(envelope.payload as WSStatsPayload)
        options.onStats?.(envelope.payload as WSStatsPayload)
        break
      case 'error': {
        const errorPayload = envelope.payload as { message: string }
        connectionStore.setError(errorPayload.message)
        options.onError?.(errorPayload.message)
        break
      }
      case 'ack': {
        const ackPayload = envelope.payload as { action: string }
        if (ackPayload.action === 'subscribed') {
          subscribed.value = true
        } else if (ackPayload.action === 'unsubscribed') {
          subscribed.value = false
        }
        break
      }
    }
  }

  function subscribe() {
    if (ws.value?.readyState !== WebSocket.OPEN) {
      return
    }
    ws.value.send(JSON.stringify({
      action: 'subscribe',
      type: messageType.value
    }))
  }

  function unsubscribe() {
    if (ws.value?.readyState !== WebSocket.OPEN) {
      return
    }
    ws.value.send(JSON.stringify({
      action: 'unsubscribe'
    }))
  }

  function disconnect() {
    intentionalClose = true
    clearReconnectTimers()
    reconnectAttempt.value = 0

    if (ws.value) {
      if (subscribed.value) {
        unsubscribe()
      }
      ws.value.close()
      ws.value = null
    }
    state.value = 'disconnected'
    subscribed.value = false
    messageTimestamps.length = 0
    frequencyHz.value = 0
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    state,
    subscribed,
    frequencyHz,
    reconnectAttempt,
    reconnectCountdown,
    connect,
    disconnect,
    subscribe,
    unsubscribe,
  }
}
