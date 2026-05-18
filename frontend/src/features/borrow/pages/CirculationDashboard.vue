<script setup>
import { computed, onBeforeUnmount, onMounted, ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useApiRequest } from '@/composables/useApiRequest';
import BaseIcon from '@/components/base/BaseIcon.vue';
import Table from '@/components/Table.vue';
import { getAllBorrows, updateBorrowById, removeBorrowById, createBorrow } from '@/features/borrow/api/borrowApi';
import { createReturn, getAllReturns } from '@/features/returns/api/returnApi';
import { getAllReservation, updateReservationById, removeReservationById } from '@/features/reservation/api/reservationApi';
import { getAllMaterials } from '@/features/material/api/materialApi';
import { getAllUser } from '@/features/users/Api/UserApi';
import { generatePaymentReceipt } from '@/features/payment/utils/receiptGenerator';
import { secondDateFormatWithTime, toasted } from '@/utils/utils';
import { emitEntityMutation, subscribeEntityMutation } from '@/utils/entitySync';
import {
  mdiKeyboardReturn,
  mdiClockAlertOutline,
  mdiBookmarkOutline,
  mdiCashMultiple,
  mdiMagnify,
  mdiRefresh,
  mdiDelete,
  mdiBarcodeScan,
  mdiCheckCircleOutline,
  mdiCancel,
  mdiFileDownloadOutline,
  mdiPrinter,
  mdiAlertCircle,
  mdiCheck,
  mdiPlus
} from '@mdi/js';

const router = useRouter();
const activeTab = ref('borrows');
const searchQuery = ref('');

// API composables
const borrowReq = useApiRequest();
const returnReq = useApiRequest();
const reservationReq = useApiRequest();
const returnActionReq = useApiRequest();
const deleteReq = useApiRequest();
const actionReq = useApiRequest();

// Quick Return Desk State
const quickReturn = reactive({
  borrowId: '',
  condition: 'GOOD',
  notes: ''
});

// Direct Borrow Checkout State
const checkoutForm = reactive({
  materialId: '',
  memberId: ''
});
const materialsReq = useApiRequest();
const usersReq = useApiRequest();
const directBorrowReq = useApiRequest();

const materialSearch = ref('');
const memberSearch = ref('');

const allPhysicalMaterials = computed(() => {
  const payload = materialsReq.response.value;
  return rowsFromPayload(payload).filter(m => Number(m.available_copies || 0) > 0 && m.can_borrow);
});

const filteredCheckoutMaterials = computed(() => {
  const list = allPhysicalMaterials.value;
  const q = materialSearch.value.trim().toLowerCase();
  if (!q) return list;
  return list.filter(m =>
    [m.title, m.author, m.isbn].filter(Boolean)
      .some(val => String(val).toLowerCase().includes(q))
  );
});

const allMembers = computed(() => {
  const payload = usersReq.response.value;
  return rowsFromPayload(payload);
});

const filteredCheckoutMembers = computed(() => {
  const list = allMembers.value.filter(u => normalizeStatus(u.role) === 'MEMBER');
  const q = memberSearch.value.trim().toLowerCase();
  if (!q) return list;
  return list.filter(m =>
    [`${m.first_name} ${m.last_name}`, m.id_number, m.email].filter(Boolean)
      .some(val => String(val).toLowerCase().includes(q))
  );
});

function loadAddCheckoutData() {
  materialsReq.send(() => getAllMaterials({ page: 1, size: 500 }, 'physical'));
  usersReq.send(() => getAllUser({ page: 1, size: 500 }));
}

function submitDirectCheckout() {
  if (!checkoutForm.materialId || !checkoutForm.memberId) {
    toasted(false, 'Please select both a physical material and a member.');
    return;
  }
  directBorrowReq.send(
    () => createBorrow({ material: checkoutForm.materialId, member: checkoutForm.memberId }),
    (res) => {
      if (res.success) {
        toasted(true, 'Borrow transaction registered successfully!');
        emitEntityMutation('borrows', { action: 'created', id: res.data?.id });
        checkoutForm.materialId = '';
        checkoutForm.memberId = '';
        activeTab.value = 'borrows';
        loadDashboardData();
      } else {
        toasted(false, 'Direct checkout registration failed', res.error);
      }
    }
  );
}

let unsubscribeSync = () => {};

function rowsFromPayload(payload) {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.content)) return payload.content;
  if (Array.isArray(payload?.response)) return payload.response;
  if (Array.isArray(payload?.data)) return payload.data;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.result)) return payload.result;
  return [];
}

function normalizeStatus(value) {
  return String(value || '').trim().toUpperCase();
}

function loadDashboardData() {
  borrowReq.send(() => getAllBorrows({ page: 1, size: 300 }));
  returnReq.send(() => getAllReturns({ page: 1, size: 300 }));
  reservationReq.send(() => getAllReservation({ page: 1, size: 300 }));
}

