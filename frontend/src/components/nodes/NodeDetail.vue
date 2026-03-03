<script setup lang="ts">
import { NTag, NSpin } from 'naive-ui'
import { ArrowUpRight, ArrowDownLeft, Wrench, Plug } from 'lucide-vue-next'
import { useNodesStore } from '@/stores/nodes'

const nodesStore = useNodesStore()
</script>

<template>
  <div class="h-full overflow-auto p-5">
    <NSpin :show="nodesStore.loading && !!nodesStore.selectedNode">
      <template v-if="nodesStore.selectedNode">
        <!-- Header -->
        <div class="mb-6">
          <h2 class="text-lg font-semibold text-text-primary font-mono">
            {{ nodesStore.selectedNode.full_name }}
          </h2>
          <div class="text-sm text-text-muted mt-1">
            Namespace: <span class="text-text-secondary">{{ nodesStore.selectedNode.namespace }}</span>
          </div>
        </div>

        <!-- Publishers -->
        <section class="mb-5">
          <div class="flex items-center gap-2 mb-2">
            <ArrowUpRight :size="14" class="text-live" />
            <h3 class="text-sm font-medium text-text-secondary">
              Publishers ({{ nodesStore.selectedNode.publishers.length }})
            </h3>
          </div>
          <div v-if="nodesStore.selectedNode.publishers.length === 0" class="text-sm text-text-muted pl-5">
            None
          </div>
          <div v-else class="space-y-1.5 pl-5">
            <div v-for="pub in nodesStore.selectedNode.publishers" :key="pub.topic" class="flex items-baseline gap-2">
              <span class="text-sm font-mono text-text-primary">{{ pub.topic }}</span>
              <NTag v-for="t in pub.types" :key="t" type="success" size="tiny" :bordered="false">{{ t }}</NTag>
            </div>
          </div>
        </section>

        <!-- Subscribers -->
        <section class="mb-5">
          <div class="flex items-center gap-2 mb-2">
            <ArrowDownLeft :size="14" class="text-warning" />
            <h3 class="text-sm font-medium text-text-secondary">
              Subscribers ({{ nodesStore.selectedNode.subscribers.length }})
            </h3>
          </div>
          <div v-if="nodesStore.selectedNode.subscribers.length === 0" class="text-sm text-text-muted pl-5">
            None
          </div>
          <div v-else class="space-y-1.5 pl-5">
            <div v-for="sub in nodesStore.selectedNode.subscribers" :key="sub.topic" class="flex items-baseline gap-2">
              <span class="text-sm font-mono text-text-primary">{{ sub.topic }}</span>
              <NTag v-for="t in sub.types" :key="t" type="warning" size="tiny" :bordered="false">{{ t }}</NTag>
            </div>
          </div>
        </section>

        <!-- Services -->
        <section class="mb-5">
          <div class="flex items-center gap-2 mb-2">
            <Wrench :size="14" class="text-primary" />
            <h3 class="text-sm font-medium text-text-secondary">
              Services ({{ nodesStore.selectedNode.services.length }})
            </h3>
          </div>
          <div v-if="nodesStore.selectedNode.services.length === 0" class="text-sm text-text-muted pl-5">
            None
          </div>
          <div v-else class="space-y-1.5 pl-5">
            <div v-for="srv in nodesStore.selectedNode.services" :key="srv.name" class="flex items-baseline gap-2">
              <span class="text-sm font-mono text-text-primary">{{ srv.name }}</span>
              <NTag v-for="t in srv.types" :key="t" type="info" size="tiny" :bordered="false">{{ t }}</NTag>
            </div>
          </div>
        </section>

        <!-- Clients -->
        <section>
          <div class="flex items-center gap-2 mb-2">
            <Plug :size="14" class="text-text-muted" />
            <h3 class="text-sm font-medium text-text-secondary">
              Clients ({{ nodesStore.selectedNode.clients.length }})
            </h3>
          </div>
          <div v-if="nodesStore.selectedNode.clients.length === 0" class="text-sm text-text-muted pl-5">
            None
          </div>
          <div v-else class="space-y-1.5 pl-5">
            <div v-for="cli in nodesStore.selectedNode.clients" :key="cli.name" class="flex items-baseline gap-2">
              <span class="text-sm font-mono text-text-primary">{{ cli.name }}</span>
              <NTag v-for="t in cli.types" :key="t" size="tiny" :bordered="false">{{ t }}</NTag>
            </div>
          </div>
        </section>
      </template>

      <!-- Empty state -->
      <div v-else class="flex flex-col items-center justify-center h-full text-text-muted py-20">
        <Server :size="40" class="mb-3 opacity-30" />
        <p class="text-sm">Select a node to view details</p>
      </div>
    </NSpin>
  </div>
</template>
