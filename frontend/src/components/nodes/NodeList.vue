<script setup lang="ts">
import { NDataTable, NInput, NTag, NEmpty } from 'naive-ui'
import { ref, computed, h } from 'vue'
import { Search } from 'lucide-vue-next'
import type { DataTableColumns } from 'naive-ui'
import type { NodeSummary } from '@/types'
import { useNodesStore } from '@/stores/nodes'

const nodesStore = useNodesStore()
const search = ref('')

const emit = defineEmits<{
  select: [node: NodeSummary]
}>()

defineProps<{
  selectedName?: string
}>()

const filtered = computed(() => {
  if (!search.value) return nodesStore.nodes
  const q = search.value.toLowerCase()
  return nodesStore.nodes.filter(n =>
    n.name.toLowerCase().includes(q) ||
    n.namespace.toLowerCase().includes(q) ||
    n.full_name.toLowerCase().includes(q)
  )
})

const columns: DataTableColumns<NodeSummary> = [
  {
    title: 'Name',
    key: 'name',
    sorter: 'default',
    ellipsis: { tooltip: true },
  },
  {
    title: 'Namespace',
    key: 'namespace',
    width: 120,
    sorter: 'default',
    render(row) {
      return h(NTag, { type: 'info', size: 'small', bordered: false }, { default: () => row.namespace })
    },
  },
]
</script>

<template>
  <div class="flex flex-col h-full">
    <!-- Search -->
    <div class="p-3 border-b border-surface-border">
      <NInput
        v-model:value="search"
        placeholder="Filter nodes..."
        size="small"
        clearable
      >
        <template #prefix>
          <Search :size="14" class="text-text-muted" />
        </template>
      </NInput>
    </div>

    <!-- Table -->
    <div class="flex-1 overflow-auto">
      <NEmpty v-if="filtered.length === 0 && !nodesStore.loading" description="No nodes found" class="py-12" />
      <NDataTable
        v-else
        :columns="columns"
        :data="filtered"
        :row-props="(row: NodeSummary) => ({
          style: 'cursor: pointer',
          class: row.full_name === selectedName ? 'n-data-table-tr--active' : '',
          onClick: () => emit('select', row),
        })"
        :bordered="false"
        :bottom-bordered="false"
        size="small"
        :max-height="undefined"
      />
    </div>

    <!-- Count -->
    <div class="px-3 py-2 border-t border-surface-border text-xs text-text-muted">
      {{ filtered.length }} node{{ filtered.length !== 1 ? 's' : '' }}
    </div>
  </div>
</template>
