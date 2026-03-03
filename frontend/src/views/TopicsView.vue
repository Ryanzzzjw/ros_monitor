<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'
import type { TopicSummary } from '@/types'
import { useTopicsStore } from '@/stores/topics'
import { useUrlState } from '@/composables/useUrlState'
import TopicList from '@/components/topics/TopicList.vue'
import TopicDetail from '@/components/topics/TopicDetail.vue'

const topicsStore = useTopicsStore()
const topicDetailRef = ref<InstanceType<typeof TopicDetail> | null>(null)
const selectedName = ref<string | undefined>()
const urlTopicName = useUrlState('topic')

function handleSelect(topic: TopicSummary) {
  selectedName.value = topic.name
  urlTopicName.value = topic.name
  topicsStore.loadTopicDetail(topic.name)
  topicDetailRef.value?.setTopic(topic.name, topic.types[0] || '')
}

// Load topic from URL on mount
watch(urlTopicName, (name) => {
  if (name && !selectedName.value) {
    const match = topicsStore.topics.find(t => t.name === name)
    if (match) {
      handleSelect(match)
    }
  }
}, { immediate: true })

onUnmounted(() => {
  topicsStore.clearSelection()
})
</script>

<template>
  <div class="flex h-full -m-6">
    <!-- Master: topic list (40%) -->
    <div class="w-2/5 min-w-[280px] border-r border-surface-border bg-surface">
      <TopicList :selected-name="selectedName" @select="handleSelect" />
    </div>

    <!-- Detail panel (60%) -->
    <div class="flex-1 min-w-0">
      <Transition name="fade">
        <TopicDetail ref="topicDetailRef" :key="selectedName ?? 'empty'" />
      </Transition>
    </div>
  </div>
</template>