// Computeds for data lists
const borrows = computed(() => rowsFromPayload(borrowReq.response.value));
const returns = computed(() => rowsFromPayload(returnReq.response.value));
const reservations = computed(() => rowsFromPayload(reservationReq.response.value));

// Active Borrows filter
const activeBorrows = computed(() =>
  borrows.value.filter((row) => !row?.is_returned && ['BORROWED', 'OVERDUE'].includes(normalizeStatus(row?.status)))
);

// Dynamic Calculations & Overdue check
const parsedBorrows = computed(() => {
  return activeBorrows.value.map(b => {
    const dueDate = new Date(b.due_date);
    const now = new Date();
    const isOverdue = dueDate < now;
    const estFine = isOverdue ? Math.max(0, Math.ceil((now - dueDate) / (1000 * 60 * 60 * 24)) * 1.5) : 0;
    return {
      ...b,
      isOverdueComputed: isOverdue,
      estimatedFine: estFine
    };
  });
});

// Search filters
const filteredBorrows = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  if (!query) return parsedBorrows.value;
  return parsedBorrows.value.filter(row =>
    [row?.material_title, row?.member_name, row?.member_id_number, row?.member].filter(Boolean)
      .some(val => String(val).toLowerCase().includes(query))
  );
});

const filteredReservations = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  const list = reservations.value.filter(r => ['RESERVED', 'PENDING'].includes(normalizeStatus(r.status)));
  if (!query) return list;
  return list.filter(row =>
    [row?.material_title, row?.member_id_number, row?.member].filter(Boolean)
      .some(val => String(val).toLowerCase().includes(query))
  );
});

// Statistics Card metrics
const stats = computed(() => {
  const overdueCount = parsedBorrows.value.filter(b => b.isOverdueComputed || normalizeStatus(b.status) === 'OVERDUE').length;
  const pendingFines = returns.value.filter(r => normalizeStatus(r.payment_status) !== 'COMPLETED' && Number(r.fine_amount) > 0);
  const totalFineAmt = pendingFines.reduce((sum, r) => sum + Number(r.fine_amount || 0), 0);
  
  return {
    activeBorrows: parsedBorrows.value.length,
    overdue: overdueCount,
    reservations: filteredReservations.value.length,
    pendingFinesCount: pendingFines.length,
    totalFines: totalFineAmt
  };
});

// Double Confirmation state
const showDeleteConfirm = ref(false);
const itemToDelete = ref(null);
const doubleConfirmText = ref('');

function triggerDeleteFlow(row) {
  itemToDelete.value = row;
  doubleConfirmText.value = '';
  showDeleteConfirm.value = true;
}

function processSecureDelete() {
  if (doubleConfirmText.value.toLowerCase() !== 'restore') {
    toasted(false, "Verification failed. Please type 'restore' to confirm.");
    return;
  }
  if (!itemToDelete.value) return;

  deleteReq.send(
    () => removeBorrowById(itemToDelete.value.id),
    (res) => {
      if (res.success) {
        toasted(true, 'Borrow transaction safely deleted. Inventory restored.');
        emitEntityMutation('borrows', { action: 'deleted', id: itemToDelete.value.id });
        showDeleteConfirm.value = false;
        itemToDelete.value = null;
        loadDashboardData();
      } else {
        toasted(false, 'Failed to delete record', res.error);
      }
    }
  );
}

// Inline Return Check-In Flow
function checkInBorrow(borrowId, condition = 'GOOD') {
  returnActionReq.send(
    () => createReturn({ borrow: borrowId, condition }),
    (res) => {
      if (res.success) {
        const retData = res.data || res;
        const fine = Number(retData?.fine_amount || 0);
        toasted(true, `Return processed successfully!${fine > 0 ? ` Fine generated: $${fine.toFixed(2)}` : ''}`);
        
        emitEntityMutation('returns', { action: 'created', id: retData?.id });
        
        // Settle state
        quickReturn.borrowId = '';
        quickReturn.notes = '';
        
        // Auto download fine receipt if fine is paid or generated
        if (fine > 0) {
          triggerReceiptDownload(retData);
        }

        loadDashboardData();
      } else {
        toasted(false, 'Check-In failed', res.error);
      }
    }
  );
}

// Cancel Reservation
function cancelReservation(row) {
  if (!confirm(`Cancel reservation for "${row.material_title}"?`)) return;
  actionReq.send(
    () => removeReservationById(row.id),
    (res) => {
      if (res.success) {
        toasted(true, 'Reservation cancelled successfully.');
        emitEntityMutation('reservations', { action: 'updated', id: row.id, status: 'CANCELLED' });
        loadDashboardData();
      } else {
        toasted(false, 'Failed to cancel', res.error);
      }
    }
  );
}

