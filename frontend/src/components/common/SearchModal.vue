<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { NModal, NInput } from 'naive-ui'
import { Search, Server, Radio } from 'lucide-vue-next'
import { useRouter } from 'vue-router'
import { useNodesStore } from '@/stores/nodes'
import { useTopicsStore } from '@/stores/topics'

const props = defineProps<{
  show: boolean
}>()

const emit = defineEmits<{
  'update:show': [value: boolean]
}>()

const router = useRouter()
const nodesStore = useNodesStore()
const topicsStore = useTopicsStore()

const query = ref('')
const selectedIndex = ref(0)
const inputRef = ref<InstanceType<typeof NInput> | null>(null)

interface SearchResult {
  type: 'node' | 'topic'
  name: string
  detail: string
}

const results = computed<SearchResult[]>(() => {
  const q = query.value.toLowerCase().trim()
  const items: SearchResult[] = []

  for (const node of nodesStore.nodes) {
    if (!q || node.name.toLowerCase().includes(q) || node.full_name.toLowerCase().includes(q)) {
      items.push({ type: 'node', name: node.full_name, detail: node.namespace })
    }
  }

  for (const topic of topicsStore.topics) {
    if (!q || topic.name.toLowerCase().includes(q) || topic.types.some(t => t.toLowerCase().includes(q))) {
      items.push({ type: 'topic', name: topic.name, detail: topic.types[0] || '' })
    }
  }

  return items.slice(0, 20)
})

watch(() => props.show, (val) => {
  if (val) {
    query.value = ''
    selectedIndex.value = 0
    nextTick(() => {
      inputRef.value?.focus()
    })
  }
})

watch(query, () => {
  selectedIndex.value = 0
})

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    selectedIndex.value = Math.min(selectedIndex.value + 1, results.value.length - 1)
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    selectedIndex.value = Math.max(selectedIndex.value - 1, 0)
  } else if (e.key === 'Enter') {
    e.preventDefault()
    selectResult(results.value[selectedIndex.value])
  }
}

function selectResult(result: SearchResult | undefined) {
  if (!result) return
  emit('update:show', false)

  if (result.type === 'node') {
    router.push({ name: 'nodes', query: { node: result.name } })
  } else {
    router.push({ name: 'topics', query: { topic: result.name } })
  }
}
</script>

<template>
  <NModal
    :show="show"
    @update:show="emit('update:show', $event)"
    :mask-closable="true"
    :auto-focus="false"
    preset="card"
    :bordered="false"
    size="small"
    style="width: 480px; max-height: 400px;"
    class="!bg-surface !border !border-surface-border"
  >
    <!-- Search input -->
    <div class="border-b border-surface-border pb-3 mb-2">
      <NInput
        ref="inputRef"
        v-model:value="query"
        placeholder="Search nodes, topics..."
        size="large"
        :bordered="false"
        @keydown="handleKeydown"
      >
        <template #prefix>
          <Search :size="16" class="text-text-muted" />
        </template>
      </NInput>
    </div>

    <!-- Results -->
    <div class="max-h-[280px] overflow-auto -mx-2">
      <div v-if="results.length === 0" class="px-4 py-8 text-center text-text-muted text-sm">
        No results found
      </div>

      <div
        v-for="(result, idx) in results"
        :key="`${result.type}-${result.name}`"
        class="flex items-center gap-3 px-3 py-2 mx-1 rounded cursor-pointer transition-colors"
        :class="idx === selectedIndex ? 'bg-primary/10' : 'hover:bg-surface-hover'"
        @click="selectResult(result)"
        @mouseenter="selectedIndex = idx"
      >
        <component
          :is="result.type === 'node' ? Server : Radio"
          :size="14"
          :class="result.type === 'node' ? 'text-primary' : 'text-live'"
        />
        <div class="min-w-0 flex-1">
          <div class="text-sm text-text-primary font-mono truncate">{{ result.name }}</div>
          <div class="text-xs text-text-muted truncate">{{ result.detail }}</div>
        </div>
        <span class="text-[10px] text-text-muted uppercase">{{ result.type }}</span>
      </div>
    </div>

    <!-- Footer hint -->
    <div class="border-t border-surface-border pt-2 mt-2 flex items-center gap-4 text-[10px] text-text-muted">
      <span><kbd class="px-1 py-0.5 bg-bg border border-surface-border rounded text-[10px]">↑↓</kbd> navigate</span>
      <span><kbd class="px-1 py-0.5 bg-bg border border-surface-border rounded text-[10px]">↵</kbd> select</span>
      <span><kbd class="px-1 py-0.5 bg-bg border border-surface-border rounded text-[10px]">esc</kbd> close</span>
    </div>
  </NModal>
</template>
