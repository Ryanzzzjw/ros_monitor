/** Topic endpoint (publisher/subscriber) */
export interface TopicEndpoint {
  topic: string
  types: string[]
}

/** Service/client endpoint */
export interface ServiceEndpoint {
  name: string
  types: string[]
}

/** Brief node info */
export interface NodeSummary {
  name: string
  namespace: string
  full_name: string
}

/** Full node detail */
export interface NodeDetail {
  name: string
  namespace: string
  full_name: string
  publishers: TopicEndpoint[]
  subscribers: TopicEndpoint[]
  services: ServiceEndpoint[]
  clients: ServiceEndpoint[]
}

/** Node list response */
export interface NodeListResponse {
  nodes: NodeSummary[]
  count: number
}

/** Brief topic info */
export interface TopicSummary {
  name: string
  types: string[]
}

/** Topic list response */
export interface TopicListResponse {
  topics: TopicSummary[]
  count: number
}

/** Topic endpoint info (node that publishes/subscribes) */
export interface TopicEndpointInfo {
  node_name: string
  node_namespace: string
}

/** Full topic detail */
export interface TopicDetail {
  name: string
  types: string[]
  publisher_count: number
  subscriber_count: number
  publishers: TopicEndpointInfo[]
  subscribers: TopicEndpointInfo[]
}

/** Topic stats */
export interface TopicStats {
  topic: string
  msg_count: number
  rate_hz: number
  subscriber_count: number
}

/** WebSocket envelope types */
export type WSEnvelopeType = 'data' | 'stats' | 'error' | 'ack'

/** Base WebSocket envelope */
export interface WSEnvelope<T = unknown> {
  type: WSEnvelopeType
  topic: string
  payload: T
  timestamp: number
  seq?: number
}

/** Data envelope payload */
export interface WSDataPayload {
  [key: string]: unknown
}

/** Stats envelope payload */
export interface WSStatsPayload {
  topic: string
  msg_count: number
  rate_hz: number
  subscriber_count: number
}

/** Error envelope payload */
export interface WSErrorPayload {
  message: string
}

/** Ack envelope payload */
export interface WSAckPayload {
  action: string
}

/** WebSocket connection state */
export type ConnectionState = 'disconnected' | 'connecting' | 'connected' | 'error'

/** Stream message for virtual scroll display */
export interface StreamMessage {
  id: number
  seq: number
  timestamp: number
  data: WSDataPayload
  /** Pre-serialized JSON string for display */
  preview: string
}

/** Frequency data point for charts */
export interface FrequencyDataPoint {
  time: number
  hz: number
}
