<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { NTag, NButton, NSpin } from 'naive-ui'
import { Radio, Wifi, WifiOff } from 'lucide-vue-next'
import { useTopicsStore } from '@/stores/topics'
import { useWebSocket } from '@/composables/useWebSocket'
import TopicFrequencyChart from './TopicFrequencyChart.vue'
import StreamControls from './StreamControls.vue'
import LiveStreamViewer from './LiveStreamViewer.vue'

const topicsStore = useTopicsStore()

const selectedTopicName = ref('')
const selectedMessageType = ref('')

const { state: wsState, connect: wsConnect, disconnect: wsDisconnect } = useWebSocket(
  selectedTopicName,
  selectedMessageType
)

function setTopic(name: string, type: string) {
  // Disconnect previous if any
  if (wsState.value !== 'disconnected') {
    wsDisconnect()
    topicsStore.clearMessages()
  }
  selectedTopicName.value = name
  selectedMessageType.value = type
}

function toggleConnection() {
  if (wsState.value === 'disconnected') {
    wsConnect()
  } else {
    wsDisconnect()
  }
}

onUnmounted(() => {
  wsDisconnect()
})

defineExpose({ setTopic })
</script>

<template>
  <div class="flex flex-col h-full">
    <NSpin :show="topicsStore.loading && !!topicsStore.selectedTopic">
      <template v-if="topicsStore.selectedTopic">
        <!-- Topic header -->
        <div class="flex items-center justify-between px-4 py-3 border-b border-surface-border">
          <div class="min-w-0">
            <h2 class="text-base font-semibold text-text-primary font-mono truncate">
              {{ topicsStore.selectedTopic.name }}
            </h2>
            <div class="flex items-center gap-2 mt-1">
              <NTag v-for="t in topicsStore.selectedTopic.types" :key="t" type="info" size="tiny" :bordered="false">
                {{ t }}
              </NTag>
              <span class="text-xs text-text-muted">
                {{ topicsStore.selectedTopic.publisher_count }} pub ·
                {{ topicsStore.selectedTopic.subscriber_count }} sub
              </span>
            </div>
          </div>
          <NButton
            :type="wsState === 'connected' ? 'error' : 'primary'"
            size="small"
            @click="toggleConnection"
            :loading="wsState === 'connecting'"
          >
            <template #icon>
              <component :is="wsState === 'connected' ? WifiOff : Wifi" :size="14" />
            </template>
            {{ wsState === 'connected' ? 'Disconnect' : 'Connect' }}
          </NButton>
        </div>

        <!-- Frequency chart (visible when connected) -->
        <TopicFrequencyChart v-if="wsState === 'connected'" />

        <!-- Stream controls -->
        <StreamControls v-if="wsState === 'connected'" />

        <!-- Live stream viewer -->
        <LiveStreamViewer v-if="wsState === 'connected'" />

        <!-- Not connected state -->
        <div v-if="wsState === 'disconnected'" class="flex-1 flex items-center justify-center text-text-muted py-20">
          <div class="text-center">
            <Wifi :size="32" class="mx-auto mb-2 opacity-30" />
            <p class="text-sm">Click Connect to receive real-time messages</p>
          </div>
        </div>
      </template>

      <!-- No topic selected -->
      <div v-else class="flex flex-col items-center justify-center h-full text-text-muted py-20">
        <Radio :size="40" class="mb-3 opacity-30" />
        <p class="text-sm">Select a topic to view details</p>
      </div>
    </NSpin>
  </div>
</template>
