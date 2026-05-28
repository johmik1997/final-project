<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import BaseIcon from '@/components/base/BaseIcon.vue';
import Table from '@/components/Table.vue';
import { useApiRequest } from '@/composables/useApiRequest';
import { getAllBorrows } from '@/features/borrow/api/borrowApi';
import { initializeFinePayment, verifyFinePayment } from '@/features/payment/api/paymentApi';
import { createReturn, getAllReturns } from '../api/returnApi';
import { emitEntityMutation, subscribeEntityMutation } from '@/utils/entitySync';
import { secondDateFormatWithTime, toasted } from '@/utils/utils';
import {
  mdiCashMultiple,
  mdiCheckCircleOutline,
  mdiClockAlertOutline,
  mdiKeyboardReturn,
  mdiMagnify,
  mdiRefresh,
  mdiClose,
} from '@mdi/js';

const router = useRouter();
const borrowReq = useApiRequest();
const returnReq = useApiRequest();
const createReq = useApiRequest();
const paymentReq = useApiRequest();
const verifyReq = useApiRequest();
const searchQuery = ref('');
let unsubscribeEntitySync = () => {};

// Condition modal state
const showConditionModal = ref(false);
const selectedCondition = ref('GOOD');
const pendingReturnRow = ref(null);

const CONDITIONS = [
  { value: 'GOOD', label: 'Good', description: 'No damage, no fine', color: 'text-emerald-600' },
  { value: 'FAIR', label: 'Fair', description: 'Minor wear', color: 'text-yellow-600' },
  { value: 'DAMAGED', label: 'Damaged', description: 'Significant damage', color: 'text-orange-600' },
  { value: 'LOST', label: 'Lost', description: 'Material not returned', color: 'text-rose-600' },
];

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

function amount(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function loadPage() {
  borrowReq.send(() => getAllBorrows({ page: 1, size: 200 }));
  returnReq.send(() => getAllReturns({ page: 1, size: 200 }));
}

const borrows = computed(() => rowsFromPayload(borrowReq.response.value));
const returns = computed(() => rowsFromPayload(returnReq.response.value));

const settlementByBorrowId = computed(() =>
  returns.value.reduce((state, row) => {
    if (row?.borrow) {
      state[row.borrow] = row;
    }
    return state;
  }, {})
);

const activeBorrows = computed(() =>
  borrows.value.filter((row) => !row?.is_returned && ['BORROWED', 'OVERDUE'].includes(normalizeStatus(row?.status)))
);

const filteredBorrows = computed(() => {
  const query = searchQuery.value.trim().toLowerCase();
  if (!query) return activeBorrows.value;

  return activeBorrows.value.filter((row) =>
    [
      row?.material_title,
      row?.material_author,
      row?.member_name,
      row?.member_id,
      row?.library_name,
      row?.status,
    ]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(query))
  );
});

const settlementRows = computed(() =>
  [...returns.value]
    .filter((row) => amount(row?.fine_amount) > 0)
    .sort((a, b) => new Date(b?.return_date || 0) - new Date(a?.return_date || 0))
);

const pendingSettlementRows = computed(() =>
  settlementRows.value.filter((row) => normalizeStatus(row?.payment_status) !== 'COMPLETED')
);

const stats = computed(() => ({
  awaitingCheckIn: activeBorrows.value.length,
  overdue: activeBorrows.value.filter((row) => normalizeStatus(row?.status) === 'OVERDUE').length,
  unpaidSettlements: pendingSettlementRows.value.length,
  pendingFineTotal: pendingSettlementRows.value.reduce((sum, row) => sum + amount(row?.fine_amount), 0),
}));

// Fine preview calculation (client-side estimate shown in modal)
const estimatedOverdueFine = computed(() => {
  if (!pendingReturnRow.value) return 0;
  return amount(pendingReturnRow.value?.estimated_fine_amount);
});

const conditionFineNote = computed(() => {
  const cond = selectedCondition.value;
  if (cond === 'GOOD' || cond === 'NEW') return null;
  const price = amount(pendingReturnRow.value?.material_price);
  if (!price) return `Condition fine will be calculated based on material price × policy %.`;
  return null;
});

function getReturnUrl() {
  return `${window.location.origin}/returns`;
}

function openPayments(returnId = null) {
  router.push({
    path: '/fine-payments',
    query: returnId ? { returnId: String(returnId) } : {},
  });
}

function openConditionModal(row) {
  pendingReturnRow.value = row;
  selectedCondition.value = 'GOOD';
  showConditionModal.value = true;
}

