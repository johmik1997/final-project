import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface BreadcrumbRoutes {
  name: string,
  path: string
}

export const useBreadcrumb = defineStore('breadcrumb', () => {
  const breadcrumbs = ref<BreadcrumbRoutes[]>([])

  return {
    breadcrumbs
  }
})