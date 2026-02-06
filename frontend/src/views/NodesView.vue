<script setup lang="ts">
import { NCard, NDataTable, NDrawer, NDrawerContent, NDescriptions, NDescriptionsItem, NTag, NSpin, NEmpty } from 'naive-ui'
import { ref, onMounted, onUnmounted, h } from 'vue'
import type { DataTableColumns } from 'naive-ui'
import type { NodeSummary } from '@/types'
import { useNodesStore } from '@/stores/nodes'
import { usePolling } from '@/composables/usePolling'

const nodesStore = useNodesStore()
const showDrawer = ref(false)

const columns: DataTableColumns<NodeSummary> = [
  {
    title: 'Name',
    key: 'name',
    sorter: 'default'
  },
  {
    title: 'Namespace',
    key: 'namespace',
    sorter: 'default',
    render(row) {
      return h(NTag, { type: 'info', size: 'small' }, { default: () => row.namespace })
    }
  },
  {
    title: 'Full Name',
    key: 'full_name'
  }
]

function handleRowClick(row: NodeSummary) {
  nodesStore.loadNodeDetail(row.namespace, row.name)
  showDrawer.value = true
}

function handleDrawerClose() {
  showDrawer.value = false
  nodesStore.clearSelection()
}

const { start, stop } = usePolling(() => nodesStore.loadNodes(), 2000, { immediate: false })

onMounted(() => {
  nodesStore.loadNodes()
  start()
})

onUnmounted(() => {
  stop()
})
</script>

<template>
  <div>
    <h1 style="margin-bottom: 24px;">ROS Nodes</h1>

    <NCard>
      <NSpin :show="nodesStore.loading && nodesStore.nodes.length === 0">
        <NEmpty v-if="nodesStore.nodes.length === 0 && !nodesStore.loading" description="No nodes found" />
        <NDataTable
          v-else
          :columns="columns"
          :data="nodesStore.nodes"
          :row-props="(row: NodeSummary) => ({ style: 'cursor: pointer', onClick: () => handleRowClick(row) })"
          :pagination="{ pageSize: 20 }"
        />
      </NSpin>
    </NCard>

    <NDrawer v-model:show="showDrawer" :width="500" @after-leave="handleDrawerClose">
      <NDrawerContent :title="nodesStore.selectedNode?.full_name || 'Node Detail'">
        <NSpin :show="nodesStore.loading">
          <template v-if="nodesStore.selectedNode">
            <NDescriptions label-placement="left" :column="1" style="margin-bottom: 24px;">
              <NDescriptionsItem label="Name">{{ nodesStore.selectedNode.name }}</NDescriptionsItem>
              <NDescriptionsItem label="Namespace">{{ nodesStore.selectedNode.namespace }}</NDescriptionsItem>
            </NDescriptions>

            <h4>Publishers ({{ nodesStore.selectedNode.publishers.length }})</h4>
            <div v-if="nodesStore.selectedNode.publishers.length === 0" style="color: #999; margin-bottom: 16px;">None</div>
            <div v-else style="margin-bottom: 16px;">
              <div v-for="pub in nodesStore.selectedNode.publishers" :key="pub.topic" style="margin-bottom: 8px;">
                <NTag type="success" size="small">{{ pub.topic }}</NTag>
                <span style="margin-left: 8px; color: #999; font-size: 12px;">{{ pub.types.join(', ') }}</span>
              </div>
            </div>

            <h4>Subscribers ({{ nodesStore.selectedNode.subscribers.length }})</h4>
            <div v-if="nodesStore.selectedNode.subscribers.length === 0" style="color: #999; margin-bottom: 16px;">None</div>
            <div v-else style="margin-bottom: 16px;">
              <div v-for="sub in nodesStore.selectedNode.subscribers" :key="sub.topic" style="margin-bottom: 8px;">
                <NTag type="warning" size="small">{{ sub.topic }}</NTag>
                <span style="margin-left: 8px; color: #999; font-size: 12px;">{{ sub.types.join(', ') }}</span>
              </div>
            </div>

            <h4>Services ({{ nodesStore.selectedNode.services.length }})</h4>
            <div v-if="nodesStore.selectedNode.services.length === 0" style="color: #999; margin-bottom: 16px;">None</div>
            <div v-else style="margin-bottom: 16px;">
              <div v-for="srv in nodesStore.selectedNode.services" :key="srv.name" style="margin-bottom: 8px;">
                <NTag type="info" size="small">{{ srv.name }}</NTag>
                <span style="margin-left: 8px; color: #999; font-size: 12px;">{{ srv.types.join(', ') }}</span>
              </div>
            </div>

            <h4>Clients ({{ nodesStore.selectedNode.clients.length }})</h4>
            <div v-if="nodesStore.selectedNode.clients.length === 0" style="color: #999;">None</div>
            <div v-else>
              <div v-for="cli in nodesStore.selectedNode.clients" :key="cli.name" style="margin-bottom: 8px;">
                <NTag type="default" size="small">{{ cli.name }}</NTag>
                <span style="margin-left: 8px; color: #999; font-size: 12px;">{{ cli.types.join(', ') }}</span>
              </div>
            </div>
          </template>
        </NSpin>
      </NDrawerContent>
    </NDrawer>
  </div>
</template>
