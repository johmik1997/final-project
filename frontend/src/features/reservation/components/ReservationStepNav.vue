<script setup>
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiCheckCircle } from '@mdi/js';

defineProps({
  hasSelection: {
    type: Boolean,
    default: false,
  },
  hasDate: {
    type: Boolean,
    default: false,
  },
});
</script>

<template>
  <div class="bg-white border border-gray-200 rounded-xl p-4">
    <div class="grid grid-cols-3 gap-2">
      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold bg-blue-600 text-white">
          1
        </div>
        <span class="text-sm font-medium text-gray-900">Select Material</span>
      </div>

      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold"
             :class="hasSelection ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'">
          2
        </div>
        <span class="text-sm font-medium" :class="hasSelection ? 'text-gray-900' : 'text-gray-500'">Pick Date</span>
      </div>

      <div class="flex items-center gap-2">
        <div class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold"
             :class="hasSelection && hasDate ? 'bg-green-600 text-white' : 'bg-gray-200 text-gray-600'">
          <BaseIcon v-if="hasSelection && hasDate" :path="mdiCheckCircle" size="14" />
          <span v-else>3</span>
        </div>
        <span class="text-sm font-medium" :class="hasSelection && hasDate ? 'text-green-700' : 'text-gray-500'">Reserve</span>
      </div>
    </div>
  </div>
</template>
