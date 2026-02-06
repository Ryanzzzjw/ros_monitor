import { ref, onUnmounted, type Ref } from 'vue'
import type { ConnectionState, WSEnvelope, WSDataPayload, WSStatsPayload } from '@/types'
import { useConnectionStore } from '@/stores/connection'
import { useTopicsStore } from '@/stores/topics'

export interface UseWebSocketOptions {
  onMessage?: (envelope: WSEnvelope<WSDataPayload>) => void
  onStats?: (stats: WSStatsPayload) => void
  onError?: (error: string) => void
  onStateChange?: (state: ConnectionState) => void
}

export function useWebSocket(topicName: Ref<string>, messageType: Ref<string>, options: UseWebSocketOptions = {}) {
  const connectionStore = useConnectionStore()
  const topicsStore = useTopicsStore()

  const ws = ref<WebSocket | null>(null)
  const state = ref<ConnectionState>('disconnected')
  const subscribed = ref(false)

  function getWsUrl(topic: string): string {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const cleanTopic = topic.startsWith('/') ? topic.slice(1) : topic
    return `${protocol}//${host}/ws/topics/${cleanTopic}`
  }

  function connect() {
    if (ws.value?.readyState === WebSocket.OPEN) {
      return
    }

    const url = getWsUrl(topicName.value)
    state.value = 'connecting'
    connectionStore.setWsState('connecting')
    options.onStateChange?.('connecting')

    ws.value = new WebSocket(url)

    ws.value.onopen = () => {
      state.value = 'connected'
      connectionStore.setWsState('connected')
      options.onStateChange?.('connected')
      // Auto-subscribe on connect
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
    }
  }

  function handleEnvelope(envelope: WSEnvelope<unknown>) {
    switch (envelope.type) {
      case 'data':
        topicsStore.handleMessage(envelope as WSEnvelope<WSDataPayload>)
        options.onMessage?.(envelope as WSEnvelope<WSDataPayload>)
        break
      case 'stats':
        topicsStore.handleStats(envelope.payload as WSStatsPayload)
        options.onStats?.(envelope.payload as WSStatsPayload)
        break
      case 'error':
        const errorPayload = envelope.payload as { message: string }
        connectionStore.setError(errorPayload.message)
        options.onError?.(errorPayload.message)
        break
      case 'ack':
        const ackPayload = envelope.payload as { action: string }
        if (ackPayload.action === 'subscribed') {
          subscribed.value = true
        } else if (ackPayload.action === 'unsubscribed') {
          subscribed.value = false
        }
        break
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
    if (ws.value) {
      if (subscribed.value) {
        unsubscribe()
      }
      ws.value.close()
      ws.value = null
    }
    state.value = 'disconnected'
    subscribed.value = false
  }

  onUnmounted(() => {
    disconnect()
  })

  return {
    state,
    subscribed,
    connect,
    disconnect,
    subscribe,
    unsubscribe
  }
}
