<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import Table from '@/components/Table.vue';
import { useApiRequest } from '@/composables/useApiRequest';
import { usePaginations } from '@/composables/usePaginationTemp';
import { useRouter } from 'vue-router';
import { openModal } from '@customizer/modal-x';
import ApiService from '@/service/ApiService';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiBookmark, mdiCloseCircle, mdiMagnify, mdiPencil, mdiDeleteAlert, mdiClose } from '@mdi/js';
import { secondDateFormatWithTime, toasted } from '@/utils/utils';
import { getAllBorrows, updateBorrowById } from '../api/borrowApi';
import { useBorrow } from '../store/borrowStore';
import BorrowHeader from '../components/BorrowHeader.vue';
import { emitEntityMutation, subscribeEntityMutation } from '@/utils/entitySync';

const borrowStore = useBorrow();
const cancelReq = useApiRequest();
const router = useRouter();
const searchQuery = ref('');
let unsubscribeEntitySync = () => {};

const pagination = usePaginations({
  store: borrowStore,
  cb: getAllBorrows,
});

onMounted(() => {
  unsubscribeEntitySync = subscribeEntityMutation('borrows', () => {
    pagination.refresh();
  });
});

onBeforeUnmount(() => {
  unsubscribeEntitySync?.();
});

const filteredBorrows = computed(() => {
  const rows = borrowStore.borrows || [];
  const query = searchQuery.value.trim().toLowerCase();
  if (!query) return rows;

  return rows.filter((row) => {
    return [
      row?.material_title,
      row?.material_author,
      row?.member_name,
      row?.member_id_number,
      row?.status,
    ]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(query));
  });
});

const headerStats = computed(() => {
  const rows = borrowStore.borrows || [];
  return {
    total: rows.length,
    available: rows.filter((row) => row?.status === 'RETURNED' || row?.status === 'COMPLETED').length,
    borrowed: rows.filter((row) => row?.status === 'BORROWED' || row?.status === 'RESERVED').length,
    categories: new Set(
      rows
        .map((row) => row?.material_category || row?.category)
        .filter(Boolean)
    ).size,
  };
});

function getBorrowId(row) {
  return row?.id || row?.borrowUuid || row?.uuid;
}

const showEditModal = ref(false);
const selectedBorrow = ref(null);
const newStatus = ref('');
const savingStatus = ref(false);

function openEditStatusModal(row) {
  selectedBorrow.value = row;
  newStatus.value = row.status || 'BORROWED';
  showEditModal.value = true;
}

function closeEditModal() {
  showEditModal.value = false;
  selectedBorrow.value = null;
}

async function saveStatusUpdate() {
  if (!selectedBorrow.value || !newStatus.value) return;
  savingStatus.value = true;
  const id = getBorrowId(selectedBorrow.value);
  
  try {
    const api = new ApiService();
    const res = await api.addAuthenticationHeader().patch(`/transactions/borrow/${id}/`, {
      status: newStatus.value
    });
    
    if (res?.success || res?.data) {
      const updated = res.data || { ...selectedBorrow.value, status: newStatus.value };
      borrowStore.update(id, updated);
      emitEntityMutation('borrows', { action: 'updated', id, status: newStatus.value });
      toasted(true, 'Borrow status updated successfully');
      pagination.refresh();
      closeEditModal();
    } else {
      toasted(false, 'Failed to update status', res?.error || 'Validation error');
    }
  } catch (err) {
    toasted(false, err?.response?.data?.detail || 'An error occurred while updating status');
  } finally {
    savingStatus.value = false;
  }
}

function deleteBorrowRecord(row) {
  const id = getBorrowId(row);
  if (!id) return;
  
  openModal(
    'Confirmation',
    {
      title: 'WARNING: Delete Borrow Record',
      message: `Are you sure you want to delete the borrow record for "${row.material_title}"? This action is permanent.`,
    },
    (confirm1) => {
      if (!confirm1) return;
      
      openModal(
        'Confirmation',
        {
          title: 'FINAL CONFIRMATION: Restore Inventory?',
          message: `This will restore 1 copy of "${row.material_title}" back to library stock. Are you absolutely sure you want to delete this record?`,
        },
        (confirm2) => {
          if (!confirm2) return;
          
          const api = new ApiService();
          api.addAuthenticationHeader().delete(`/transactions/borrow/${id}/`).then(() => {
            borrowStore.remove(id);
            emitEntityMutation('borrows', { action: 'deleted', id });
            toasted(true, 'Borrow record deleted and inventory restored');
            pagination.refresh();
          }).catch((err) => {
            toasted(false, err?.response?.data?.detail || 'Failed to delete borrow record');
          });
        }
      );
    }
  );
}
</script>

