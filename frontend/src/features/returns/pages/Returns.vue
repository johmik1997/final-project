<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { openModal } from '@customizer/modal-x';
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
} from '@mdi/js';

const router = useRouter();
const borrowReq = useApiRequest();
const returnReq = useApiRequest();
const createReq = useApiRequest();
const paymentReq = useApiRequest();
const verifyReq = useApiRequest();
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

function getReturnUrl() {
  return `${window.location.origin}/returns`;
}

function openPayments(returnId = null) {
  router.push({
    path: '/fine-payments',
    query: returnId ? { returnId: String(returnId) } : {},
  });
}

function recordReturn(row) {
  const isOverdue = normalizeStatus(row?.status) === 'OVERDUE';
  const title = isOverdue ? 'Create Fine Settlement' : 'Complete Return';
  const message = isOverdue
    ? `This borrow is overdue. Create the fine settlement for "${row?.material_title || 'this material'}" so payment can be completed before the return is finalized?`
    : `Complete the return for "${row?.material_title || 'this material'}"?`;

  openModal(
    'Confirmation',
    { title, message },
    (confirmed) => {
      if (!confirmed) return;

      createReq.send(
        () => createReturn({ borrow: row?.id }),
        (res) => {
          if (!res?.success) {
            toasted(false, 'Failed to process return', res?.error || 'Unknown error');
            return;
          }

          const fineAmount = amount(res?.data?.fine_amount);
          emitEntityMutation('returns', { action: 'created', id: res?.data?.id });

          if (fineAmount > 0) {
            toasted(true, `Fine settlement created. ETB ${fineAmount.toFixed(2)} must be paid before the return closes.`);
            openPayments(res?.data?.id);
          } else {
            emitEntityMutation('borrows', { action: 'updated', id: row?.id, status: 'RETURNED' });
            toasted(true, 'Return recorded successfully');
          }

          loadPage();
        }
      );
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
      
      <!-- Small Top Text -->
      <p class="text-xs font-semibold uppercase tracking-[0.32em] text-slate-500 dark:text-slate-400">
        Circulation Desk
      </p>

      <!-- Title -->
      <h1 class="mt-3 text-3xl font-bold tracking-tight bg-gradient-to-r from-amber-500 to-yellow-400 bg-clip-text text-transparent">
        Process returns without losing the payment workflow.
      </h1>

      <!-- Description -->
      <p class="mt-3 text-sm text-slate-600 dark:text-slate-400">
        Regular returns can close immediately. Overdue borrows create a fine settlement first, and the return only finishes after payment verification.
      </p>
    </div>

    <!-- Refresh Button -->
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
          <p class="text-sm text-slate-500 dark:text-slate-400">Overdue rows create settlement records instead of instantly closing the return.</p>
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
                @click="recordReturn(row)"
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

    <!-- Outstanding Fine Settlements Section -->
    <!-- <section class="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-sm">
      <div class="flex flex-col gap-2">
        <h2 class="text-xl font-semibold text-slate-900 dark:text-white">Outstanding fine settlements</h2>
        <p class="text-sm text-slate-500 dark:text-slate-400">These returns stay incomplete until the overdue payment is verified.</p>
      </div>

      <div class="mt-6">
        <Table
          :pending="returnReq.pending.value || paymentReq.pending.value || verifyReq.pending.value"
          :rows="pendingSettlementRows"
          :show-pagination="false"
          :headers="{
            head: ['Material', 'Member', 'Return Created', 'Fine Amount', 'Payment Status', 'Actions'],
            row: ['material_title', 'member_name', 'return_date', 'fine_amount', 'payment_status'],
          }"
          :cells="{
            return_date: (val) => secondDateFormatWithTime(val) || '-',
            fine_amount: (val) => `ETB ${amount(val).toFixed(2)}`,
          }"
        >
          <template #actions="{ row }">
            <div class="flex flex-wrap items-center justify-end gap-2">
              <button
                v-if="row?.payment_reference && row?.payment_status === 'PENDING'"
                class="rounded-full border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-950/50 px-3 py-1.5 text-xs font-semibold text-amber-700 dark:text-amber-400 transition hover:bg-amber-100 dark:hover:bg-amber-900/50"
                @click="verifyPayment(row?.payment_reference)"
              >
                Verify
              </button>
              <button
                class="rounded-full bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white transition hover:bg-emerald-700 dark:bg-emerald-500 dark:hover:bg-emerald-600 disabled:cursor-not-allowed disabled:opacity-60"
                :disabled="paymentReq.pending.value"
                @click="startPayment(row)"
              >
                Pay now
              </button>
            </div>
          </template>
          <template #placeholder>
            <div class="rounded-2xl border border-dashed border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 p-8 text-center text-sm text-slate-500 dark:text-slate-400">
              No overdue settlements are waiting for payment.
            </div>
          </template>
        </Table>
      </div>
    </section> -->
  </div>
</template>