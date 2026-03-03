<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterView } from 'vue-router'
import { useRosApi } from '@/composables/useRosApi'
import { useConnectionStore } from '@/stores/connection'
import { useTopicsStore } from '@/stores/topics'
import { useKeyboardShortcuts } from '@/composables/useKeyboardShortcuts'
import AppSidebar from './AppSidebar.vue'
import AppHeader from './AppHeader.vue'
import SearchModal from '@/components/common/SearchModal.vue'

const connectionStore = useConnectionStore()
const topicsStore = useTopicsStore()
const { startAllPolling, stopAllPolling } = useRosApi()

const sidebarCollapsed = ref(false)
const showSearch = ref(false)

// Global keyboard shortcuts
useKeyboardShortcuts([
  {
    key: 'k',
    ctrl: true,
    handler: () => { showSearch.value = !showSearch.value },
  },
  {
    key: 'Escape',
    handler: () => { showSearch.value = false },
  },
  {
    key: ' ',
    handler: () => { topicsStore.togglePause() },
    prevent: true,
  },
])

onMounted(() => {
  connectionStore.loadConfig()
  startAllPolling()
})

onUnmounted(() => {
  stopAllPolling()
})
</script>

<template>
  <div class="flex h-screen overflow-hidden bg-bg">
    <!-- Sidebar -->
    <AppSidebar v-model:collapsed="sidebarCollapsed" />

    <!-- Main area -->
    <div class="flex flex-col flex-1 min-w-0">
      <!-- Header -->
      <AppHeader @open-search="showSearch = true" />

      <!-- Content -->
      <main class="flex-1 overflow-auto p-6">
        <RouterView />
      </main>
    </div>

    <!-- Search modal -->
    <SearchModal v-model:show="showSearch" />
  </div>
</template>
