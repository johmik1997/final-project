<script setup>
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiBook, mdiAccount, mdiCheckCircle, mdiStar, mdiBookOpenPageVariant } from '@mdi/js';
import { computed } from 'vue';

const props = defineProps({
  material: Object,
  isSelected: Boolean,
  selectUnavailableOnly: {
    type: Boolean,
    default: false,
  },
  viewMode: {
    type: String,
    default: 'grid',
  },
});

const emit = defineEmits(['select']);

const availabilityStatus = computed(() => {
  if (props.material.available_copies === 0) return 'unavailable';
  if (props.material.available_copies < 3) return 'limited';
  return 'available';
});

const statusClasses = {
  available: 'bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-300',
  limited: 'bg-amber-100 dark:bg-amber-900/50 text-amber-700 dark:text-amber-300',
  unavailable: 'bg-red-100 dark:bg-red-900/50 text-red-700 dark:text-red-300'
};

const statusText = {
  available: 'Available',
  limited: 'Limited',
  unavailable: 'Out of Stock'
};

const isSelectable = computed(() => {
  const availableCopies = Number(props.material?.available_copies || 0);
  return props.selectUnavailableOnly ? availableCopies <= 0 : availableCopies > 0;
});

const availabilityPercentage = computed(() => {
  const total = Number(props.material?.total_copies || 1);
  const available = Number(props.material?.available_copies || 0);
  return (available / total) * 100;
});
</script>

<template>
  <div 
    @click="isSelectable && emit('select', material)"
    class="group relative bg-white dark:bg-slate-800 rounded-xl border-2 transition-all duration-300 cursor-pointer overflow-hidden"
    :class="[
      isSelected 
        ? 'border-amber-500 ring-4 ring-amber-500/20 dark:ring-amber-500/30 shadow-lg' 
        : 'border-gray-200 dark:border-slate-700 hover:border-amber-400 dark:hover:border-amber-600 hover:shadow-md',
      !isSelectable ? 'opacity-60 cursor-not-allowed hover:border-gray-200 dark:hover:border-slate-700' : '',
      viewMode === 'list' ? 'flex items-stretch' : ''
    ]"
  >
    <!-- Card Image/Icon Section -->
    <div
      class="relative bg-gradient-to-br from-amber-50/50 to-orange-50/30 dark:from-slate-700 dark:to-slate-800 flex items-center justify-center"
      :class="viewMode === 'list' ? 'w-28 border-r border-gray-100 dark:border-slate-700' : 'h-32 border-b border-gray-100 dark:border-slate-700'"
    >
      <div class="w-14 h-14 bg-white dark:bg-slate-700 rounded-xl shadow-md flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
        <BaseIcon 
          :path="mdiBook" 
          size="28" 
          class="text-amber-500 dark:text-amber-400" 
        />
      </div>
      
      <!-- Selected Badge -->
      <div 
        v-if="isSelected" 
        class="absolute top-2 right-2 bg-gradient-to-r from-amber-500 to-orange-500 text-white p-1.5 rounded-lg shadow-md animate-pulse"
      >
        <BaseIcon :path="mdiCheckCircle" size="14" />
      </div>

      <!-- Availability Badge on Image -->
      <div 
        v-if="availabilityStatus === 'limited'" 
        class="absolute bottom-2 left-2 bg-amber-500 text-white text-[10px] font-bold px-2 py-0.5 rounded-full"
      >
        Low Stock
      </div>
    </div>

    <!-- Card Content -->
    <div class="p-3" :class="viewMode === 'list' ? 'flex-1 flex flex-col justify-center' : ''">
      <h5 class="font-semibold text-gray-900 dark:text-white truncate mb-1 group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors text-sm">
        {{ material.title || 'Untitled' }}
      </h5>
      
      <div class="flex justify-between items-center mb-2">
        <p class="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
          <BaseIcon :path="mdiAccount" size="10" class="text-gray-400 dark:text-gray-600" />
          {{ material.author || 'Unknown Author' }}
        </p>
        <div class="flex items-center text-amber-500 text-xs font-medium" v-if="material.average_rating || material.rating">
          <BaseIcon :path="mdiStar" size="12" />
          <span class="ml-0.5">{{ Number(material.average_rating || material.rating || 0).toFixed(1) }}</span>
        </div>
      </div>

      <!-- Additional Info for List View -->
      <div v-if="viewMode === 'list'" class="flex items-center gap-3 mt-1 text-xs">
        <span class="text-gray-500 dark:text-gray-400">ISBN: {{ material.isbn || 'N/A' }}</span>
        <span class="text-gray-500 dark:text-gray-400">Category: {{ material.category || 'General' }}</span>
      </div>

      <!-- Status and Copies -->
      <div class="flex items-center justify-between" :class="viewMode === 'list' ? 'mt-2' : ''">
        <span 
          class="text-[10px] font-semibold px-2 py-0.5 rounded-full transition-all"
          :class="statusClasses[availabilityStatus]"
        >
          {{ statusText[availabilityStatus] }}
        </span>
        <div class="flex items-center gap-1">
          <span class="text-xs font-medium text-gray-700 dark:text-gray-300">
            {{ material.available_copies || 0 }}/{{ material.total_copies || 0 }}
          </span>
          <span class="text-[10px] text-gray-400 dark:text-gray-600">copies</span>
        </div>
      </div>

      <!-- Progress Bar for Grid View -->
      <div v-if="viewMode === 'grid'" class="mt-2">
        <div class="w-full bg-gray-200 dark:bg-slate-700 rounded-full h-1">
          <div 
            class="h-1 rounded-full transition-all duration-500"
            :class="availabilityPercentage > 50 ? 'bg-green-500' : availabilityPercentage > 0 ? 'bg-amber-500' : 'bg-red-500'"
            :style="{ width: `${availabilityPercentage}%` }"
          ></div>
        </div>
      </div>

      <!-- Select Indicator -->
      <div v-if="!isSelected && isSelectable" class="mt-2 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        <span class="text-[10px] text-amber-600 dark:text-amber-400 font-medium">Click to select →</span>
      </div>
    </div>
  </div>
</template>