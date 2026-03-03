<script setup lang="ts">
import { NDataTable, NInput, NTag, NEmpty } from 'naive-ui'
import { ref, computed, h } from 'vue'
import { Search } from 'lucide-vue-next'
import type { DataTableColumns } from 'naive-ui'
import type { TopicSummary } from '@/types'
import { useTopicsStore } from '@/stores/topics'

const topicsStore = useTopicsStore()
const search = ref('')

const emit = defineEmits<{
  select: [topic: TopicSummary]
}>()

defineProps<{
  selectedName?: string
}>()

const filtered = computed(() => {
  if (!search.value) return topicsStore.topics
  const q = search.value.toLowerCase()
  return topicsStore.topics.filter(t =>
    t.name.toLowerCase().includes(q) ||
    t.types.some(typ => typ.toLowerCase().includes(q))
  )
})

const columns: DataTableColumns<TopicSummary> = [
  {
    title: 'Topic',
    key: 'name',
    sorter: 'default',
    ellipsis: { tooltip: true },
    render(row) {
      return h('span', { class: 'font-mono text-sm' }, row.name)
    },
  },
  {
    title: 'Type',
    key: 'types',
    width: 200,
    ellipsis: { tooltip: true },
    render(row) {
      return row.types.map(t =>
        h(NTag, { type: 'info', size: 'tiny', bordered: false, style: 'margin-right: 4px' }, { default: () => t })
      )
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
        placeholder="Filter topics..."
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
      <NEmpty v-if="filtered.length === 0 && !topicsStore.loading" description="No topics found" class="py-12" />
      <NDataTable
        v-else
        :columns="columns"
        :data="filtered"
        :row-props="(row: TopicSummary) => ({
          style: 'cursor: pointer',
          class: row.name === selectedName ? 'n-data-table-tr--active' : '',
          onClick: () => emit('select', row),
        })"
        :bordered="false"
        :bottom-bordered="false"
        size="small"
      />
    </div>

    <!-- Count -->
    <div class="px-3 py-2 border-t border-surface-border text-xs text-text-muted">
      {{ filtered.length }} topic{{ filtered.length !== 1 ? 's' : '' }}
    </div>
  </div>
</template>
