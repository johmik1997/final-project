<script setup>
import BaseIcon from '@/components/base/BaseIcon.vue';
import { secondDateFormatWithTime } from '@/utils/utils';
import { mdiHistory } from '@mdi/js';

defineProps({
  rows: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
});
</script>

<template>
  <div class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
    <div class="flex items-center gap-2 mb-4">
      <BaseIcon :path="mdiHistory" size="20" class="text-gray-700" />
      <h2 class="text-lg font-semibold text-gray-900">My Reservation History</h2>
    </div>

    <div v-if="loading" class="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-center gap-3">
      <div class="animate-spin rounded-full h-5 w-5 border-2 border-blue-600 border-t-transparent"></div>
      <p class="text-sm text-blue-800">Loading your reservations...</p>
    </div>

    <div v-else-if="rows.length === 0" class="bg-gray-50 border border-gray-200 rounded-lg p-6 text-center text-sm text-gray-500">
      No reservation history yet.
    </div>

    <div v-else class="overflow-x-auto rounded-lg border border-gray-200">
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50 border-b border-gray-200">
          <tr>
            <th class="text-left px-4 py-3 font-semibold text-gray-700">Material</th>
            <th class="text-left px-4 py-3 font-semibold text-gray-700">Author</th>
            <th class="text-left px-4 py-3 font-semibold text-gray-700">Reserved At</th>
            <th class="text-left px-4 py-3 font-semibold text-gray-700">Expires At</th>
            <th class="text-left px-4 py-3 font-semibold text-gray-700">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row?.id || row?.uuid" class="border-b border-gray-100">
            <td class="px-4 py-3 font-medium text-gray-900">{{ row?.material_title || row?.material?.title || '-' }}</td>
            <td class="px-4 py-3 text-gray-700">{{ row?.material_author || row?.material?.author || '-' }}</td>
            <td class="px-4 py-3 text-gray-700">{{ secondDateFormatWithTime(row?.reserve_date || row?.created_at) || '-' }}</td>
            <td class="px-4 py-3 text-gray-700">{{ secondDateFormatWithTime(row?.expiry_date) || '-' }}</td>
            <td class="px-4 py-3">
              <span class="text-xs px-2 py-1 rounded-full font-medium"
                    :class="row?.status === 'RESERVED' ? 'bg-blue-100 text-blue-700' : row?.status === 'CANCELLED' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'">
                {{ row?.status || '-' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
