<script setup>
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiCalendar, mdiCheckCircle, mdiAccount, mdiBook } from '@mdi/js';

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
  <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
    <h2 class="text-lg font-semibold text-gray-900 mb-4">Reservation Details</h2>

    <div v-if="!selectedMaterial" class="text-sm text-gray-500 bg-gray-50 border border-gray-200 rounded-lg p-4">
      Select a material first to continue.
    </div>

    <div v-else class="space-y-4">
      <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
        <p class="font-medium text-gray-900 flex items-center gap-1">
          <BaseIcon :path="mdiBook" size="14" />
          {{ selectedMaterial.title }}
        </p>
        <p class="text-xs text-gray-500 flex items-center gap-1 mt-1">
          <BaseIcon :path="mdiAccount" size="12" />
          {{ selectedMaterial.author || '-' }}
        </p>
        <p class="text-xs text-gray-600 mt-2">Available copies: {{ selectedMaterial.available_copies || 0 }}</p>
      </div>

      <label class="block text-sm font-medium text-gray-700">Reservation Date</label>
      <div class="relative">
        <BaseIcon :path="mdiCalendar" size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
        <input
          :value="reserveDate"
          type="date"
          class="w-full pl-10 pr-3 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400"
          @input="emit('update:reserveDate', $event.target.value)"
        />
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
        class="w-full py-2.5 rounded-lg border border-gray-200 text-gray-700 hover:bg-gray-50"
        @click="emit('change-material')"
      >
        Change Material
      </button>
    </div>
  </div>
</template>
