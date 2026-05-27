<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import { useApiRequest } from '@/composables/useApiRequest';
import Table from '@/components/Table.vue';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiCheckCircle, mdiCloseCircle, mdiPlus } from '@mdi/js';
import { secondDateFormatWithTime, toasted } from '@/utils/utils';
import { getAllTransferRequests, createTransferRequest, fulfillTransferRequest, cancelTransferRequest } from '../api/transferApi';
import { useAuth } from '@/stores/auth';
import { getAllMaterials } from '@/features/material/api/materialApi';

const auth = useAuth();
const transferReq = useApiRequest();
const fulfillReq = useApiRequest();
const cancelReq = useApiRequest();
const createReq = useApiRequest();
const materialsReq = useApiRequest();

const showAddModal = ref(false);
const selectedMaterial = ref('');
const selectedDirection = ref('');

const currentRole = computed(() => {
  const role = auth?.auth?.user?.role || auth?.auth?.user?.roleName || '';
  return role.replace(/^ROLE_/, '').toUpperCase();
});

const isFrontDesk = computed(() => {
  const r = String(currentRole.value || '').replace(/\s+/g, '').toUpperCase();
  return r === 'FRONTDESKSTAFF' || r === 'ADMIN' || r === 'SUPERADMIN';
});
const isStackStaff = computed(() => {
  const r = String(currentRole.value || '').replace(/\s+/g, '').toUpperCase();
  return r === 'STACKSTAFF' || r === 'ADMIN' || r === 'SUPERADMIN';
});
const isAdminLike = computed(() => {
  const r = String(currentRole.value || '').replace(/\s+/g, '').toUpperCase();
  return r === 'ADMIN' || r === 'SUPERADMIN';
});
const canRequestStackToShelf = computed(() => isFrontDesk.value);
const canRequestShelfToStack = computed(() => isStackStaff.value);
const canCreateRequests = computed(() => canRequestStackToShelf.value || canRequestShelfToStack.value);
const directionOptions = computed(() => {
  const options = [];
  if (canRequestStackToShelf.value) {
    options.push({ value: 'STACK_TO_SHELF', label: 'Stack to Shelf' });
  }
  if (canRequestShelfToStack.value) {
    options.push({ value: 'SHELF_TO_STACK', label: 'Shelf to Stack' });
  }
  return options;
});
const sourceLocation = computed(() => (selectedDirection.value === 'SHELF_TO_STACK' ? 'SHELF' : 'STACK'));
const destinationLocation = computed(() => (sourceLocation.value === 'STACK' ? 'SHELF' : 'STACK'));
const routeLabel = computed(() => `${sourceLocation.value} -> ${destinationLocation.value}`);

const rows = computed(() => {
const response = transferReq.response.value;

const data =
response?.data?.result ||
response?.data?.results ||
response?.result ||
response?.results ||
[];

return Array.isArray(data) ? data : [];
});

const materials = computed(() => {
  const response = materialsReq.response.value;

  return (
    response?.data?.result ||
    response?.data?.results ||
    response?.result ||
    response?.results ||
    response ||
    []
  );
});

function loadPage() {
  transferReq.send(() => getAllTransferRequests({ page: 1, size: 200 }));
}

function loadMaterials() {
  if (canCreateRequests.value) {
    materialsReq.send(() => getAllMaterials({ page: 1, size: 500, location: sourceLocation.value }, 'physical'));
  }
}
const requestedQuantity = ref(1);

onMounted(() => {
  if (!selectedDirection.value && directionOptions.value.length) {
    selectedDirection.value = directionOptions.value[0].value;
  }
  loadPage();
});

watch(directionOptions, (options) => {
  if (!options.length) {
    selectedDirection.value = '';
    return;
  }
  if (!options.some((option) => option.value === selectedDirection.value)) {
    selectedDirection.value = options[0].value;
  }
}, { immediate: true });

watch(selectedDirection, () => {
  selectedMaterial.value = '';
  if (showAddModal.value) {
    loadMaterials();
  }
});

function formatRoute(row) {
  return `${row?.source_location || 'STACK'} -> ${row?.destination_location || 'SHELF'}`;
}

function canFulfill(row) {
  if (isAdminLike.value) return true;
  if (row?.source_location === 'STACK' && row?.destination_location === 'SHELF') {
    return isStackStaff.value;
  }
  if (row?.source_location === 'SHELF' && row?.destination_location === 'STACK') {
    return isFrontDesk.value;
  }
  return false;
}

function canCancel(row) {
  if (isAdminLike.value) return true;
  const requesterId = row?.requested_by || row?.requested_by_id;
  const currentUserId = auth?.auth?.user?.id;
  if (requesterId && currentUserId && String(requesterId) === String(currentUserId)) {
    return true;
  }
  return canFulfill(row);
}

function openCreateRequestModal() {
  showAddModal.value = true;
  if (!selectedDirection.value && directionOptions.value.length) {
    selectedDirection.value = directionOptions.value[0].value;
  }
  loadMaterials();
}

function handleFulfill(row) {
  fulfillReq.send(
    () => fulfillTransferRequest(row.id),
    (res) => {
      if (res.success) {
        toasted(true, 'Transfer request fulfilled.');
        loadPage();
      } else {
        toasted(false, 'Failed to fulfill', res.error);
      }
    }
  );
}

function handleCancel(row) {
  cancelReq.send(
    () => cancelTransferRequest(row.id),
    (res) => {
      if (res.success) {
        toasted(true, 'Transfer request cancelled.');
        loadPage();
      } else {
        toasted(false, 'Failed to cancel', res.error);
      }
    }
  );
}

