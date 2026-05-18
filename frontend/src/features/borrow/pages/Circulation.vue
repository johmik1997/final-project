<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import Table from '@/components/Table.vue';
import { useApiRequest } from '@/composables/useApiRequest';
import { openModal } from '@customizer/modal-x';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiSwapHorizontal, mdiPlus, mdiCheck, mdiMagnify } from '@mdi/js';
import { secondDateFormatWithTime, toasted } from '@/utils/utils';
import { getAllCirculation, returnCirculation } from '../api/circulationApi';
import { useCirculation } from '../store/circulationStore';
import AddCirculation from './AddCirculation.mdl.vue';
import { emitEntityMutation, subscribeEntityMutation } from '@/utils/entitySync';

const circStore = useCirculation();
const req = useApiRequest();
const returnReq = useApiRequest();
const searchQuery = ref('');
let unsubscribeEntitySync = () => {};

onMounted(() => {
  fetchCirculations();
  unsubscribeEntitySync = subscribeEntityMutation('circulations', () => {
    fetchCirculations();
  });
});

onBeforeUnmount(() => {
  unsubscribeEntitySync?.();
});

function fetchCirculations() {
  req.send(() => getAllCirculation({ size: 100 }), (res) => {
    if (res?.success) {
      circStore.set(res.data?.result || res.data?.results || res.data || []);
    }
  });
}

const filteredCirculations = computed(() => {
  const rows = circStore.circulations || [];
  const query = searchQuery.value.trim().toLowerCase();
  if (!query) return rows;

  return rows.filter((row) => {
    return [
      row?.material_title,
      row?.material_author,
      row?.member_name,
      row?.member_id,
      row?.status,
    ]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(query));
  });
});

const stats = computed(() => {
  const rows = circStore.circulations || [];
  return {
    total: rows.length,
    active: rows.filter((row) => row?.status === 'BORROWED').length,
    returned: rows.filter((row) => row?.status === 'RETURNED').length,
  };
});

function openAddCirculationModal() {
  openModal('AddCirculation', {}, () => {
    fetchCirculations();
  });
}

function handleReturn(row) {
  openModal(
    'Confirmation',
    {
      title: 'Return Circulation Material',
      message: 'Are you sure you want to mark this material as returned to the shelf?',
    },
    (confirm) => {
      if (!confirm) return;

      returnReq.send(
        () => returnCirculation(row.id),
        (res) => {
          if (res.success) {
            toasted(true, 'Material returned to shelf');
            fetchCirculations();
            emitEntityMutation('circulations', { action: 'updated', id: row.id, status: 'RETURNED' });
          } else {
            toasted(false, res.error || 'Failed to return material');
          }
        }
      );
    }
  );
}
</script>

<template>
  <div class="p-4 sm:p-7 space-y-6">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
      <div class="flex items-center gap-2">
        <BaseIcon :path="mdiSwapHorizontal" size="28" class="text-[color:var(--bw-text)]" />
        <div>
          <h1 class="text-2xl font-bold">On-Site Shelf Circulation</h1>
          <p class="text-xs text-zinc-500">In-library reading checkouts strictly for Shelf inventory</p>
        </div>
      </div>
      <button @click="openAddCirculationModal" class="bw-btn bw-btn-primary flex items-center gap-2">
        <BaseIcon :path="mdiPlus" size="18" />
        Log Shelf Circulation
      </button>
    </div>

    <!-- Quick Stats Grid -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bw-card p-5 space-y-1">
        <span class="text-xs font-bold text-zinc-400 uppercase tracking-wider">Total Shelf Circulations</span>
        <div class="text-3xl font-extrabold text-zinc-900 dark:text-zinc-100">{{ stats.total }}</div>
      </div>
      <div class="bw-card p-5 space-y-1">
        <span class="text-xs font-bold text-zinc-400 uppercase tracking-wider">Active Reading Now</span>
        <div class="text-3xl font-extrabold text-zinc-900 dark:text-zinc-100">{{ stats.active }}</div>
      </div>
      <div class="bw-card p-5 space-y-1">
        <span class="text-xs font-bold text-zinc-400 uppercase tracking-wider">Returned to Shelf</span>
        <div class="text-3xl font-extrabold text-zinc-900 dark:text-zinc-100">{{ stats.returned }}</div>
      </div>
    </div>

    <!-- Search box -->
    <div class="relative max-w-md">
      <BaseIcon :path="mdiMagnify" size="20" class="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400" />
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search shelf circulations..."
        class="w-full pl-12 pr-4 py-2.5 bw-input"
      />
    </div>

    <!-- Table -->
    <div class="bw-card overflow-hidden">
      <Table
        :pending="req.pending.value"
        :show-pagination="false"
        :rows="filteredCirculations"
        :headers="{
          head: ['Material', 'Member', 'Status', 'Logged At', 'Actions'],
          row: ['material_title', 'member_name', 'status', 'created_at']
        }"
        :cells="{
          created_at: (val) => secondDateFormatWithTime(val) || '-',
          status: (val) => {
            const map = {
              'BORROWED': '⚪ Reading In-Site',
              'RETURNED': '⚫ On Shelf',
            };
            return map[val] || val;
          }
        }"
      >
        <template #actions="{ row }">
          <div class="flex items-center gap-2">
            <template v-if="row.status === 'BORROWED'">
              <button class="bw-btn bw-btn-primary p-1.5 rounded-lg flex items-center gap-1.5 text-xs" 
                      @click="handleReturn(row)" title="Mark as Returned">
                <BaseIcon :path="mdiCheck" size="16" />
                Return to Shelf
              </button>
            </template>
            <span v-else class="text-xs text-zinc-500">None</span>
          </div>
        </template>
      </Table>
    </div>
  </div>
</template>