// Fulfill Reservation (convert reservation to borrow)
function fulfillReservation(row) {
  if (!confirm(`Convert reservation for "${row.material_title}" to active borrow?`)) return;
  // Reservation transitions to COMPLETED on backend via PATCH/PUT or Custom Action
  actionReq.send(
    () => updateReservationById(row.id, { status: 'COMPLETED' }),
    (res) => {
      if (res.success) {
        toasted(true, 'Reservation fulfilled successfully.');
        emitEntityMutation('reservations', { action: 'fulfilled', id: row.id });
        loadDashboardData();
      } else {
        toasted(false, 'Fulfillment failed', res.error);
      }
    }
  );
}

// PDF receipt compiler
function triggerReceiptDownload(retObj) {
  const paymentMock = {
    id: retObj.id,
    payment_intent_id: retObj.payment_reference || `TX-${retObj.id.slice(0,8)}`,
    payment_date: retObj.return_date || new Date().toISOString(),
    payment_method: 'Circulation Desk Settle',
    member_name: retObj.member_name || 'Library Patron',
    member_id_number: retObj.member || 'N/A',
    library_name: retObj.library_name || 'Central Library',
    material_title: retObj.material_title || 'Overdue Material Return',
    fee_type: 'Overdue Fine Penalty',
    amount: retObj.fine_amount || 0
  };
  generatePaymentReceipt(paymentMock);
}

onMounted(() => {
  loadDashboardData();
  unsubscribeSync = subscribeEntityMutation('*', ({ entity }) => {
    if (['borrows', 'returns', 'reservations'].includes(entity)) {
      loadDashboardData();
    }
  });
});

onBeforeUnmount(() => {
  unsubscribeSync?.();
});
</script>

