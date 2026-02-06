import axios from 'axios'
import type {
  NodeListResponse,
  NodeDetail,
  TopicListResponse,
  TopicDetail,
  TopicStats
} from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// --- Nodes API ---

export async function fetchNodes(): Promise<NodeListResponse> {
  const response = await api.get<NodeListResponse>('/nodes')
  return response.data
}

export async function fetchNodeDetail(namespace: string, nodeName: string): Promise<NodeDetail> {
  // Remove leading slash from namespace for URL
  const ns = namespace.startsWith('/') ? namespace.slice(1) : namespace
  const response = await api.get<NodeDetail>(`/nodes/${ns}/${nodeName}`)
  return response.data
}

// --- Topics API ---

export async function fetchTopics(): Promise<TopicListResponse> {
  const response = await api.get<TopicListResponse>('/topics')
  return response.data
}

export async function fetchTopicInfo(topicName: string): Promise<TopicDetail> {
  // Remove leading slash for URL
  const name = topicName.startsWith('/') ? topicName.slice(1) : topicName
  const response = await api.get<TopicDetail>(`/topics/${name}/info`)
  return response.data
}

export async function fetchTopicStats(topicName: string): Promise<TopicStats> {
  const name = topicName.startsWith('/') ? topicName.slice(1) : topicName
  const response = await api.get<TopicStats>(`/topics/${name}/stats`)
  return response.data
}

// --- Health API ---

export async function checkHealth(): Promise<boolean> {
  try {
    const response = await api.get<{ status: string }>('/health')
    return response.data.status === 'ok'
  } catch {
    return false
  }
}

export default api
