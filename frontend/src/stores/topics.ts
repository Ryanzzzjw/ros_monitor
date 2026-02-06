import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { TopicSummary, TopicDetail, WSEnvelope, WSDataPayload, WSStatsPayload } from '@/types'
import { fetchTopics, fetchTopicInfo } from '@/api/client'

export const useTopicsStore = defineStore('topics', () => {
  const topics = ref<TopicSummary[]>([])
  const selectedTopic = ref<TopicDetail | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Real-time message data for subscribed topic
  const latestMessage = ref<WSDataPayload | null>(null)
  const latestStats = ref<WSStatsPayload | null>(null)
  const messageHistory = ref<WSEnvelope<WSDataPayload>[]>([])
  const maxHistorySize = 100

  const topicCount = computed(() => topics.value.length)

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
    messageHistory.value.push(envelope)
    if (messageHistory.value.length > maxHistorySize) {
      messageHistory.value.shift()
    }
  }

  function handleStats(stats: WSStatsPayload) {
    latestStats.value = stats
  }

  function clearMessages() {
    latestMessage.value = null
    latestStats.value = null
    messageHistory.value = []
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
    messageHistory,
    loadTopics,
    loadTopicDetail,
    handleMessage,
    handleStats,
    clearMessages,
    clearSelection
  }
})
