<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useApiRequest } from '@/composables/useApiRequest';
import { secondDateFormatWithTime } from '@/utils/utils';
import Table from '@/components/Table.vue';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiBookshelf, mdiMagnify } from '@mdi/js';
import { getAllCirculation } from '@/features/borrow/api/circulationApi';
import { subscribeEntityMutation } from '@/utils/entitySync';

const circulationReq = useApiRequest();
const searchQuery = ref('');
let unsubscribeEntitySync = () => {};

function rowsFromPayload(payload) {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.content)) return payload.content;
  if (Array.isArray(payload?.response)) return payload.response;
  if (Array.isArray(payload?.data)) return payload.data;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.result)) return payload.result;
  if (payload?.id) return [payload];
  return [];
}

function normalizeStatus(value) {
  return String(value || '').trim().toUpperCase();
}

const allCirculations = computed(() => rowsFromPayload(circulationReq.response.value));

const filteredCirculations = computed(() => {
  const rows = allCirculations.value || [];
  const query = searchQuery.value.trim().toLowerCase();
  if (!query) return rows;

  return rows.filter((row) =>
    [
      row?.material_title,
      row?.material_author,
      row?.library_name,
      row?.status,
      row?.created_at,
      row?.updated_at,
    ]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(query))
  );
});

const stats = computed(() => {
  const rows = allCirculations.value || [];
  return {
    total: rows.length,
    active: rows.filter((row) => normalizeStatus(row?.status) === 'BORROWED').length,
    returned: rows.filter((row) => normalizeStatus(row?.status) === 'RETURNED').length,
  };
});

function loadCirculations() {
  circulationReq.send(() => getAllCirculation({ page: 1, size: 200 }));
}

onMounted(() => {
  loadCirculations();
  unsubscribeEntitySync = subscribeEntityMutation('circulations', () => {
    loadCirculations();
  });
});

onBeforeUnmount(() => {
  unsubscribeEntitySync?.();
});
</script>

<template>
  <div class="p-4 sm:p-7">
    <div class="mb-6 bg-white dark:bg-slate-800/50 rounded-2xl border border-gray-100 dark:border-slate-700 shadow-sm p-5 transition-colors">
      <div class="flex flex-col lg:flex-row justify-between lg:items-center gap-4">
        <div>
          <h1 class="text-2xl font-bold flex items-center gap-2 text-gray-900 dark:text-white">
            <BaseIcon :path="mdiBookshelf" size="28" class="text-amber-600 dark:text-amber-400" />
            My Circulations
          </h1>
          <p class="text-sm text-gray-500 dark:text-slate-400 mt-1">
            Track your in-library shelf reading records and their latest status.
          </p>
        </div>

        <div class="flex flex-wrap gap-3 text-sm text-gray-600 dark:text-slate-300">
          <span class="px-3 py-1 rounded-full bg-gray-100 dark:bg-slate-700 dark:text-slate-200">Total: {{ stats.total }}</span>
          <span class="px-3 py-1 rounded-full bg-amber-100 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300">Active: {{ stats.active }}</span>
          <span class="px-3 py-1 rounded-full bg-emerald-100 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300">Returned: {{ stats.returned }}</span>
        </div>
      </div>

      <div class="mt-4 relative">
        <BaseIcon
          :path="mdiMagnify"
          size="18"
          class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-slate-500"
        />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by material, branch, status, or date..."
          class="w-full pl-10 pr-4 py-2.5 border border-gray-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-primary-200 dark:focus:ring-amber-500/20 focus:border-primary-400 dark:focus:border-amber-500"
        />
      </div>
    </div>

    <div class="hidden lg:block bg-white dark:bg-slate-800/50 rounded-lg shadow-sm border border-gray-100 dark:border-slate-700 overflow-hidden transition-colors">
      <Table
        :pending="circulationReq.pending.value"
        :rows="filteredCirculations"
        :show-pagination="false"
        :headers="{
          head: ['Material', 'Author', 'Library', 'Logged At', 'Last Updated', 'Status'],
          row: ['material_title', 'material_author', 'library_name', 'created_at', 'updated_at', 'status'],
        }"
        :cells="{
          created_at: (val) => secondDateFormatWithTime(val) || '-',
          updated_at: (val) => secondDateFormatWithTime(val) || '-',
        }"
      />
    </div>

    <div class="block lg:hidden">
      <div v-if="circulationReq.pending.value" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div
          v-for="num in 4"
          :key="`circulation-skeleton-${num}`"
          class="bg-white dark:bg-slate-800/50 rounded-xl border border-gray-100 dark:border-slate-700 shadow-sm p-4 animate-pulse"
        >
          <div class="h-4 bg-gray-200 dark:bg-slate-600 rounded w-3/4 mb-3"></div>
          <div class="h-3 bg-gray-200 dark:bg-slate-600 rounded w-1/2 mb-2"></div>
          <div class="h-3 bg-gray-200 dark:bg-slate-600 rounded w-2/3 mb-2"></div>
          <div class="h-3 bg-gray-200 dark:bg-slate-600 rounded w-1/3"></div>
        </div>
      </div>

      <div v-else-if="filteredCirculations.length" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div
          v-for="row in filteredCirculations"
          :key="row?.id || row?.uuid"
          class="bg-white dark:bg-slate-800/50 rounded-xl border border-gray-100 dark:border-slate-700 shadow-sm p-4 space-y-3 transition-colors"
        >
          <div>
            <h3 class="text-base font-semibold text-gray-900 dark:text-white">{{ row?.material_title || 'Untitled Material' }}</h3>
            <p class="text-sm text-gray-500 dark:text-slate-400">{{ row?.material_author || 'Unknown Author' }}</p>
          </div>

          <div class="text-sm text-gray-600 dark:text-slate-300 space-y-1">
            <div class="flex justify-between gap-2">
              <span class="text-gray-500 dark:text-slate-400">Library</span>
              <span class="font-medium">{{ row?.library_name || '-' }}</span>
            </div>
            <div class="flex justify-between gap-2">
              <span class="text-gray-500 dark:text-slate-400">Logged</span>
              <span class="font-medium">{{ secondDateFormatWithTime(row?.created_at) || '-' }}</span>
            </div>
            <div class="flex justify-between gap-2">
              <span class="text-gray-500 dark:text-slate-400">Updated</span>
              <span class="font-medium">{{ secondDateFormatWithTime(row?.updated_at) || '-' }}</span>
            </div>
          </div>

          <div class="flex items-center justify-between">
            <span class="text-xs text-gray-500 dark:text-slate-400">Status</span>
            <span
              class="text-xs font-semibold px-2.5 py-1 rounded-full"
              :class="
                normalizeStatus(row?.status) === 'BORROWED'
                  ? 'bg-amber-100 dark:bg-amber-950/50 text-amber-700 dark:text-amber-300'
                  : 'bg-emerald-100 dark:bg-emerald-950/50 text-emerald-700 dark:text-emerald-300'
              "
            >
              {{ row?.status || 'UNKNOWN' }}
            </span>
          </div>
        </div>
      </div>

      <div
        v-else
        class="bg-white dark:bg-slate-800/50 rounded-xl border border-gray-100 dark:border-slate-700 shadow-sm p-6 text-center text-sm text-gray-500 dark:text-slate-400"
      >
        No circulation records found.
      </div>
    </div>
  </div>
</template>
