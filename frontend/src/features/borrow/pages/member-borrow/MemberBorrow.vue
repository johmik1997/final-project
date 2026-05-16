<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useApiRequest } from '@/composables/useApiRequest';
import { secondDateFormatWithTime } from '@/utils/utils';
import Table from '@/components/Table.vue';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiBookmarkMultiple, mdiMagnify } from '@mdi/js';
import { getMyBorrows } from '@/features/borrow/api/borrowApi';
import { subscribeEntityMutation } from '@/utils/entitySync';
const borrowsReq = useApiRequest();
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

function formatDaysLeft(value) {
  if (!value) return '-';
  const due = new Date(value);
  if (Number.isNaN(due.getTime())) return '-';
  const today = new Date();
  const ms = due.getTime() - today.getTime();
  const days = Math.ceil(ms / (1000 * 60 * 60 * 24));
  if (days < 0) return `Overdue by ${Math.abs(days)} day${Math.abs(days) === 1 ? '' : 's'}`;
  if (days === 0) return 'Due today';
  return `${days} day${days === 1 ? '' : 's'} left`;
}

const allBorrows = computed(() => rowsFromPayload(borrowsReq.response.value));

const myBorrows = computed(() => allBorrows.value);

const filteredBorrows = computed(() => {
  const rows = myBorrows.value || [];
  const query = searchQuery.value.trim().toLowerCase();
  if (!query) return rows;

  return rows.filter((row) => {
    return [
      row?.material_title,
      row?.material_author,
      row?.status,
      row?.borrow_date,
      row?.due_date,
    ]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(query));
  });
});

const stats = computed(() => {
  const rows = myBorrows.value || [];
  return {
    total: rows.length,
    borrowed: rows.filter((row) => normalizeStatus(row?.status) === 'BORROWED').length,
    overdue: rows.filter((row) => normalizeStatus(row?.status) === 'OVERDUE').length,
    returned: rows.filter((row) => ['RETURNED', 'COMPLETED'].includes(normalizeStatus(row?.status))).length,
  };
});

function loadBorrows() {
  borrowsReq.send(() => getMyBorrows({ page: 1, size: 200 }));
}

onMounted(() => {
  loadBorrows();
  unsubscribeEntitySync = subscribeEntityMutation('borrows', () => {
    loadBorrows();
  });
});

onBeforeUnmount(() => {
  unsubscribeEntitySync?.();
});
</script>

<template>
  <div class="p-4 sm:p-7">
    <div class="mb-6 bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
      <div class="flex flex-col lg:flex-row justify-between lg:items-center gap-4">
        <div>
          <h1 class="text-2xl font-bold flex items-center gap-2">
            <BaseIcon :path="mdiBookmarkMultiple" size="28" />
            My Borrowed Materials
          </h1>
          <p class="text-sm text-gray-500 mt-1">
            Track your borrowed items, due dates, and status
          </p>
        </div>

        <div class="flex flex-wrap gap-3 text-sm text-gray-600">
          <span class="px-3 py-1 rounded-full bg-gray-100">Total: {{ stats.total }}</span>
          <span class="px-3 py-1 rounded-full bg-amber-100 text-amber-700">Borrowed: {{ stats.borrowed }}</span>
          <span class="px-3 py-1 rounded-full bg-red-100 text-red-700">Overdue: {{ stats.overdue }}</span>
          <span class="px-3 py-1 rounded-full bg-emerald-100 text-emerald-700">Returned: {{ stats.returned }}</span>
        </div>
      </div>

      <div class="mt-4 relative">
        <BaseIcon
          :path="mdiMagnify"
          size="18"
          class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
        />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by title, author, status, or date..."
          class="w-full pl-10 pr-4 py-2.5 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-200 focus:border-primary-400"
        />
      </div>
    </div>

    <!-- Mobile Cards -->
    <div class="block lg:hidden">
      <div v-if="borrowsReq.pending.value" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div v-for="num in 4" :key="`borrow-skeleton-${num}`" class="bg-white rounded-xl border border-gray-100 shadow-sm p-4 animate-pulse">
          <div class="h-4 bg-gray-200 rounded w-3/4 mb-3"></div>
          <div class="h-3 bg-gray-200 rounded w-1/2 mb-2"></div>
          <div class="h-3 bg-gray-200 rounded w-2/3 mb-2"></div>
          <div class="h-3 bg-gray-200 rounded w-1/3"></div>
        </div>
      </div>

      <div v-else-if="filteredBorrows.length" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div
          v-for="row in filteredBorrows"
          :key="row?.id || row?.uuid"
          class="bg-white rounded-xl border border-gray-100 shadow-sm p-4 space-y-3"
        >
          <div>
            <h3 class="text-base font-semibold text-gray-900">{{ row?.material_title || 'Untitled Material' }}</h3>
            <p class="text-sm text-gray-500">{{ row?.material_author || 'Unknown Author' }}</p>
          </div>

          <div class="text-sm text-gray-600 space-y-1">
            <div class="flex justify-between gap-2">
              <span class="text-gray-500">Borrowed</span>
              <span class="font-medium">{{ secondDateFormatWithTime(row?.borrow_date) || '-' }}</span>
            </div>
            <div class="flex justify-between gap-2">
              <span class="text-gray-500">Due</span>
              <span class="font-medium">{{ secondDateFormatWithTime(row?.due_date) || '-' }}</span>
            </div>
            <div class="flex justify-between gap-2">
              <span class="text-gray-500">Days Left</span>
              <span class="font-medium">{{ formatDaysLeft(row?.due_date) }}</span>
            </div>
          </div>

          <div class="flex items-center justify-between">
            <span class="text-xs text-gray-500">Status</span>
            <span
              class="text-xs font-semibold px-2.5 py-1 rounded-full"
              :class="
                normalizeStatus(row?.status) === 'OVERDUE'
                  ? 'bg-red-100 text-red-700'
                  : normalizeStatus(row?.status) === 'BORROWED'
                    ? 'bg-amber-100 text-amber-700'
                    : 'bg-emerald-100 text-emerald-700'
              "
            >
              {{ row?.status || 'UNKNOWN' }}
            </span>
          </div>
        </div>
      </div>

      <div v-else class="bg-white rounded-xl border border-gray-100 shadow-sm p-6 text-center text-sm text-gray-500">
        No borrowed materials found.
      </div>
    </div>

    <!-- Desktop Table -->
    <div class="hidden lg:block bg-white rounded-lg shadow-sm border border-gray-100 overflow-hidden">
      <Table
        :pending="borrowsReq.pending.value"
        :rows="filteredBorrows"
        :show-pagination="false"
        :headers="{
          head: [
            'Material',
            'Author',
            'Borrowed At',
            'Due Date',
            'Days Left',
            'Status',
          ],
          row: [
            'material_title',
            'material_author',
            'borrow_date',
            'due_date',
            'days_left',
            'status',
          ],
        }"
        :cells="{
          borrow_date: (val) => secondDateFormatWithTime(val) || '-',
          due_date: (val) => secondDateFormatWithTime(val) || '-',
          days_left: (_, row) => formatDaysLeft(row?.due_date),
        }"
      />
    </div>
  </div>
</template>
