<template>
  <button
    @click="toggleTheme"
    class="theme-toggle-btn"
    :title="hoverLabel"
    :aria-label="hoverLabel"
  >
    <span class="theme-tooltip">{{ hoverLabel }}</span>
    <!-- Sun icon for light mode -->
    <svg
      v-if="!isDark"
      class="theme-icon sun-icon"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <circle cx="12" cy="12" r="5"/>
      <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
    </svg>
    <!-- Moon icon for dark mode -->
    <svg
      v-else
      class="theme-icon moon-icon"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    </svg>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useTheme } from '@/composables/useTheme'

const { isDark, toggleTheme } = useTheme()
const hoverLabel = computed(() => (isDark.value ? 'Light mode' : 'Dark mode'))
</script>

<style scoped>
.theme-toggle-btn {
  @apply relative p-2 rounded-lg transition-all duration-200 hover:bg-amber-500/10 focus:outline-none focus:ring-2 focus:ring-amber-500/50;
}

.theme-icon {
  @apply w-5 h-5 text-slate-600 dark:text-slate-300 hover:text-amber-500 dark:hover:text-amber-400 transition-colors duration-200;
}

.sun-icon {
  @apply text-amber-500;
}

.moon-icon {
  @apply text-slate-600 dark:text-slate-300;
}

.theme-tooltip {
  @apply pointer-events-none absolute left-1/2 top-full z-10 mt-2 -translate-x-1/2 rounded-md bg-slate-900 px-2 py-1 text-xs font-medium text-white opacity-0 shadow-lg transition-opacity duration-200 dark:bg-slate-100 dark:text-slate-900;
  white-space: nowrap;
}

.theme-toggle-btn:hover .theme-tooltip,
.theme-toggle-btn:focus-visible .theme-tooltip {
  @apply opacity-100;
}
</style>