function closeConditionModal() {
  showConditionModal.value = false;
  pendingReturnRow.value = null;
  selectedCondition.value = 'GOOD';
}

function confirmReturn() {
  const row = pendingReturnRow.value;
  if (!row) return;

  const conditionToSubmit = selectedCondition.value;
  closeConditionModal();

  createReq.send(
    () => createReturn({ borrow: row?.id, material_condition: conditionToSubmit }),
    (res) => {
      if (!res?.success) {
        toasted(false, 'Failed to process return', res?.error || 'Unknown error');
        return;
      }

      const data = res?.data;
      const overdueFine = amount(data?.overdue_fine);
      const conditionFine = amount(data?.condition_fine);
      const totalFine = amount(data?.fine_amount);

      emitEntityMutation('returns', { action: 'created', id: data?.id });

      if (totalFine > 0) {
        const breakdown = [
          `Overdue Fine: ETB ${overdueFine.toFixed(2)}`,
          `Condition Fine (${data?.material_condition}): ETB ${conditionFine.toFixed(2)}`,
          `Total Fine: ETB ${totalFine.toFixed(2)}`,
        ].join(' | ');
        toasted(true, `Fine settlement created. ${breakdown}`);
        openPayments(data?.id);
      } else {
        emitEntityMutation('borrows', { action: 'updated', id: row?.id, status: 'RETURNED' });
        toasted(true, 'Return recorded successfully');
      }

      loadPage();
    }
  );
}

function startPayment(row) {
  paymentReq.send(
    () => initializeFinePayment({ return_id: row?.id, return_url: getReturnUrl() }),
    (res) => {
      if (!res?.success) {
        toasted(false, 'Unable to start payment', res?.error || 'Unknown error');
        return;
      }

      const checkoutUrl = res?.data?.checkout_url;
      if (!checkoutUrl) {
        toasted(false, 'Payment provider did not return a checkout link.');
        return;
      }

      emitEntityMutation('payments', { action: 'initialized', tx_ref: res?.data?.payment?.transaction_reference });
      window.location.href = checkoutUrl;
    }
  );
}

function verifyPayment(txRef) {
  if (!txRef) return;

  verifyReq.send(
    () => verifyFinePayment(txRef),
    (res) => {
      if (!res?.success) {
        toasted(false, 'Payment verification failed', res?.error || 'Unknown error');
        return;
      }

      const status = normalizeStatus(res?.data?.payment?.status);
      emitEntityMutation('payments', { action: 'verified', tx_ref: txRef, status });
      emitEntityMutation('returns', { action: 'payment-updated', tx_ref: txRef, status });
      loadPage();

      if (status === 'COMPLETED') {
        toasted(true, 'Payment verified successfully and return finalized');
      } else {
        toasted(false, 'Payment was not completed', `Current status: ${status || 'FAILED'}`);
      }
    }
  );
}

function actionLabel(row) {
  const settlement = settlementByBorrowId.value[row?.id];
  if (settlement) {
    return normalizeStatus(settlement?.payment_status) === 'COMPLETED' ? 'Settled' : 'Await payment';
  }
  return normalizeStatus(row?.status) === 'OVERDUE' ? 'Create fine' : 'Return';
}

onMounted(() => {
  loadPage();
  unsubscribeEntitySync = subscribeEntityMutation('*', ({ entity }) => {
    if (['borrows', 'returns', 'payments'].includes(entity)) {
      loadPage();
    }
  });
});

onBeforeUnmount(() => {
  unsubscribeEntitySync?.();
});
</script>

