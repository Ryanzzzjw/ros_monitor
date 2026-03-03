import { onMounted, onUnmounted } from 'vue'

export interface ShortcutHandler {
  key: string
  ctrl?: boolean
  meta?: boolean
  handler: () => void
  /** Prevent default browser behavior */
  prevent?: boolean
}

/**
 * Register global keyboard shortcuts.
 * Automatically cleaned up on component unmount.
 */
export function useKeyboardShortcuts(shortcuts: ShortcutHandler[]) {
  function handleKeydown(e: KeyboardEvent) {
    // Skip when typing in input/textarea elements
    const tag = (e.target as HTMLElement)?.tagName
    if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') {
      // Allow Escape in inputs
      if (e.key !== 'Escape') return
    }

    for (const shortcut of shortcuts) {
      const ctrlMatch = shortcut.ctrl
        ? (e.ctrlKey || e.metaKey)
        : true
      const metaMatch = shortcut.meta
        ? e.metaKey
        : true
      const keyMatch = e.key.toLowerCase() === shortcut.key.toLowerCase()

      if (keyMatch && ctrlMatch && metaMatch) {
        if (shortcut.prevent !== false) {
          e.preventDefault()
          e.stopPropagation()
        }
        shortcut.handler()
        return
      }
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeydown, true)
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown, true)
  })
}
