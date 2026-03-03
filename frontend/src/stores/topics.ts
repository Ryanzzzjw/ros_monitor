import { defineStore } from 'pinia'
import { ref, computed, shallowRef } from 'vue'
import type {
  TopicSummary, TopicDetail, WSEnvelope, WSDataPayload, WSStatsPayload,
  StreamMessage, FrequencyDataPoint,
} from '@/types'
import { fetchTopics, fetchTopicInfo } from '@/api/client'

export const useTopicsStore = defineStore('topics', () => {
  const topics = ref<TopicSummary[]>([])
  const selectedTopic = ref<TopicDetail | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Real-time message buffer (larger capacity for virtual scroll)
  const messageBuffer = shallowRef<StreamMessage[]>([])
  const maxBufferSize = 5000
  let seqCounter = 0

  // Latest data (backward compatible)
  const latestMessage = ref<WSDataPayload | null>(null)
  const latestStats = ref<WSStatsPayload | null>(null)

  // Pause / snapshot
  const paused = ref(false)
  const pauseSnapshot = shallowRef<StreamMessage[]>([])

  // JSON filter
  const jsonFilter = ref('')

  // Frequency history for chart (last 60 seconds)
  const statsHistory = ref<FrequencyDataPoint[]>([])
  const maxStatsHistory = 60

  // Derived stats
  const frequencyHz = ref(0)
  const dropCount = ref(0)

  const topicCount = computed(() => topics.value.length)

  /** Displayed messages: snapshot when paused, live buffer otherwise */
  const displayedMessages = computed(() =>
    paused.value ? pauseSnapshot.value : messageBuffer.value
  )

  async function loadTopics() {
    loading.value = true
    error.value = null
    try {
      const response = await fetchTopics()
      topics.value = response.topics
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load topics'
    } finally {
      loading.value = false
    }
  }

  async function loadTopicDetail(topicName: string) {
    loading.value = true
    error.value = null
    try {
      selectedTopic.value = await fetchTopicInfo(topicName)
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to load topic detail'
      selectedTopic.value = null
    } finally {
      loading.value = false
    }
  }

  function handleMessage(envelope: WSEnvelope<WSDataPayload>) {
    latestMessage.value = envelope.payload

    const msg: StreamMessage = {
      id: ++seqCounter,
      seq: envelope.seq ?? seqCounter,
      timestamp: envelope.timestamp,
      data: envelope.payload,
      preview: JSON.stringify(envelope.payload),
    }

    // Append to buffer (drop oldest if full)
    const buf = [...messageBuffer.value, msg]
    if (buf.length > maxBufferSize) {
      dropCount.value += buf.length - maxBufferSize
      messageBuffer.value = buf.slice(buf.length - maxBufferSize)
    } else {
      messageBuffer.value = buf
    }
  }

  function handleStats(stats: WSStatsPayload) {
    latestStats.value = stats
    frequencyHz.value = stats.rate_hz

    statsHistory.value.push({
      time: Date.now(),
      hz: stats.rate_hz,
    })
    if (statsHistory.value.length > maxStatsHistory) {
      statsHistory.value.shift()
    }
  }

  function togglePause() {
    if (!paused.value) {
      // Take snapshot
      pauseSnapshot.value = [...messageBuffer.value]
      paused.value = true
    } else {
      // Resume — discard snapshot
      pauseSnapshot.value = []
      paused.value = false
    }
  }

  function clearMessages() {
    latestMessage.value = null
    latestStats.value = null
    messageBuffer.value = []
    pauseSnapshot.value = []
    statsHistory.value = []
    paused.value = false
    jsonFilter.value = ''
    dropCount.value = 0
    frequencyHz.value = 0
    seqCounter = 0
  }

  function clearSelection() {
    selectedTopic.value = null
    clearMessages()
  }

  return {
    topics,
    selectedTopic,
    loading,
    error,
    topicCount,
    latestMessage,
    latestStats,
    messageBuffer,
    displayedMessages,
    paused,
    jsonFilter,
    statsHistory,
    frequencyHz,
    dropCount,
    loadTopics,
    loadTopicDetail,
    handleMessage,
    handleStats,
    togglePause,
    clearMessages,
    clearSelection,
  }
})
