<script setup lang="ts">
import { NConfigProvider, NMessageProvider, darkTheme } from 'naive-ui'
import { ref } from 'vue'
import AppLayout from './components/layout/AppLayout.vue'

const isDark = ref(true)
</script>

<template>
  <NConfigProvider :theme="isDark ? darkTheme : undefined">
    <NMessageProvider>
      <AppLayout />
    </NMessageProvider>
  </NConfigProvider>
</template>

<style>
body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
}

#app {
  min-height: 100vh;
}
</style>
