<script setup lang="ts">
import { NCard, NGrid, NGridItem, NStatistic, NSpin, NAlert } from 'naive-ui'
import { onMounted, onUnmounted } from 'vue'
import { useRosApi } from '@/composables/useRosApi'

const { nodesStore, topicsStore, connectionStore, startAllPolling, stopAllPolling } = useRosApi()

onMounted(() => {
  startAllPolling()
})

onUnmounted(() => {
  stopAllPolling()
})
</script>

<template>
  <div>
    <h1 style="margin-bottom: 24px;">Dashboard</h1>

    <NAlert
      v-if="!connectionStore.backendConnected"
      type="error"
      title="Backend Disconnected"
      style="margin-bottom: 24px;"
    >
      Cannot connect to the ROS 2 Web Monitor backend. Please ensure the server is running.
    </NAlert>

    <NGrid :cols="3" :x-gap="16" :y-gap="16">
      <NGridItem>
        <NCard title="ROS Nodes">
          <NSpin :show="nodesStore.loading">
            <NStatistic label="Active Nodes" :value="nodesStore.nodeCount" />
          </NSpin>
        </NCard>
      </NGridItem>

      <NGridItem>
        <NCard title="Topics">
          <NSpin :show="topicsStore.loading">
            <NStatistic label="Active Topics" :value="topicsStore.topicCount" />
          </NSpin>
        </NCard>
      </NGridItem>

      <NGridItem>
        <NCard title="Connection">
          <NStatistic
            label="Backend Status"
            :value="connectionStore.backendConnected ? 'Connected' : 'Disconnected'"
          />
        </NCard>
      </NGridItem>
    </NGrid>

    <NCard title="Recent Activity" style="margin-top: 24px;">
      <p v-if="nodesStore.nodes.length === 0 && topicsStore.topics.length === 0">
        No ROS nodes or topics detected. Make sure ROS 2 nodes are running.
      </p>
      <div v-else>
        <p><strong>Nodes:</strong> {{ nodesStore.nodes.slice(0, 5).map(n => n.name).join(', ') }}{{ nodesStore.nodes.length > 5 ? '...' : '' }}</p>
        <p><strong>Topics:</strong> {{ topicsStore.topics.slice(0, 5).map(t => t.name).join(', ') }}{{ topicsStore.topics.length > 5 ? '...' : '' }}</p>
      </div>
    </NCard>
  </div>
</template>