<template>
  <div class="space-y-6 p-4 sm:p-7 dark:bg-slate-950">
    <!-- Hero Section -->
    <section class="rounded-[28px] border border-slate-200 dark:border-slate-800 bg-[linear-gradient(135deg,_rgba(245,158,11,0.15),_rgba(239,68,68,0.1))] p-6 shadow-xl">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div class="max-w-2xl">
          <p class="text-xs font-semibold uppercase tracking-[0.32em] text-slate-500 dark:text-slate-400">
            Circulation Desk
          </p>
          <h1 class="mt-3 text-3xl font-bold tracking-tight bg-gradient-to-r from-amber-500 to-yellow-400 bg-clip-text text-transparent">
            Process returns without losing the payment workflow.
          </h1>
          <p class="mt-3 text-sm text-slate-600 dark:text-slate-400">
            Select the material condition on return. Condition fines are added to any overdue fine and must be paid before the return closes.
          </p>
        </div>
        <button
          class="inline-flex items-center gap-2 rounded-full bg-amber-500 px-4 py-2 text-sm font-semibold text-white transition hover:bg-amber-600 shadow-md"
          @click="loadPage"
        >
          <BaseIcon :path="mdiRefresh" size="18" />
          Refresh
        </button>
      </div>
    </section>

    <!-- Stats Cards -->
    <section class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
      <div class="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs uppercase tracking-[0.22em] text-slate-400 dark:text-slate-500">Awaiting Check-in</p>
            <p class="mt-2 text-3xl font-bold text-slate-900 dark:text-white">{{ stats.awaitingCheckIn }}</p>
          </div>
          <div class="rounded-2xl bg-blue-50 dark:bg-blue-950/50 p-3 text-blue-700 dark:text-blue-400">
            <BaseIcon :path="mdiKeyboardReturn" size="22" />
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs uppercase tracking-[0.22em] text-slate-400 dark:text-slate-500">Overdue</p>
            <p class="mt-2 text-3xl font-bold text-amber-600 dark:text-amber-500">{{ stats.overdue }}</p>
          </div>
          <div class="rounded-2xl bg-amber-50 dark:bg-amber-950/50 p-3 text-amber-600 dark:text-amber-400">
            <BaseIcon :path="mdiClockAlertOutline" size="22" />
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs uppercase tracking-[0.22em] text-slate-400 dark:text-slate-500">Pending Settlements</p>
            <p class="mt-2 text-3xl font-bold text-rose-600 dark:text-rose-400">{{ stats.unpaidSettlements }}</p>
          </div>
          <div class="rounded-2xl bg-rose-50 dark:bg-rose-950/50 p-3 text-rose-600 dark:text-rose-400">
            <BaseIcon :path="mdiCashMultiple" size="22" />
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs uppercase tracking-[0.22em] text-slate-400 dark:text-slate-500">Outstanding Fine Total</p>
            <p class="mt-2 text-3xl font-bold text-emerald-600 dark:text-emerald-400">ETB {{ stats.pendingFineTotal.toFixed(2) }}</p>
          </div>
          <div class="rounded-2xl bg-emerald-50 dark:bg-emerald-950/50 p-3 text-emerald-600 dark:text-emerald-400">
            <BaseIcon :path="mdiCheckCircleOutline" size="22" />
          </div>
        </div>
      </div>
    </section>

    <!-- Return Queue Section -->
    <section class="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-sm">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 class="text-xl font-semibold text-slate-900 dark:text-white">Return queue</h2>
          <p class="text-sm text-slate-500 dark:text-slate-400">Select material condition on return. Condition fines are calculated from the Library Policy.</p>
        </div>

        <div class="relative w-full max-w-xl">
          <BaseIcon :path="mdiMagnify" size="18" class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 dark:text-slate-500" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by material, member, library, or status..."
            class="w-full rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 py-3 pl-10 pr-4 text-sm text-slate-700 dark:text-slate-200 outline-none transition focus:border-blue-300 dark:focus:border-blue-500 focus:bg-white dark:focus:bg-slate-800 focus:ring-2 focus:ring-blue-100 dark:focus:ring-blue-950/50"
          />
        </div>
      </div>

      <div class="mt-6">
        <Table
          :pending="borrowReq.pending.value || createReq.pending.value"
          :rows="filteredBorrows"
          :show-pagination="false"
          :headers="{
            head: ['Material', 'Member', 'Library', 'Due Date', 'Borrow Status', 'Settlement', 'Actions'],
            row: ['material_title', 'member_name', 'library_name', 'due_date', 'status', 'settlement_status'],
          }"
          :cells="{
            library_name: (val) => val || '-',
            due_date: (val) => secondDateFormatWithTime(val) || '-',
            settlement_status: (_, row) => settlementByBorrowId[row?.id]?.settlement_status || 'NOT STARTED',
          }"
        >
          <template #actions="{ row }">
            <div class="flex flex-wrap items-center justify-end gap-2">
              <template v-if="settlementByBorrowId[row?.id]">
                <button
                  class="rounded-full border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 px-3 py-1.5 text-xs font-semibold text-slate-700 dark:text-slate-300 transition hover:bg-slate-100 dark:hover:bg-slate-700"
                  @click="openPayments(settlementByBorrowId[row?.id]?.id)"
                >
                  {{ actionLabel(row) }}
                </button>
              </template>
              <button
                v-else
                class="inline-flex items-center gap-1 rounded-full bg-blue-600 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-60"
                :disabled="createReq.pending.value"
                @click="openConditionModal(row)"
              >
                <BaseIcon :path="mdiKeyboardReturn" size="14" />
                {{ actionLabel(row) }}
              </button>
            </div>
          </template>
          <template #placeholder>
            <div class="rounded-2xl border border-dashed border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 p-8 text-center text-sm text-slate-500 dark:text-slate-400">
              No active borrows are waiting to be processed.
            </div>
          </template>
        </Table>
      </div>
    </section>

    <!-- Condition & Fine Modal -->
    <Teleport to="body">
      <div
        v-if="showConditionModal"
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
        @click.self="closeConditionModal"
      >
        <div class="w-full max-w-md rounded-3xl bg-white dark:bg-slate-900 shadow-2xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          <!-- Modal Header -->
          <div class="flex items-center justify-between px-6 py-4 border-b border-slate-100 dark:border-slate-800">
            <div>
              <h3 class="text-lg font-semibold text-slate-900 dark:text-white">Process Return</h3>
              <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5 truncate max-w-xs">
                {{ pendingReturnRow?.material_title || 'Material' }} — {{ pendingReturnRow?.member_name || 'Member' }}
              </p>
            </div>
            <button
              class="rounded-full p-1.5 text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 transition"
              @click="closeConditionModal"
            >
              <BaseIcon :path="mdiClose" size="18" />
            </button>
          </div>

          <!-- Condition Selector -->
          <div class="px-6 py-5 space-y-3">
            <p class="text-sm font-medium text-slate-700 dark:text-slate-300">Select returned material condition:</p>
            <div class="grid grid-cols-2 gap-2">
              <button
                v-for="cond in CONDITIONS"
                :key="cond.value"
                class="rounded-2xl border-2 px-4 py-3 text-left transition"
                :class="selectedCondition === cond.value
                  ? 'border-blue-500 bg-blue-50 dark:bg-blue-950/40'
                  : 'border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 hover:border-slate-300 dark:hover:border-slate-600'"
                @click="selectedCondition = cond.value"
              >
                <span class="block text-sm font-semibold" :class="cond.color">{{ cond.label }}</span>
                <span class="block text-xs text-slate-500 dark:text-slate-400 mt-0.5">{{ cond.description }}</span>
              </button>
            </div>

            <!-- Fine Breakdown -->
            <div class="mt-4 rounded-2xl bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 p-4 space-y-2">
              <p class="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-slate-400">Fine Breakdown</p>

              <div class="flex justify-between text-sm text-slate-700 dark:text-slate-300">
                <span>Overdue Fine</span>
                <span class="font-medium">ETB {{ estimatedOverdueFine.toFixed(2) }}</span>
              </div>

              <div class="flex justify-between text-sm text-slate-700 dark:text-slate-300">
                <span>Condition Fine</span>
                <span class="font-medium text-slate-400 dark:text-slate-500 italic text-xs">
                  {{ selectedCondition === 'GOOD' || selectedCondition === 'NEW' ? 'ETB 0.00' : 'Calculated by server (price × policy %)' }}
                </span>
              </div>

              <div class="border-t border-slate-200 dark:border-slate-700 pt-2 flex justify-between text-sm font-semibold text-slate-900 dark:text-white">
                <span>Total Fine</span>
                <span>
                  {{ selectedCondition === 'GOOD' || selectedCondition === 'NEW'
                    ? `ETB ${estimatedOverdueFine.toFixed(2)}`
                    : `ETB ${estimatedOverdueFine.toFixed(2)} + condition fine` }}
                </span>
              </div>

              <p v-if="selectedCondition === 'LOST'" class="text-xs text-rose-600 dark:text-rose-400 mt-1">
                ⚠ LOST: Future borrowing will be disabled for this material until the fine is paid.
              </p>
              <p v-else-if="selectedCondition !== 'GOOD' && selectedCondition !== 'NEW'" class="text-xs text-amber-600 dark:text-amber-400 mt-1">
                Exact condition fine will be confirmed after submission based on material price and policy percentage.
              </p>
            </div>
          </div>

          <!-- Modal Actions -->
          <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-slate-100 dark:border-slate-800">
            <button
              class="rounded-full border border-slate-200 dark:border-slate-700 px-4 py-2 text-sm font-semibold text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition"
              @click="closeConditionModal"
            >
              Cancel
            </button>
            <button
              class="rounded-full bg-blue-600 px-5 py-2 text-sm font-semibold text-white hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 transition disabled:opacity-60 disabled:cursor-not-allowed"
              :disabled="createReq.pending.value"
              @click="confirmReturn"
            >
              Confirm Return
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
