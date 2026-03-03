import { ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

/**
 * Two-way sync between a reactive value and a URL query parameter.
 * Changes to the ref update the URL; navigating to a URL with the param sets the ref.
 */
export function useUrlState(paramName: string, defaultValue = '') {
  const router = useRouter()
  const route = useRoute()
  const state = ref(defaultValue)

  // Read from URL on mount
  onMounted(() => {
    const value = route.query[paramName]
    if (typeof value === 'string' && value) {
      state.value = value
    }
  })

  // Write to URL when state changes
  watch(state, (newVal) => {
    const currentQuery = { ...route.query }
    if (newVal && newVal !== defaultValue) {
      currentQuery[paramName] = newVal
    } else {
      delete currentQuery[paramName]
    }
    router.replace({ query: currentQuery })
  })

  // Read from URL when route changes (browser back/forward)
  watch(
    () => route.query[paramName],
    (newVal) => {
      const val = typeof newVal === 'string' ? newVal : defaultValue
      if (val !== state.value) {
        state.value = val
      }
    }
  )

  return state
}
