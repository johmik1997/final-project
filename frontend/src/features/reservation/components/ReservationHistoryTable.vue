<script setup>
import { ref, computed } from 'vue';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { secondDateFormatWithTime, toasted } from '@/utils/utils';
import { mdiHistory, mdiClose, mdiPencil } from '@mdi/js';
import ApiService from '@/service/ApiService';
import { openModal } from '@customizer/modal-x';

const props = defineProps({
  rows: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['refresh']);

const userRole = computed(() => {
  const stored = JSON.parse(localStorage.getItem('userDetail') || '{}');
  const user = stored?.user || stored || {};
  return String(user?.roleName || user?.role || user?.userRole || '').toUpperCase();
});

const isStaff = computed(() => {
  return ['STACKSTAFF', 'TECHNICALSTAFF', 'FRONTDESKSTAFF', 'ADMIN', 'SUPERADMIN', 'STACK STAFF'].includes(userRole.value);
});

function cancelReservation(row) {
  const id = row?.id || row?.uuid;
  if (!id) return;
  
  openModal(
    'Confirmation',
    {
      title: 'Cancel Reservation',
      message: `Are you sure you want to cancel your reservation for "${row?.material_title || 'this material'}"?`,
    },
    (confirm) => {
      if (!confirm) return;
      
      const api = new ApiService();
      api.addAuthenticationHeader().delete(`/transactions/reservations/${id}/`).then(() => {
        toasted(true, 'Reservation cancelled successfully');
        emit('refresh');
      }).catch((err) => {
        toasted(false, err?.response?.data?.detail || 'Failed to cancel reservation');
      });
    }
  );
}

const showEditModal = ref(false);
const selectedRes = ref(null);
const newStatus = ref('');
const saving = ref(false);

function openEditModal(row) {
  selectedRes.value = row;
  newStatus.value = row.status || 'RESERVED';
  showEditModal.value = true;
}

function closeEditModal() {
  showEditModal.value = false;
  selectedRes.value = null;
}

async function saveStatus() {
  if (!selectedRes.value || !newStatus.value) return;
  saving.value = true;
  const id = selectedRes.value.id || selectedRes.value.uuid;
  
  try {
    const api = new ApiService();
    const res = await api.addAuthenticationHeader().patch(`/transactions/reservations/${id}/`, {
      status: newStatus.value
    });
    
    if (res?.success || res?.data) {
      toasted(true, 'Reservation status updated successfully');
      emit('refresh');
      closeEditModal();
    } else {
      toasted(false, 'Failed to update status', res?.error || 'Validation error');
    }
  } catch (err) {
    toasted(false, err?.response?.data?.detail || 'An error occurred while updating status');
  } finally {
    saving.value = false;
  }
}
</script>

<template>
  <div class="bg-white dark:bg-slate-800 rounded-2xl border border-gray-100 dark:border-slate-700 shadow-sm p-5 transition-colors duration-300">
    <div class="flex items-center gap-2 mb-4">
      <BaseIcon :path="mdiHistory" size="20" class="text-gray-700 dark:text-gray-300" />
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Reservation History</h2>
    </div>

    <div v-if="loading" class="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-900 rounded-lg p-4 flex items-center gap-3">
      <div class="animate-spin rounded-full h-5 w-5 border-2 border-blue-600 border-t-transparent"></div>
      <p class="text-sm text-blue-800 dark:text-blue-300">Loading reservations...</p>
    </div>

    <div v-else-if="rows.length === 0" class="bg-gray-50 dark:bg-slate-900 border border-gray-200 dark:border-slate-800 rounded-lg p-6 text-center text-sm text-gray-500 dark:text-gray-400">
      No reservation history found.
    </div>

    <div v-else class="overflow-x-auto rounded-lg border border-gray-200 dark:border-slate-700">
      <table class="min-w-full text-sm">
        <thead class="bg-gray-50 dark:bg-slate-900 border-b border-gray-200 dark:border-slate-700">
          <tr>
            <th class="text-left px-4 py-3 font-semibold text-gray-700 dark:text-gray-300">Material</th>
            <th class="text-left px-4 py-3 font-semibold text-gray-700 dark:text-gray-300">Author</th>
            <th class="text-left px-4 py-3 font-semibold text-gray-700 dark:text-gray-300">Reserved At</th>
            <th class="text-left px-4 py-3 font-semibold text-gray-700 dark:text-gray-300">Expires At</th>
            <th class="text-left px-4 py-3 font-semibold text-gray-700 dark:text-gray-300">Status</th>
            <th class="text-right px-4 py-3 font-semibold text-gray-700 dark:text-gray-300">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row?.id || row?.uuid" class="border-b border-gray-100 dark:border-slate-700 hover:bg-gray-50/50 dark:hover:bg-slate-900/50">
            <td class="px-4 py-3 font-medium text-gray-900 dark:text-white">{{ row?.material_title || row?.material?.title || '-' }}</td>
            <td class="px-4 py-3 text-gray-700 dark:text-gray-300">{{ row?.material_author || row?.material?.author || '-' }}</td>
            <td class="px-4 py-3 text-gray-700 dark:text-gray-300">{{ secondDateFormatWithTime(row?.reserve_date || row?.created_at) || '-' }}</td>
            <td class="px-4 py-3 text-gray-700 dark:text-gray-300">{{ secondDateFormatWithTime(row?.expiry_date) || '-' }}</td>
            <td class="px-4 py-3">
              <span class="text-xs px-2 py-1 rounded-full font-medium"
                    :class="row?.status === 'RESERVED' ? 'bg-blue-100 text-blue-700' : row?.status === 'CANCELLED' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-700'">
                {{ row?.status || '-' }}
              </span>
            </td>
            <td class="px-4 py-3 text-right">
              <div class="flex justify-end gap-2">
                <button
                  v-if="row?.status === 'RESERVED' && isStaff"
                  @click="openEditModal(row)"
                  class="text-xs bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 hover:bg-blue-600 hover:text-white px-2.5 py-1 rounded-lg transition-all duration-200"
                >
                  Edit Status
                </button>
                <button
                  v-if="row?.status === 'RESERVED'"
                  @click="cancelReservation(row)"
                  class="text-xs bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400 hover:bg-rose-600 hover:text-white px-2.5 py-1 rounded-lg transition-all duration-200"
                >
                  Cancel
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Edit Status Modal -->
    <div v-if="showEditModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fade-in">
      <div class="bg-white dark:bg-slate-800 rounded-2xl w-full max-w-md shadow-2xl border border-gray-100 dark:border-slate-700 overflow-hidden transform transition-all duration-300">
        <header class="px-6 py-4 border-b border-gray-100 dark:border-slate-700 flex justify-between items-center">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">Edit Reservation Status</h3>
          <button @click="closeEditModal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
            <BaseIcon :path="mdiClose" size="18" />
          </button>
        </header>
        
        <div class="p-6">
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Update reservation status for: <strong class="text-gray-950 dark:text-white">"{{ selectedRes?.material_title }}"</strong>
          </p>
          
          <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Status</label>
          <select
            v-model="newStatus"
            class="w-full px-4 py-2.5 border border-gray-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-amber-400 bg-white dark:bg-slate-800 text-gray-900 dark:text-gray-100"
          >
            <option value="RESERVED">RESERVED</option>
            <option value="EXPIRED">EXPIRED</option>
            <option value="CANCELLED">CANCELLED</option>
          </select>
        </div>
        
        <footer class="px-6 py-4 bg-gray-50 dark:bg-slate-900 border-t border-gray-100 dark:border-slate-700 flex justify-end gap-3">
          <button @click="closeEditModal" class="px-4 py-2 rounded-xl text-sm font-semibold border border-gray-200 dark:border-slate-700 text-gray-500 hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors" :disabled="saving">Cancel</button>
          <button @click="saveStatus" class="px-4 py-2 rounded-xl text-sm font-semibold bg-amber-500 hover:bg-amber-600 text-white shadow-md hover:shadow-lg transition-all" :disabled="saving">
            {{ saving ? 'Saving...' : 'Save Changes' }}
          </button>
        </footer>
      </div>
    </div>
  </div>
</template>
