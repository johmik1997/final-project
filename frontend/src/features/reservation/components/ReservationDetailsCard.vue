<script setup>
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiCheckCircle, mdiAccount, mdiBook } from '@mdi/js';

const props = defineProps({
  selectedMaterial: {
    type: Object,
    default: null,
  },
  reserveDate: {
    type: String,
    default: '',
  },
  submitting: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['update:reserveDate', 'submit', 'change-material']);
</script>

<template>
  <div class="bg-white dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-700 shadow-sm p-5 transition-colors">
    <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">Reservation Details</h2>

    <div
      v-if="!selectedMaterial"
      class="text-sm text-gray-500 dark:text-slate-400 bg-gray-50 dark:bg-slate-900/50 border border-gray-200 dark:border-slate-700 rounded-lg p-4"
    >
      Select a material first to continue.
    </div>

    <div v-else class="space-y-4">
      <div class="bg-gray-50 dark:bg-slate-900/50 rounded-lg p-4 border border-gray-200 dark:border-slate-700">
        <p class="font-medium text-gray-900 dark:text-white flex items-center gap-1">
          <BaseIcon :path="mdiBook" size="14" />
          {{ selectedMaterial.title }}
        </p>
        <p class="text-xs text-gray-500 dark:text-slate-400 flex items-center gap-1 mt-1">
          <BaseIcon :path="mdiAccount" size="12" />
          {{ selectedMaterial.author || '-' }}
        </p>
        <p class="text-xs text-gray-600 dark:text-slate-300 mt-2">Available copies: {{ selectedMaterial.available_copies || 0 }}</p>
      </div>

      <button
        type="button"
        class="w-full py-2.5 rounded-lg bg-primary text-white hover:bg-primary/90 disabled:opacity-60"
        :disabled="submitting"
        @click="emit('submit')"
      >
        <span class="inline-flex items-center gap-2">
          <BaseIcon :path="mdiCheckCircle" size="16" />
          {{ submitting ? 'Reserving...' : 'Reserve' }}
        </span>
      </button>

      <button
        type="button"
        class="w-full py-2.5 rounded-lg border border-gray-200 dark:border-slate-600 text-gray-700 dark:text-slate-300 hover:bg-gray-50 dark:hover:bg-slate-800"
        @click="emit('change-material')"
      >
        Change Material
      </button>
    </div>
  </div>
</template>
