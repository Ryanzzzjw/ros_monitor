<script setup lang="ts">
import {
  NCard, NDataTable, NDrawer, NDrawerContent, NDescriptions, NDescriptionsItem,
  NTag, NSpin, NEmpty, NButton, NCode, NScrollbar, NStatistic, NGrid, NGridItem
} from 'naive-ui'
import { ref, onMounted, onUnmounted, h, computed } from 'vue'
import type { DataTableColumns } from 'naive-ui'
import type { TopicSummary } from '@/types'
import { useTopicsStore } from '@/stores/topics'
import { usePolling } from '@/composables/usePolling'
import { useWebSocket } from '@/composables/useWebSocket'

const topicsStore = useTopicsStore()
const showDrawer = ref(false)
const selectedTopicName = ref('')
const selectedMessageType = ref('')

const columns: DataTableColumns<TopicSummary> = [
  {
    title: 'Topic Name',
    key: 'name',
    sorter: 'default'
  },
  {
    title: 'Message Types',
    key: 'types',
    render(row) {
      return row.types.map(t => h(NTag, { type: 'info', size: 'small', style: 'margin-right: 4px' }, { default: () => t }))
    }
  }
]

function handleRowClick(row: TopicSummary) {
  selectedTopicName.value = row.name
  selectedMessageType.value = row.types[0] || ''
  topicsStore.loadTopicDetail(row.name)
  showDrawer.value = true
}

function handleDrawerClose() {
  showDrawer.value = false
  wsDisconnect()
  topicsStore.clearSelection()
  selectedTopicName.value = ''
  selectedMessageType.value = ''
}

// WebSocket for real-time messages
const { state: wsState, subscribed, connect: wsConnect, disconnect: wsDisconnect } = useWebSocket(
  selectedTopicName,
  selectedMessageType
)

function toggleSubscription() {
  if (wsState.value === 'disconnected') {
    wsConnect()
  } else {
    wsDisconnect()
  }
}

const formattedMessage = computed(() => {
  if (!topicsStore.latestMessage) return null
  return JSON.stringify(topicsStore.latestMessage, null, 2)
})

const { start, stop } = usePolling(() => topicsStore.loadTopics(), 2000, { immediate: false })

onMounted(() => {
  topicsStore.loadTopics()
  start()
})

onUnmounted(() => {
  stop()
  wsDisconnect()
})
</script>

<template>
  <div>
    <h1 style="margin-bottom: 24px;">ROS Topics</h1>

    <NCard>
      <NSpin :show="topicsStore.loading && topicsStore.topics.length === 0">
        <NEmpty v-if="topicsStore.topics.length === 0 && !topicsStore.loading" description="No topics found" />
        <NDataTable
          v-else
          :columns="columns"
          :data="topicsStore.topics"
          :row-props="(row: TopicSummary) => ({ style: 'cursor: pointer', onClick: () => handleRowClick(row) })"
          :pagination="{ pageSize: 20 }"
        />
      </NSpin>
    </NCard>

    <NDrawer v-model:show="showDrawer" :width="600" @after-leave="handleDrawerClose">
      <NDrawerContent :title="topicsStore.selectedTopic?.name || 'Topic Detail'">
        <NSpin :show="topicsStore.loading">
          <template v-if="topicsStore.selectedTopic">
            <NDescriptions label-placement="left" :column="1" style="margin-bottom: 24px;">
              <NDescriptionsItem label="Name">{{ topicsStore.selectedTopic.name }}</NDescriptionsItem>
              <NDescriptionsItem label="Types">
                <NTag v-for="t in topicsStore.selectedTopic.types" :key="t" type="info" size="small" style="margin-right: 4px;">
                  {{ t }}
                </NTag>
              </NDescriptionsItem>
              <NDescriptionsItem label="Publishers">{{ topicsStore.selectedTopic.publisher_count }}</NDescriptionsItem>
              <NDescriptionsItem label="Subscribers">{{ topicsStore.selectedTopic.subscriber_count }}</NDescriptionsItem>
            </NDescriptions>

            <!-- Real-time subscription -->
            <NCard title="Real-time Messages" style="margin-bottom: 16px;">
              <template #header-extra>
                <NButton
                  :type="wsState === 'connected' ? 'error' : 'primary'"
                  size="small"
                  @click="toggleSubscription"
                  :loading="wsState === 'connecting'"
                >
                  {{ wsState === 'connected' ? 'Disconnect' : 'Connect' }}
                </NButton>
              </template>

              <NGrid :cols="3" :x-gap="12" style="margin-bottom: 16px;">
                <NGridItem>
                  <NStatistic label="Status">
                    <NTag :type="wsState === 'connected' ? 'success' : wsState === 'error' ? 'error' : 'default'" size="small">
                      {{ wsState }}
                    </NTag>
                  </NStatistic>
                </NGridItem>
                <NGridItem>
                  <NStatistic label="Messages" :value="topicsStore.latestStats?.msg_count || 0" />
                </NGridItem>
                <NGridItem>
                  <NStatistic label="Rate (Hz)" :value="topicsStore.latestStats?.rate_hz?.toFixed(1) || '0.0'" />
                </NGridItem>
              </NGrid>

              <div v-if="formattedMessage">
                <h4 style="margin-bottom: 8px;">Latest Message:</h4>
                <NScrollbar style="max-height: 300px;">
                  <NCode :code="formattedMessage" language="json" />
                </NScrollbar>
              </div>
              <NEmpty v-else-if="wsState === 'connected'" description="Waiting for messages..." />
              <NEmpty v-else description="Click Connect to receive messages" />
            </NCard>

            <!-- Publishers list -->
            <h4>Publishers</h4>
            <div v-if="topicsStore.selectedTopic.publishers.length === 0" style="color: #999; margin-bottom: 16px;">None</div>
            <div v-else style="margin-bottom: 16px;">
              <div v-for="pub in topicsStore.selectedTopic.publishers" :key="`${pub.node_namespace}/${pub.node_name}`" style="margin-bottom: 4px;">
                <NTag type="success" size="small">{{ pub.node_namespace }}/{{ pub.node_name }}</NTag>
              </div>
            </div>

            <!-- Subscribers list -->
            <h4>Subscribers</h4>
            <div v-if="topicsStore.selectedTopic.subscribers.length === 0" style="color: #999;">None</div>
            <div v-else>
              <div v-for="sub in topicsStore.selectedTopic.subscribers" :key="`${sub.node_namespace}/${sub.node_name}`" style="margin-bottom: 4px;">
                <NTag type="warning" size="small">{{ sub.node_namespace }}/{{ sub.node_name }}</NTag>
              </div>
            </div>
          </template>
        </NSpin>
      </NDrawerContent>
    </NDrawer>
  </div>
</template>