function submitRequest() {
  if (!selectedMaterial.value) {
    toasted(false, 'Please select a material');
    return;
  }
  createReq.send(
    () =>
      createTransferRequest({
        material: selectedMaterial.value,
        requested_quantity: requestedQuantity.value,
        source_location: sourceLocation.value,
        destination_location: destinationLocation.value,
      }),
    (res) => {
      if (res.success) {
        toasted(true, 'Transfer request created.');
        showAddModal.value = false;
        selectedMaterial.value = '';
        requestedQuantity.value = 1;
        loadPage();
      } else {
        toasted(false, 'Failed to create request', res.error);
      }
    }
  );
}
</script>

<template>
  <div class="p-4 sm:p-7">
    <div class="flex justify-between items-center mb-6">
      <div>
        <h1 class="text-2xl font-bold text-slate-900 dark:text-white">Material Transfer Requests</h1>
        <p class="text-sm text-slate-500 dark:text-slate-400">Manage both stack-to-shelf and shelf-to-stack transfer requests.</p>
      </div>
      <button
        v-if="canCreateRequests"
        @click="openCreateRequestModal"
        class="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 transition"
      >
        <BaseIcon :path="mdiPlus" size="18" />
        New Request
      </button>
    </div>

    <div class="bg-white dark:bg-slate-900 rounded-xl border border-gray-200 dark:border-slate-800 p-4 shadow-sm">
      <Table
        :pending="transferReq.pending.value"
        :rows="rows"
        :show-pagination="false"
        :headers="{
          head: ['Material', 'Route', 'Status', 'Requested By', 'Fulfilled By', 'Created At', 'Completed At', 'Actions'],
          row: ['material_title', 'route', 'status', 'requested_by_name', 'fulfilled_by_name', 'created_at', 'completed_at']
        }"
        :cells="{
          route: (_, row) => formatRoute(row),
          created_at: (val) => secondDateFormatWithTime(val) || '-',
          completed_at: (val) => secondDateFormatWithTime(val) || '-'
        }"
      >
        <template #actions="{ row }">
          <div v-if="row.status === 'PENDING' && (canFulfill(row) || canCancel(row))" class="flex gap-2">
            <button
              v-if="canFulfill(row)"
              class="bg-emerald-50 text-emerald-600 hover:bg-emerald-600 hover:text-white px-3 py-1 rounded-lg flex items-center gap-1 transition text-sm"
              @click="handleFulfill(row)"
              :disabled="fulfillReq.pending.value"
            >
              <BaseIcon :path="mdiCheckCircle" size="14" />
              Fulfill
            </button>
            <button
              v-if="canCancel(row)"
              class="bg-red-50 text-red-600 hover:bg-red-600 hover:text-white px-3 py-1 rounded-lg flex items-center gap-1 transition text-sm"
              @click="handleCancel(row)"
              :disabled="cancelReq.pending.value"
            >
              <BaseIcon :path="mdiCloseCircle" size="14" />
              Cancel
            </button>
          </div>
          <span v-else class="text-xs text-gray-400">No actions</span>
        </template>
      </Table>
    </div>

    <!-- Add Modal -->
    <div v-if="showAddModal" class="fixed inset-0 bg-black/60 flex items-center justify-center z-50 px-4">
      <div class="bg-white dark:bg-slate-800 rounded-xl p-6 w-full max-w-md shadow-xl border border-gray-200 dark:border-slate-700">
        <h2 class="text-xl font-bold mb-4 text-slate-900 dark:text-white">Create Transfer Request</h2>
        <div v-if="directionOptions.length > 1" class="mb-4">
          <label class="block text-sm font-medium mb-1 text-slate-700 dark:text-slate-300">Transfer Direction</label>
          <select
            v-model="selectedDirection"
            class="w-full border border-gray-300 dark:border-slate-600 rounded-lg p-2.5 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500"
          >
            <option v-for="option in directionOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>
        <div v-else class="mb-4 rounded-lg border border-blue-200 bg-blue-50 px-3 py-2 text-sm text-blue-700 dark:border-blue-900/60 dark:bg-blue-950/30 dark:text-blue-300">
          Route: {{ routeLabel }}
        </div>
        <div class="mb-4">
          <label class="block text-sm font-medium mb-1 text-slate-700 dark:text-slate-300">Select Material ({{ sourceLocation }})</label>
          <select 
            v-model="selectedMaterial" 
            class="w-full border border-gray-300 dark:border-slate-600 rounded-lg p-2.5 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500"
          >
            <option value="" disabled>Select a material...</option>
            <option v-for="mat in materials" :key="mat.id" :value="mat.id">
              {{ mat.title }} ({{ mat.available_copies }} available)
            </option>
          </select>
          <p v-if="materialsReq.pending.value" class="text-xs text-blue-500 mt-1">Loading materials...</p>
        </div>
          <div class="mb-4">
            <label class="block text-sm font-medium mb-1 text-slate-700 dark:text-slate-300">Requested Quantity</label>
            <input 
              type="number" 
              v-model.number="requestedQuantity" 
              min="1"
              class="w-full border border-gray-300 dark:border-slate-600 rounded-lg p-2.5 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:ring-2 focus:ring-blue-500"
            />
        </div>
        <div class="flex justify-end gap-3 mt-6">
          <button 
            @click="showAddModal = false"
            class="px-4 py-2 border border-gray-300 dark:border-slate-600 rounded-lg text-slate-700 dark:text-slate-300 hover:bg-gray-50 dark:hover:bg-slate-700 transition"
          >
            Cancel
          </button>
          <button 
            @click="submitRequest"
            :disabled="createReq.pending.value || !selectedMaterial || !selectedDirection"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50"
          >
            {{ createReq.pending.value ? 'Creating...' : 'Submit Request' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
