<script setup lang="ts">
import { computed } from 'vue'
import { NMenu, NTooltip } from 'naive-ui'
import { h } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { LayoutDashboard, Server, Radio, PanelLeftClose, PanelLeftOpen } from 'lucide-vue-next'
import { useConnectionStore } from '@/stores/connection'
import ConnectionIndicator from './ConnectionIndicator.vue'

const router = useRouter()
const route = useRoute()
const connectionStore = useConnectionStore()

const props = withDefaults(defineProps<{
  collapsed?: boolean
}>(), {
  collapsed: false,
})

const emit = defineEmits<{
  'update:collapsed': [value: boolean]
}>()

const menuOptions = [
  {
    label: 'Dashboard',
    key: 'dashboard',
    icon: () => h(LayoutDashboard, { size: 18 }),
  },
  {
    label: 'Nodes',
    key: 'nodes',
    icon: () => h(Server, { size: 18 }),
  },
  {
    label: 'Topics',
    key: 'topics',
    icon: () => h(Radio, { size: 18 }),
  },
]

const activeKey = computed(() => route.name as string)

function handleMenuUpdate(key: string) {
  router.push({ name: key })
}

function toggleCollapse() {
  emit('update:collapsed', !props.collapsed)
}
</script>

<template>
  <aside
    class="flex flex-col border-r border-surface-border bg-surface transition-all duration-200 responsive-sidebar shrink-0"
    :class="collapsed ? 'w-16' : 'w-56'"
  >
    <!-- Logo area -->
    <div class="flex items-center justify-between h-14 px-4 border-b border-surface-border shrink-0">
      <div v-if="!collapsed" class="text-sm font-semibold text-text-primary truncate">
        ROS 2 Monitor
      </div>
      <div v-else class="w-full flex justify-center">
        <Radio :size="20" class="text-primary" />
      </div>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 py-2">
      <NMenu
        :options="menuOptions"
        :value="activeKey"
        :collapsed="collapsed"
        :collapsed-width="64"
        :collapsed-icon-size="20"
        @update:value="handleMenuUpdate"
      />
    </nav>

    <!-- Bottom area -->
    <div class="border-t border-surface-border shrink-0">
      <!-- Collapse toggle -->
      <button
        class="w-full flex items-center justify-center py-2 text-text-muted hover:text-text-secondary transition-colors cursor-pointer"
        @click="toggleCollapse"
      >
        <NTooltip :disabled="!collapsed" placement="right">
          <template #trigger>
            <component :is="collapsed ? PanelLeftOpen : PanelLeftClose" :size="16" />
          </template>
          Expand sidebar
        </NTooltip>
      </button>

      <!-- Connection status -->
      <div class="px-4 py-2.5">
        <div class="flex items-center gap-2">
          <ConnectionIndicator
            :state="connectionStore.backendConnected ? 'connected' : 'disconnected'"
            :label="!collapsed"
            size="md"
          />
        </div>
      </div>
    </div>
  </aside>
</template>
