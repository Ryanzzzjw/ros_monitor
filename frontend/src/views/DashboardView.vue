<script setup lang="ts">
import { NAlert } from 'naive-ui'
import { Server, Radio, Wifi, WifiOff } from 'lucide-vue-next'
import { useNodesStore } from '@/stores/nodes'
import { useTopicsStore } from '@/stores/topics'
import { useConnectionStore } from '@/stores/connection'
import StatsCard from '@/components/common/StatsCard.vue'
import FrequencyChart from '@/components/dashboard/FrequencyChart.vue'
import ActivityFeed from '@/components/dashboard/ActivityFeed.vue'

const nodesStore = useNodesStore()
const topicsStore = useTopicsStore()
const connectionStore = useConnectionStore()
</script>

<template>
  <div>
    <!-- Backend disconnection alert -->
    <NAlert
      v-if="!connectionStore.backendConnected"
      type="error"
      title="Backend Disconnected"
      class="mb-6"
    >
      Cannot connect to the ROS 2 Web Monitor backend. Please ensure the server is running.
    </NAlert>

    <!-- Stats cards row -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <StatsCard
        :icon="Server"
        :value="nodesStore.nodeCount"
        label="Active Nodes"
        color="primary"
      />
      <StatsCard
        :icon="Radio"
        :value="topicsStore.topicCount"
        label="Active Topics"
        color="live"
      />
      <StatsCard
        :icon="connectionStore.backendConnected ? Wifi : WifiOff"
        :value="connectionStore.backendConnected ? 'Online' : 'Offline'"
        label="Backend Status"
        :color="connectionStore.backendConnected ? 'live' : 'danger'"
      />
      <StatsCard
        :icon="Radio"
        :value="connectionStore.domainId ?? 'N/A'"
        label="Domain ID"
        color="warning"
      />
    </div>

    <!-- Chart + Activity feed -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <FrequencyChart />
      <ActivityFeed />
    </div>
  </div>
</template>