<template>
  <div class="space-y-6 p-4 sm:p-7 bg-slate-50 dark:bg-slate-950 min-h-screen text-slate-800 dark:text-slate-100 transition-colors duration-300">
    
    <!-- Hero Branding Board -->
    <header class="relative rounded-[28px] border border-slate-200 dark:border-slate-800 bg-[radial-gradient(circle_at_top_left,_rgba(245,158,11,0.18),_transparent_45%),linear-gradient(135deg,_#0f172a,_#1d4ed8_55%,_#1e3a8a)] p-6 text-white shadow-xl overflow-hidden">
      <div class="absolute right-0 top-0 w-64 h-64 bg-amber-500/10 rounded-full blur-3xl -z-10"></div>
      <div class="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <span class="text-xs font-bold uppercase tracking-[0.28em] text-amber-400">Circulation Desk Terminal</span>
          <h1 class="mt-2 text-3xl font-bold tracking-tight">Consolidated Library Circulation Desk</h1>
          <p class="mt-2 text-sm text-slate-200/90 max-w-xl">
            Streamline active borrows management, quick condition-based return check-ins, fine settlements, and reservations on a single intuitive dashboard.
          </p>
        </div>
        <button
          @click="loadDashboardData"
          class="flex items-center gap-2 self-start md:self-center bg-white/10 hover:bg-white/20 transition text-white text-sm px-4 py-2 rounded-full border border-white/10"
        >
          <BaseIcon :path={mdiRefresh} size="16" />
          Sync Dashboard
        </button>
      </div>
    </header>

    <!-- Metrics Strip -->
    <section class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm flex items-center justify-between">
        <div>
          <p class="text-[10px] uppercase tracking-wider text-slate-400 dark:text-slate-500 font-bold">Active Borrows</p>
          <h3 class="text-2xl font-bold mt-1 text-slate-900 dark:text-white">{{ stats.activeBorrows }}</h3>
        </div>
        <div class="bg-blue-50 dark:bg-blue-950/40 p-3 rounded-xl text-blue-600 dark:text-blue-400">
          <BaseIcon :path={mdiKeyboardReturn} size="22" />
        </div>
      </div>

      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm flex items-center justify-between">
        <div>
          <p class="text-[10px] uppercase tracking-wider text-slate-400 dark:text-slate-500 font-bold">Overdue Checkouts</p>
          <h3 class="text-2xl font-bold mt-1 text-rose-600 dark:text-rose-400">{{ stats.overdue }}</h3>
        </div>
        <div class="bg-rose-50 dark:bg-rose-950/40 p-3 rounded-xl text-rose-600 dark:text-rose-400 font-bold">
          <BaseIcon :path={mdiClockAlertOutline} size="22" />
        </div>
      </div>

      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm flex items-center justify-between">
        <div>
          <p class="text-[10px] uppercase tracking-wider text-slate-400 dark:text-slate-500 font-bold">Active Reservations</p>
          <h3 class="text-2xl font-bold mt-1 text-amber-500 dark:text-amber-400">{{ stats.reservations }}</h3>
        </div>
        <div class="bg-amber-50 dark:bg-amber-950/40 p-3 rounded-xl text-amber-500 dark:text-amber-400">
          <BaseIcon :path={mdiBookmarkOutline} size="22" />
        </div>
      </div>

      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm flex items-center justify-between">
        <div>
          <p class="text-[10px] uppercase tracking-wider text-slate-400 dark:text-slate-500 font-bold">Pending Overdue Fines</p>
          <h3 class="text-2xl font-bold mt-1 text-emerald-600 dark:text-emerald-400">${{ stats.totalFines.toFixed(2) }}</h3>
        </div>
        <div class="bg-emerald-50 dark:bg-emerald-950/40 p-3 rounded-xl text-emerald-600 dark:text-emerald-400">
          <BaseIcon :path={mdiCashMultiple} size="22" />
        </div>
      </div>

    </section>

    <!-- Custom Navigation Tabs -->
    <div class="flex border-b border-slate-200 dark:border-slate-800 gap-4">
      <button
        @click="activeTab = 'borrows'"
        class="pb-3 text-sm font-semibold border-b-2 transition-all px-2"
        :class="activeTab === 'borrows' ? 'border-blue-600 text-blue-600 dark:border-blue-500 dark:text-blue-400' : 'border-transparent text-slate-400 hover:text-slate-600 dark:hover:text-slate-300'"
      >
        Active Borrows List
      </button>
      <button
        @click="activeTab = 'returns'"
        class="pb-3 text-sm font-semibold border-b-2 transition-all px-2"
        :class="activeTab === 'returns' ? 'border-blue-600 text-blue-600 dark:border-blue-500 dark:text-blue-400' : 'border-transparent text-slate-400 hover:text-slate-600 dark:hover:text-slate-300'"
      >
        Quick Return Desk
      </button>
      <button
        @click="activeTab = 'reservations'"
        class="pb-3 text-sm font-semibold border-b-2 transition-all px-2"
        :class="activeTab === 'reservations' ? 'border-blue-600 text-blue-600 dark:border-blue-500 dark:text-blue-400' : 'border-transparent text-slate-400 hover:text-slate-600 dark:hover:text-slate-300'"
      >
        Reservations Queue
      </button>
      <button
        @click="activeTab = 'add-checkout'; loadAddCheckoutData();"
        class="pb-3 text-sm font-semibold border-b-2 transition-all px-2"
        :class="activeTab === 'add-checkout' ? 'border-blue-600 text-blue-600 dark:border-blue-500 dark:text-blue-400' : 'border-transparent text-slate-400 hover:text-slate-600 dark:hover:text-slate-300'"
      >
        Register New Borrow
      </button>
    </div>

    <!-- Active Borrows Section -->
    <section v-if="activeTab === 'borrows'" class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-6">
        <div>
          <h2 class="text-lg font-bold text-slate-900 dark:text-white">Active Borrowing Ledger</h2>
          <p class="text-xs text-slate-400">Track and manage active checkouts and handle check-in processing.</p>
        </div>
        <div class="relative w-full sm:max-w-xs">
          <BaseIcon :path={mdiMagnify} size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search patron or book title..."
            class="w-full pl-9 pr-4 py-2 border border-slate-200 dark:border-slate-800 rounded-lg bg-slate-50 dark:bg-slate-950 text-sm outline-none focus:ring-2 focus:ring-blue-500/20"
          />
        </div>
      </div>

      <Table
        :pending="borrowReq.pending.value || returnActionReq.pending.value"
        :rows="filteredBorrows"
        :show-pagination="false"
        :headers="{
          head: ['Material Title', 'Patron Name', 'Borrow Date', 'Due Date', 'Estimated Fine', 'Status', 'Actions'],
          row: ['material_title', 'member_name', 'borrow_date', 'due_date', 'estimatedFine', 'status']
        }"
        :cells="{
          borrow_date: (val) => secondDateFormatWithTime(val) || '-',
          due_date: (val) => secondDateFormatWithTime(val) || '-',
          estimatedFine: (val, row) => row.isOverdueComputed ? `$${val.toFixed(2)}` : '$0.00'
        }"
      >
        <template #status="{ row }">
          <span
            class="text-[10px] font-bold px-2 py-0.5 rounded-full border"
            :class="row.isOverdueComputed 
              ? 'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/20 dark:text-rose-400 dark:border-rose-900/50' 
              : 'bg-amber-50 text-amber-700 border-amber-200 dark:bg-amber-950/20 dark:text-amber-400 dark:border-amber-900/50'"
          >
            {{ row.isOverdueComputed ? 'OVERDUE' : 'BORROWED' }}
          </span>
        </template>
        
        <template #actions="{ row }">
          <div class="flex items-center gap-2">
            <button
              @click="checkInBorrow(row.id)"
              class="bg-emerald-50 text-emerald-600 hover:bg-emerald-600 hover:text-white dark:bg-emerald-950/20 dark:text-emerald-400 dark:hover:bg-emerald-500 dark:hover:text-white border border-emerald-200 dark:border-emerald-900/50 px-3 py-1 rounded-lg text-xs font-semibold flex items-center gap-1 transition"
            >
              <BaseIcon :path={mdiKeyboardReturn} size="14" />
              Check In
            </button>
            <button
              @click="triggerDeleteFlow(row)"
              class="bg-rose-50 text-rose-600 hover:bg-rose-600 hover:text-white dark:bg-rose-950/20 dark:text-rose-400 dark:hover:bg-rose-500 dark:hover:text-white border border-rose-200 dark:border-rose-900/50 p-1.5 rounded-lg transition"
            >
              <BaseIcon :path={mdiDelete} size="14" />
            </button>
          </div>
        </template>
      </Table>
    </section>

    <!-- Quick Return Desk Section -->
    <section v-if="activeTab === 'returns'" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- Input Panel -->
      <div class="lg:col-span-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm space-y-4">
        <div>
          <h3 class="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
            <BaseIcon :path={mdiBarcodeScan} size="20" class="text-amber-500" />
            Quick Book Check-In
          </h3>
          <p class="text-xs text-slate-400 mt-1">Select an active borrow record, assess return condition, and complete processing.</p>
        </div>

        <div class="space-y-3">
          <div>
            <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Select Active Checkout</label>
            <select
              v-model="quickReturn.borrowId"
              class="w-full border border-slate-200 dark:border-slate-800 rounded-lg p-2.5 bg-slate-50 dark:bg-slate-950 text-sm outline-none focus:ring-2 focus:ring-blue-500/20"
            >
              <option value="" disabled>Choose a borrow checkout...</option>
              <option v-for="b in parsedBorrows" :key="b.id" :value="b.id">
                {{ b.material_title }} ({{ b.member_name }})
              </option>
            </select>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Assess Material Condition</label>
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="cond in ['NEW', 'GOOD', 'FAIR', 'DAMAGED']"
                :key="cond"
                type="button"
                @click="quickReturn.condition = cond"
                class="py-2 px-3 text-xs font-semibold rounded-lg border text-center transition"
                :class="quickReturn.condition === cond 
                  ? 'bg-amber-500 border-amber-500 text-white shadow-md' 
                  : 'bg-slate-50 dark:bg-slate-950 border-slate-200 dark:border-slate-800 hover:bg-slate-100 text-slate-700 dark:text-slate-300'"
              >
                {{ cond }}
              </button>
            </div>
            <p class="text-[10px] text-slate-400 mt-1.5 leading-relaxed">
              * Condition status maps to standard library replacement fines: Fair (10%), Damaged (35%), Lost (100%).
            </p>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Additional Staff Notes</label>
            <textarea
              v-model="quickReturn.notes"
              rows="3"
              placeholder="Record any visual damage, missing pages, or check-in details..."
              class="w-full border border-slate-200 dark:border-slate-800 rounded-lg p-2.5 bg-slate-50 dark:bg-slate-950 text-sm outline-none focus:ring-2 focus:ring-blue-500/20"
            ></textarea>
          </div>

          <button
            @click="checkInBorrow(quickReturn.borrowId, quickReturn.condition)"
            :disabled="!quickReturn.borrowId || returnActionReq.pending.value"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 rounded-lg text-sm transition shadow-lg shadow-blue-500/10 flex items-center justify-center gap-2"
          >
            <BaseIcon :path={mdiKeyboardReturn} size="16" />
            {{ returnActionReq.pending.value ? 'Processing Check-In...' : 'Record Book Return' }}
          </button>
        </div>
      </div>

      <!-- History Feed -->
      <div class="lg:col-span-2 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm">
        <h3 class="text-base font-bold text-slate-900 dark:text-white mb-4">Recent Book Returns & Settled Fees</h3>
        
        <Table
          :pending="returnReq.pending.value"
          :rows="returns"
          :show-pagination="false"
          :headers="{
            head: ['Material Title', 'Member ID', 'Return Date', 'Overdue Fine', 'Payment', 'Receipt'],
            row: ['material_title', 'member', 'return_date', 'fine_amount', 'payment_status']
          }"
          :cells="{
            return_date: (val) => secondDateFormatWithTime(val) || '-',
            fine_amount: (val) => `$${Number(val || 0).toFixed(2)}`
          }"
        >
          <template #payment_status="{ row }">
            <span
              class="text-[10px] font-bold px-2 py-0.5 rounded-full border"
              :class="Number(row.fine_amount) === 0 || normalizeStatus(row.payment_status) === 'COMPLETED'
                ? 'bg-emerald-50 text-emerald-700 border-emerald-200 dark:bg-emerald-950/20 dark:text-emerald-400 dark:border-emerald-900/50'
                : 'bg-rose-50 text-rose-700 border-rose-200 dark:bg-rose-950/20 dark:text-rose-400 dark:border-rose-900/50'"
            >
              {{ Number(row.fine_amount) === 0 || normalizeStatus(row.payment_status) === 'COMPLETED' ? 'PAID/WAIVED' : 'UNPAID' }}
            </span>
          </template>

          <template #receipt="{ row }">
            <button
              v-if="Number(row.fine_amount) > 0"
              @click="triggerReceiptDownload(row)"
              class="p-1 rounded bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 transition flex items-center gap-1 text-xs text-blue-600 dark:text-blue-400"
              title="Download Fine Payment Receipt"
            >
              <BaseIcon :path={mdiFileDownloadOutline} size="14" />
              Receipt
            </button>
            <span v-else class="text-xs text-slate-400">-</span>
          </template>
        </Table>
      </div>

    </section>

    <!-- Reservations Section -->
    <section v-if="activeTab === 'reservations'" class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between mb-6">
        <div>
          <h2 class="text-lg font-bold text-slate-900 dark:text-white">Active Reservations Board</h2>
          <p class="text-xs text-slate-400">View and fulfill material reservations queues when inventory is replenished.</p>
        </div>
        <div class="relative w-full sm:max-w-xs">
          <BaseIcon :path={mdiMagnify} size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search reservation list..."
            class="w-full pl-9 pr-4 py-2 border border-slate-200 dark:border-slate-800 rounded-lg bg-slate-50 dark:bg-slate-950 text-sm outline-none focus:ring-2 focus:ring-blue-500/20"
          />
        </div>
      </div>

      <Table
        :pending="reservationReq.pending.value || actionReq.pending.value"
        :rows="filteredReservations"
        :show-pagination="false"
        :headers="{
          head: ['Material Title', 'Patron ID', 'Reservation Date', 'Expiry Date', 'Status', 'Actions'],
          row: ['material_title', 'member', 'reserve_date', 'expiry_date', 'status']
        }"
        :cells="{
          reserve_date: (val) => secondDateFormatWithTime(val) || '-',
          expiry_date: (val) => secondDateFormatWithTime(val) || '-'
        }"
      >
        <template #status="{ row }">
          <span
            class="text-[10px] font-bold px-2 py-0.5 rounded-full border bg-purple-50 text-purple-700 border-purple-200 dark:bg-purple-950/20 dark:text-purple-400 dark:border-purple-900/50"
          >
            {{ normalizeStatus(row.status) }}
          </span>
        </template>

        <template #actions="{ row }">
          <div class="flex items-center gap-2">
            <button
              @click="fulfillReservation(row)"
              class="bg-blue-50 text-blue-600 hover:bg-blue-600 hover:text-white dark:bg-blue-950/20 dark:text-blue-400 dark:hover:bg-blue-500 dark:hover:text-white border border-blue-200 dark:border-blue-900/50 px-3 py-1 rounded-lg text-xs font-semibold flex items-center gap-1 transition"
            >
              <BaseIcon :path={mdiCheck} size="14" />
              Fulfill checkout
            </button>
            <button
              @click="cancelReservation(row)"
              class="bg-rose-50 text-rose-600 hover:bg-rose-600 hover:text-white dark:bg-rose-950/20 dark:text-rose-400 dark:hover:bg-rose-500 dark:hover:text-white border border-rose-200 dark:border-rose-900/50 px-3 py-1 rounded-lg text-xs font-semibold flex items-center gap-1 transition"
            >
              <BaseIcon :path={mdiCancel} size="14" />
              Cancel
            </button>
          </div>
        </template>
      </Table>
    </section>
 
    <!-- Register New Borrow Section -->
    <section v-if="activeTab === 'add-checkout'" class="space-y-6">
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        <!-- Left Column: Select Physical Book -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm flex flex-col h-[600px]">
          <div class="mb-4">
            <h3 class="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <BaseIcon :path="mdiPlus" size="20" class="text-amber-500" />
              1. Select Physical Material
            </h3>
            <p class="text-xs text-slate-400 mt-1">Search and select an available book for checkout.</p>
          </div>

          <div class="relative mb-4">
            <BaseIcon :path="mdiMagnify" size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              v-model="materialSearch"
              type="text"
              placeholder="Search by title, author, ISBN..."
              class="w-full pl-9 pr-4 py-2 border border-slate-200 dark:border-slate-800 rounded-lg bg-slate-50 dark:bg-slate-950 text-sm outline-none focus:ring-2 focus:ring-blue-500/20"
            />
          </div>

          <!-- Materials Scroll list -->
          <div class="flex-1 overflow-y-auto space-y-2 pr-1">
            <div v-if="materialsReq.pending.value" class="flex items-center justify-center py-12">
              <div class="animate-spin rounded-full h-8 w-8 border-2 border-blue-500 border-t-transparent"></div>
            </div>
            <div v-else-if="!filteredCheckoutMaterials.length" class="text-center py-12 text-slate-400 dark:text-slate-500">
              No available books found matching the search.
            </div>
            <div
              v-for="m in filteredCheckoutMaterials"
              :key="m.id"
              @click="checkoutForm.materialId = m.id"
              class="p-3 rounded-xl border transition cursor-pointer flex items-center justify-between"
              :class="checkoutForm.materialId === m.id
                ? 'bg-amber-500/10 border-amber-500 dark:bg-amber-950/20 shadow-md'
                : 'bg-slate-50 border-slate-200 dark:bg-slate-950 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-900'"
            >
              <div class="flex-1 min-w-0 pr-3">
                <h4 class="text-sm font-bold truncate text-slate-900 dark:text-white">{{ m.title }}</h4>
                <p class="text-xs text-slate-400 truncate mt-0.5">by {{ m.author || 'Unknown' }}</p>
                <div class="flex items-center gap-2 mt-1">
                  <span class="text-[10px] uppercase font-bold px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
                    {{ m.category }}
                  </span>
                  <span class="text-[10px] font-semibold text-slate-400">
                    ISBN: {{ m.isbn || 'N/A' }}
                  </span>
                </div>
              </div>
              <div class="flex items-center gap-3">
                <span class="text-xs font-semibold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/20 dark:text-emerald-400 px-2 py-0.5 rounded-full border border-emerald-200 dark:border-emerald-900/50">
                  {{ m.available_copies }} left
                </span>
                <div
                  class="w-5 h-5 rounded-full border flex items-center justify-center flex-shrink-0"
                  :class="checkoutForm.materialId === m.id ? 'bg-amber-500 border-amber-500 text-white' : 'border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900'"
                >
                  <BaseIcon v-if="checkoutForm.materialId === m.id" :path="mdiCheck" size="12" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Select Member -->
        <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-5 rounded-2xl shadow-sm flex flex-col h-[600px]">
          <div class="mb-4">
            <h3 class="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <BaseIcon :path="mdiPlus" size="20" class="text-amber-500" />
              2. Select Library Member
            </h3>
            <p class="text-xs text-slate-400 mt-1">Search and select the patron member checking out.</p>
          </div>

          <div class="relative mb-4">
            <BaseIcon :path="mdiMagnify" size="16" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              v-model="memberSearch"
              type="text"
              placeholder="Search by name, email, ID card number..."
              class="w-full pl-9 pr-4 py-2 border border-slate-200 dark:border-slate-800 rounded-lg bg-slate-50 dark:bg-slate-950 text-sm outline-none focus:ring-2 focus:ring-blue-500/20"
            />
          </div>

          <!-- Members Scroll list -->
          <div class="flex-1 overflow-y-auto space-y-2 pr-1">
            <div v-if="usersReq.pending.value" class="flex items-center justify-center py-12">
              <div class="animate-spin rounded-full h-8 w-8 border-2 border-blue-500 border-t-transparent"></div>
            </div>
            <div v-else-if="!filteredCheckoutMembers.length" class="text-center py-12 text-slate-400 dark:text-slate-500">
              No registered library members found.
            </div>
            <div
              v-for="u in filteredCheckoutMembers"
              :key="u.id"
              @click="checkoutForm.memberId = u.id"
              class="p-3 rounded-xl border transition cursor-pointer flex items-center justify-between"
              :class="checkoutForm.memberId === u.id
                ? 'bg-blue-500/10 border-blue-500 dark:bg-blue-950/20 shadow-md'
                : 'bg-slate-50 border-slate-200 dark:bg-slate-950 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-900'"
            >
              <div class="flex-1 min-w-0 pr-3 flex items-center gap-3">
                <div class="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-indigo-500 flex items-center justify-center text-white text-xs font-bold flex-shrink-0">
                  {{ (u.first_name?.charAt(0) || '') + (u.last_name?.charAt(0) || '') }}
                </div>
                <div class="min-w-0">
                  <h4 class="text-sm font-bold truncate text-slate-900 dark:text-white">
                    {{ u.first_name }} {{ u.last_name }}
                  </h4>
                  <p class="text-xs text-slate-400 truncate mt-0.5">{{ u.email }}</p>
                  <p class="text-[10px] font-mono text-slate-500 mt-0.5">Card ID: {{ u.id_number || 'N/A' }}</p>
                </div>
              </div>
              <div
                class="w-5 h-5 rounded-full border flex items-center justify-center flex-shrink-0"
                :class="checkoutForm.memberId === u.id ? 'bg-blue-500 border-blue-500 text-white' : 'border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900'"
              >
                <BaseIcon v-if="checkoutForm.memberId === u.id" :path="mdiCheck" size="12" />
              </div>
            </div>
          </div>
        </div>

      </div>

      <!-- Bottom Checkout Summary & Submission -->
      <div class="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-6 rounded-2xl shadow-sm flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h4 class="text-base font-bold text-slate-900 dark:text-white">3. Verify and Complete Checkout</h4>
          <p class="text-xs text-slate-400 mt-1">Review your selections to register the active borrowing transaction.</p>
        </div>
        <div class="flex items-center gap-4 flex-wrap">
          <div v-if="checkoutForm.materialId && checkoutForm.memberId" class="text-xs space-y-1">
            <p class="text-slate-600 dark:text-slate-300">
              <strong class="text-slate-900 dark:text-white">Book:</strong> 
              {{ allPhysicalMaterials.find(m => m.id === checkoutForm.materialId)?.title }}
            </p>
            <p class="text-slate-600 dark:text-slate-300">
              <strong class="text-slate-900 dark:text-white">Patron:</strong> 
              {{ allMembers.find(u => u.id === checkoutForm.memberId)?.first_name }} {{ allMembers.find(u => u.id === checkoutForm.memberId)?.last_name }}
            </p>
          </div>
          <div v-else class="text-xs text-amber-600 dark:text-amber-400 flex items-center gap-1">
            <BaseIcon :path="mdiAlertCircle" size="14" />
            Please select both a material and a member to proceed.
          </div>

          <button
            @click="submitDirectCheckout"
            :disabled="!checkoutForm.materialId || !checkoutForm.memberId || directBorrowReq.pending.value"
            class="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-2.5 rounded-lg text-sm transition shadow-lg shadow-blue-500/10 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <BaseIcon :path="mdiCheckCircleOutline" size="18" />
            {{ directBorrowReq.pending.value ? 'Registering checkout...' : 'Register Direct Borrow' }}
          </button>
        </div>
      </div>
    </section>

    <!-- Secure Delete Confirmation Modal -->
    <div v-if="showDeleteConfirm" class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-white dark:bg-slate-900 rounded-2xl border border-slate-200 dark:border-slate-800 p-6 w-full max-w-md shadow-2xl space-y-4 animate-in fade-in zoom-in-95 duration-200">
        <div class="flex items-start gap-3">
          <div class="bg-rose-50 dark:bg-rose-950/50 p-2.5 rounded-xl text-rose-600 dark:text-rose-400">
            <BaseIcon :path={mdiAlertCircle} size="24" />
          </div>
          <div>
            <h4 class="text-base font-bold text-slate-900 dark:text-white">Secure Deletion & Inventory Recovery</h4>
            <p class="text-xs text-slate-400 mt-1">
              You are about to delete an active borrow transaction. This action will permanently remove the record and automatically restore book stock levels back to the library shelves.
            </p>
          </div>
        </div>

        <div class="space-y-2 bg-slate-50 dark:bg-slate-950 p-3 rounded-lg border border-slate-200 dark:border-slate-800">
          <p class="text-xs text-slate-500 dark:text-slate-400"><strong class="text-slate-700 dark:text-slate-200">Book Title:</strong> {{ itemToDelete?.material_title }}</p>
          <p class="text-xs text-slate-500 dark:text-slate-400"><strong class="text-slate-700 dark:text-slate-200">Patron Name:</strong> {{ itemToDelete?.member_name }}</p>
        </div>

        <div>
          <label class="block text-[10px] uppercase font-bold tracking-wider text-slate-400 mb-1">Type "restore" to authorize stock recovery</label>
          <input
            v-model="doubleConfirmText"
            type="text"
            placeholder="Type 'restore' here..."
            class="w-full border border-slate-200 dark:border-slate-800 rounded-lg p-2.5 bg-slate-50 dark:bg-slate-950 text-sm outline-none focus:ring-2 focus:ring-rose-500/20 font-bold"
          />
        </div>

        <div class="flex justify-end gap-2 pt-2">
          <button
            @click="showDeleteConfirm = false; itemToDelete = null;"
            class="px-4 py-2 text-xs font-semibold rounded-lg border border-slate-200 dark:border-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition"
          >
            Cancel
          </button>
          <button
            @click="processSecureDelete"
            :disabled="doubleConfirmText.toLowerCase() !== 'restore' || deleteReq.pending.value"
            class="px-4 py-2 text-xs font-semibold rounded-lg bg-rose-600 hover:bg-rose-700 text-white transition disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-rose-500/10"
          >
            {{ deleteReq.pending.value ? 'Restoring Stock...' : 'Confirm Stock Recovery' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* Scrollbar configurations for tables */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}
::-webkit-scrollbar-track {
  background: transparent;
}
::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.3);
  border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.5);
}
</style>