<template>
  <div class="p-4 sm:p-7">
    <div class="mb-6">
      <BorrowHeader :stats="headerStats" :show-view-toggle="false" />
    </div>
    
    <div class="mb-6 bg-white dark:bg-slate-800 rounded-2xl border border-gray-100 dark:border-slate-700 shadow-sm p-5 transition-all duration-300">
      <div class="flex flex-col lg:flex-row justify-between lg:items-center gap-4">
        <div>
          <h1 class="text-2xl font-bold flex items-center gap-2 text-gray-900 dark:text-white">
            <BaseIcon :path="mdiBookmark" size="28" class="text-amber-500" />
            Borrow Management
          </h1>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Search and manage active borrow records</p>
        </div>

        <button
          @click="router.push('/borrows/add')"
          class="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-6 py-2.5 rounded-xl flex items-center gap-2 hover:from-amber-600 hover:to-orange-600 transition-all duration-300 shadow-md hover:shadow-lg"
        >
          <svg width="14" height="14" viewBox="0 0 12 14" fill="white" xmlns="http://www.w3.org/2000/svg">
            <path d="M6 0V14M0 7H12" stroke="white" stroke-width="2"/>
          </svg>
          <span>Add Borrow</span>
        </button>
      </div>
      
      <div class="mt-4 relative">
        <BaseIcon
          :path="mdiMagnify"
          size="18"
          class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500"
        />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Search by material, author, member, ID, or status..."
          class="w-3/4 pl-10 pr-4 py-2.5 border border-gray-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-amber-400 bg-white dark:bg-slate-800 text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500 transition-all duration-200"
        />
      </div>
    </div>

    <div class="bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-100 dark:border-slate-700 overflow-hidden transition-all duration-300">
      <Table
        :pending="pagination.pending.value"
        :pagination="pagination.meta.value"
        @next-page="pagination.next"
        @prev-page="pagination.previous"
        @page-change="pagination.goToPage"
        @page-size-change="pagination.setPerPage"
        :headers="{
          head: [
            'Material',
            'Author',
            'Member Name',
            'Member ID',
            'Borrowed At',
            'Returns At',
            'Fine Amount',
            'Status',
          ],
          row: [
            'material_title',
            'material_author',
            'member_name',
            'member_id',
            'borrow_date',
            'due_date',
            'estimated_fine_amount',
            'status',
          ],
        }"
        :cells="{
          borrow_date: (val) => secondDateFormatWithTime(val) || '-',
          due_date: (val) => secondDateFormatWithTime(val) || '-',
        }"
        :rows="filteredBorrows"
      >
        <template #actions="{ row }">
          <div class="flex items-center gap-2">
            <button
              v-if="row?.status !== 'RETURNED'"
              class="bg-blue-50 dark:bg-blue-950/30 text-blue-600 dark:text-blue-400 hover:bg-blue-600 hover:text-white px-2.5 py-1.5 rounded-lg flex items-center gap-1 transition-all duration-200"
              @click="openEditStatusModal(row)"
            >
              <BaseIcon :path="mdiPencil" size="14" />
              <span>Status</span>
            </button>
            <button
              v-if="row?.status !== 'RETURNED'"
              class="bg-rose-50 dark:bg-rose-950/30 text-rose-600 dark:text-rose-400 hover:bg-rose-600 hover:text-white px-2.5 py-1.5 rounded-lg flex items-center gap-1 transition-all duration-200"
              @click="deleteBorrowRecord(row)"
            >
              <BaseIcon :path="mdiDeleteAlert" size="14" />
              <span>Delete</span>
            </button>
            <span v-else class="text-xs text-gray-400 dark:text-gray-600">Returned</span>
          </div>
        </template>
      </Table>
    </div>

    <!-- Edit Status Modal -->
    <div v-if="showEditModal" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fade-in">
      <div class="bg-white dark:bg-slate-800 rounded-2xl w-full max-w-md shadow-2xl border border-gray-100 dark:border-slate-700 overflow-hidden transform transition-all duration-300">
        <header class="px-6 py-4 border-b border-gray-100 dark:border-slate-700 flex justify-between items-center">
          <h3 class="text-lg font-bold text-gray-900 dark:text-white">Edit Borrow Status</h3>
          <button @click="closeEditModal" class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200">
            <BaseIcon :path="mdiClose" size="18" />
          </button>
        </header>
        
        <div class="p-6">
          <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Update status for borrow transaction of: <strong class="text-gray-950 dark:text-white">"{{ selectedBorrow?.material_title }}"</strong>
          </p>
          
          <label class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Status</label>
          <select
            v-model="newStatus"
            class="w-full px-4 py-2.5 border border-gray-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-amber-400 bg-white dark:bg-slate-800 text-gray-900 dark:text-gray-100"
          >
            <option value="BORROWED">BORROWED</option>
            <option value="OVERDUE">OVERDUE</option>
            <option value="RETURNED">RETURNED</option>
          </select>
        </div>
        
        <footer class="px-6 py-4 bg-gray-50 dark:bg-slate-900 border-t border-gray-100 dark:border-slate-700 flex justify-end gap-3">
          <button @click="closeEditModal" class="px-4 py-2 rounded-xl text-sm font-semibold border border-gray-200 dark:border-slate-700 text-gray-500 hover:bg-gray-100 dark:hover:bg-slate-800 transition-colors" :disabled="savingStatus">Cancel</button>
          <button @click="saveStatusUpdate" class="px-4 py-2 rounded-xl text-sm font-semibold bg-amber-500 hover:bg-amber-600 text-white shadow-md hover:shadow-lg transition-all" :disabled="savingStatus">
            {{ savingStatus ? 'Saving...' : 'Save Changes' }}
          </button>
        </footer>
      </div>
    </div>
  </div>
</template>