import { ref, watch } from 'vue'

function readStoredTheme() {
  if (typeof window === 'undefined') return true
  const saved = localStorage.getItem('theme')
  if (saved === 'light') return false
  if (saved === 'dark') return true
  return true
}

const isDark = ref(readStoredTheme())

export function useTheme() {
  const toggleTheme = () => {
    isDark.value = !isDark.value
  }

  const setTheme = (dark) => {
    isDark.value = dark
  }

  watch(
    isDark,
    (newValue) => {
      if (newValue) {
        document.documentElement.classList.add('dark')
        localStorage.setItem('theme', 'dark')
      } else {
        document.documentElement.classList.remove('dark')
        localStorage.setItem('theme', 'light')
      }
    },
    { immediate: true }
  )

  return {
    isDark,
    toggleTheme,
    setTheme,
  }
}
