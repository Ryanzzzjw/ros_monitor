<script setup lang="ts">
import { NLayout, NLayoutSider, NLayoutContent, NMenu, NIcon, NBadge } from 'naive-ui'
import { h, computed } from 'vue'
import { RouterView, useRouter, useRoute } from 'vue-router'
import { useConnectionStore } from '@/stores/connection'

const router = useRouter()
const route = useRoute()
const connectionStore = useConnectionStore()

const menuOptions = [
  {
    label: 'Dashboard',
    key: 'dashboard',
    icon: () => h('span', { style: 'font-size: 18px' }, '📊')
  },
  {
    label: 'Nodes',
    key: 'nodes',
    icon: () => h('span', { style: 'font-size: 18px' }, '🔗')
  },
  {
    label: 'Topics',
    key: 'topics',
    icon: () => h('span', { style: 'font-size: 18px' }, '📨')
  }
]

const activeKey = computed(() => route.name as string)

function handleMenuUpdate(key: string) {
  router.push({ name: key })
}
</script>

<template>
  <NLayout has-sider style="min-height: 100vh">
    <NLayoutSider
      bordered
      collapse-mode="width"
      :collapsed-width="64"
      :width="200"
      show-trigger
      style="background: var(--n-color)"
    >
      <div style="padding: 16px; text-align: center; font-weight: bold; font-size: 16px;">
        ROS 2 Monitor
      </div>
      <NMenu
        :options="menuOptions"
        :value="activeKey"
        @update:value="handleMenuUpdate"
      />
      <div style="position: absolute; bottom: 16px; left: 16px; right: 16px; text-align: center;">
        <NBadge
          :type="connectionStore.backendConnected ? 'success' : 'error'"
          :value="connectionStore.backendConnected ? 'Connected' : 'Disconnected'"
        />
      </div>
    </NLayoutSider>
    <NLayoutContent style="padding: 24px;">
      <RouterView />
    </NLayoutContent>
  </NLayout>
</template>
