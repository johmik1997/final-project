<script setup>
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiBook, mdiCheckCircle, mdiClockOutline, mdiTag, mdiTrendingUp, mdiLibrary } from '@mdi/js';
import { computed } from 'vue';

const props = defineProps({ 
  stats: { type: Object, required: true },
  showTrends: { type: Boolean, default: false }
});

const statItems = computed(() => [
  { 
    label: 'Total Books', 
    key: 'total', 
    icon: mdiLibrary, 
    gradient: 'from-blue-500 to-indigo-500',
    bgGradient: 'from-blue-50 to-indigo-50 dark:from-blue-950/30 dark:to-indigo-950/30',
    textColor: 'text-blue-600 dark:text-blue-400'
  },
  { 
    label: 'Available', 
    key: 'available', 
    icon: mdiCheckCircle, 
    gradient: 'from-emerald-500 to-green-500',
    bgGradient: 'from-emerald-50 to-green-50 dark:from-emerald-950/30 dark:to-green-950/30',
    textColor: 'text-emerald-600 dark:text-emerald-400'
  },
  { 
    label: 'On Loan', 
    key: 'borrowed', 
    icon: mdiClockOutline, 
    gradient: 'from-amber-500 to-orange-500',
    bgGradient: 'from-amber-50 to-orange-50 dark:from-amber-950/30 dark:to-orange-950/30',
    textColor: 'text-amber-600 dark:text-amber-400'
  },
  { 
    label: 'Categories', 
    key: 'categories', 
    icon: mdiTag, 
    gradient: 'from-purple-500 to-pink-500',
    bgGradient: 'from-purple-50 to-pink-50 dark:from-purple-950/30 dark:to-pink-950/30',
    textColor: 'text-purple-600 dark:text-purple-400'
  }
]);
</script>

<template>
  <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
    <div 
      v-for="(item, index) in statItems" 
      :key="item.key"
      class="group relative overflow-hidden bg-white dark:bg-slate-800 rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
    >
      <!-- Animated Background Gradient -->
      <div 
        class="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
        :class="`bg-gradient-to-br ${item.bgGradient}`"
      ></div>
      
      <!-- Card Content -->
      <div class="relative p-5">
        <div class="flex items-start justify-between">
          <!-- Value and Label -->
          <div class="flex-1">
            <div class="flex items-baseline gap-1">
              <p 
                class="text-3xl font-bold transition-all duration-300 group-hover:scale-105 origin-left"
                :class="item.textColor"
              >
                {{ props.stats[item.key] || 0 }}
              </p>
              <span v-if="showTrends" class="text-xs font-medium text-green-600 dark:text-green-400 flex items-center gap-0.5">
                <BaseIcon :path="mdiTrendingUp" size="12" />
                +12%
              </span>
            </div>
            <p class="text-sm font-medium text-gray-500 dark:text-gray-400 mt-1.5">{{ item.label }}</p>
          </div>

          <!-- Icon with Gradient -->
          <div 
            class="w-12 h-12 rounded-xl flex items-center justify-center shadow-md transition-all duration-300 group-hover:scale-110 group-hover:shadow-lg"
            :class="`bg-gradient-to-br ${item.gradient}`"
          >
            <BaseIcon :path="item.icon" size="22" class="text-white" />
          </div>
        </div>

        <!-- Animated Bottom Border -->
        <div 
          class="absolute bottom-0 left-0 h-1 rounded-full transition-all duration-500 group-hover:w-full"
          :class="`w-0 bg-gradient-to-r ${item.gradient}`"
        ></div>
      </div>

      <!-- Decorative Pattern -->
      <div class="absolute -bottom-2 -right-2 w-16 h-16 opacity-5 group-hover:opacity-10 transition-opacity duration-300">
        <BaseIcon :path="item.icon" size="64" />
      </div>
    </div>
  </div>
</template>