<script setup>
import BaseIcon from '@/components/base/BaseIcon.vue';
import { 
  mdiLibrary, 
  mdiViewGrid, 
  mdiFormatListBulleted,
  mdiBook,
  mdiCheckCircle,
  mdiClockOutline,
  mdiTag
} from '@mdi/js';

defineProps({
  stats: {
    type: Object,
    default: () => ({
      total: 0,
      available: 0,
      borrowed: 0,
      categories: 0,
    }),
  },
  viewMode: {
    type: String,
    default: 'grid'
  },
  showViewToggle: {
    type: Boolean,
    default: true,
  }
});

defineEmits(['update:viewMode']);
</script>

<template>
  <div class="bg-gradient-to-br from-amber-50/50 via-white to-orange-50/30 dark:from-slate-800 dark:via-slate-800 dark:to-slate-800/80 rounded-xl p-6 border border-gray-200 dark:border-slate-700 shadow-sm transition-all duration-300">
    <div class="flex items-center justify-between mb-6">
      <div class="flex items-center gap-4">
        <div class="bg-gradient-to-r from-amber-500 to-orange-500 p-3 rounded-xl shadow-md">
          <BaseIcon :path="mdiLibrary" size="24" class="text-white" />
        </div>
        <div>
          <h2 class="text-xl font-semibold text-gray-900 dark:text-white">Library Catalog</h2>
          <p class="text-sm text-gray-500 dark:text-gray-400">Browse and select materials</p>
        </div>
      </div>
      
      <div v-if="showViewToggle" class="flex items-center gap-1 bg-white dark:bg-slate-900 rounded-lg p-1 border border-gray-200 dark:border-slate-700">
        <button
          @click="$emit('update:viewMode', 'grid')"
          class="p-2 rounded-lg transition-all duration-200"
          :class="viewMode === 'grid' ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-md' : 'text-gray-400 dark:text-gray-600 hover:bg-gray-100 dark:hover:bg-slate-800'"
        >
          <BaseIcon :path="mdiViewGrid" size="18" />
        </button>
        <button
          @click="$emit('update:viewMode', 'list')"
          class="p-2 rounded-lg transition-all duration-200"
          :class="viewMode === 'list' ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-md' : 'text-gray-400 dark:text-gray-600 hover:bg-gray-100 dark:hover:bg-slate-800'"
        >
          <BaseIcon :path="mdiFormatListBulleted" size="18" />
        </button>
      </div>
    </div>
    
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-gray-200 dark:border-slate-700 transition-all duration-300 hover:shadow-md">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ stats.total }}</p>
            <p class="text-xs font-medium text-gray-500 dark:text-gray-400">Total Books</p>
          </div>
          <div class="p-2.5 bg-amber-100 dark:bg-amber-950 rounded-lg">
            <BaseIcon :path="mdiBook" size="20" class="text-amber-600 dark:text-amber-400" />
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-gray-200 dark:border-slate-700 transition-all duration-300 hover:shadow-md">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-2xl font-bold text-green-600 dark:text-green-400">{{ stats.available }}</p>
            <p class="text-xs font-medium text-gray-500 dark:text-gray-400">Available</p>
          </div>
          <div class="p-2.5 bg-green-100 dark:bg-green-950 rounded-lg">
            <BaseIcon :path="mdiCheckCircle" size="20" class="text-green-600 dark:text-green-400" />
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-gray-200 dark:border-slate-700 transition-all duration-300 hover:shadow-md">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-2xl font-bold text-amber-600 dark:text-amber-400">{{ stats.borrowed }}</p>
            <p class="text-xs font-medium text-gray-500 dark:text-gray-400">On Loan</p>
          </div>
          <div class="p-2.5 bg-amber-100 dark:bg-amber-950 rounded-lg">
            <BaseIcon :path="mdiClockOutline" size="20" class="text-amber-600 dark:text-amber-400" />
          </div>
        </div>
      </div>

      <div class="bg-white dark:bg-slate-800 rounded-xl p-4 border border-gray-200 dark:border-slate-700 transition-all duration-300 hover:shadow-md">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-2xl font-bold text-orange-600 dark:text-orange-400">{{ stats.categories }}</p>
            <p class="text-xs font-medium text-gray-500 dark:text-gray-400">Categories</p>
          </div>
          <div class="p-2.5 bg-orange-100 dark:bg-orange-950 rounded-lg">
            <BaseIcon :path="mdiTag" size="20" class="text-orange-600 dark:text-orange-400" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>