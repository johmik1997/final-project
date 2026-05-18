<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import BaseIcon from '@/components/base/BaseIcon.vue';
import Table from '@/components/Table.vue';
import { useApiRequest } from '@/composables/useApiRequest';
import { getAllReturns } from '@/features/returns/api/returnApi';
import { initializeFinePayment, verifyFinePayment } from '../api/paymentApi';
import { emitEntityMutation, subscribeEntityMutation } from '@/utils/entitySync';
import { secondDateFormatWithTime, toasted } from '@/utils/utils';
import { generatePaymentReceipt } from '../utils/receiptGenerator';
import {
  mdiCashFast,
  mdiRefresh,
  mdiCheckCircleOutline,
  mdiClockOutline,
  mdiAlertCircleOutline,
} from '@mdi/js';

const route = useRoute();
const router = useRouter();
const returnReq = useApiRequest();
const initReq = useApiRequest();
const verifyReq = useApiRequest();
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

function amount(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function normalizeStatus(value) {
  return String(value || '').trim().toUpperCase();
}

function loadReturns() {
  returnReq.send(() => getAllReturns({ page: 1, size: 200 }));
}

const allReturns = computed(() =>
  [...rowsFromPayload(returnReq.response.value)].sort((a, b) => new Date(b?.return_date || 0) - new Date(a?.return_date || 0))
);

const fineRows = computed(() => allReturns.value.filter((row) => amount(row?.fine_amount) > 0));
const outstandingRows = computed(() =>
  fineRows.value.filter((row) => normalizeStatus(row?.payment_status) !== 'COMPLETED')
);
const completedRows = computed(() =>
  fineRows.value.filter((row) => normalizeStatus(row?.payment_status) === 'COMPLETED')
);

const stats = computed(() => ({
  totalOutstanding: outstandingRows.value.reduce((sum, row) => sum + amount(row?.fine_amount), 0),
  paidTotal: completedRows.value.reduce((sum, row) => sum + amount(row?.fine_amount), 0),
  pendingCount: outstandingRows.value.filter((row) => normalizeStatus(row?.payment_status) === 'PENDING').length,
  settledCount: completedRows.value.length,
}));

const selectedReturnId = computed(() => {
  const id = route.query?.returnId;
  return id ? String(id) : null;
});

const autoPaymentStartedForReturn = ref(null);

function getReturnUrl() {
  const url = new URL(`${window.location.origin}/fine-payments`);
  if (selectedReturnId.value) {
    url.searchParams.set('returnId', selectedReturnId.value);
  }
  return url.toString();
}

function startPayment(row) {
  initReq.send(
    () =>
      initializeFinePayment({
        return_id: row?.id,
        return_url: getReturnUrl(),
      }),
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

function clearPaymentQuery() {
  const nextQuery = { ...route.query };
  delete nextQuery.tx_ref;
  delete nextQuery.returnId;

  if (Object.keys(nextQuery).length === 0) {
    router.replace({ path: route.path });
  } else {
    router.replace({ path: route.path, query: nextQuery });
  }
}

function clearVerificationQuery() {
  if (!route.query?.tx_ref) return;
  clearPaymentQuery();
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
      loadReturns();

      if (status === 'COMPLETED') {
        toasted(true, 'Payment verified successfully');
      } else {
        toasted(false, 'Payment was not completed', `Current status: ${status || 'FAILED'}`);
      }

      clearVerificationQuery();
    }
  );
}

function maybeStartPaymentForSelectedReturn() {
  if (!selectedReturnId.value || autoPaymentStartedForReturn.value === selectedReturnId.value) {
    return;
  }

  const selectedRow = allReturns.value.find((row) => String(row?.id) === selectedReturnId.value);
  if (!selectedRow) {
    return;
  }

  const shouldPay = amount(selectedRow?.fine_amount) > 0 && normalizeStatus(selectedRow?.payment_status) !== 'COMPLETED';
  if (!shouldPay) {
    autoPaymentStartedForReturn.value = selectedReturnId.value;
    return;
  }

  autoPaymentStartedForReturn.value = selectedReturnId.value;
  startPayment(selectedRow);
}

watch(
  () => route.query?.tx_ref,
  (txRef) => {
    if (txRef) {
      verifyPayment(txRef);
    }
  },
  { immediate: true }
);

watch(
  () => [selectedReturnId.value, returnReq.response.value],
  () => {
    maybeStartPaymentForSelectedReturn();
  },
  { immediate: true }
);

onMounted(() => {
  loadReturns();
  unsubscribeEntitySync = subscribeEntityMutation('*', ({ entity }) => {
    if (['returns', 'payments'].includes(entity)) {
      loadReturns();
    }
  });
});

function downloadReceipt(row) {
  const payment = {
    payment_intent_id: row?.payment_reference || row?.id || 'N/A',
    payment_date: row?.return_date || new Date().toISOString(),
    payment_method: 'Chapa Pay',
    amount: amount(row?.fine_amount),
    material_title: row?.material_title || row?.material || 'Library Fine Payment',
    fee_type: 'Overdue Fine',
    member_name: row?.member_name || row?.member || 'Library Patron',
    member_id_number: row?.member_id_number || 'N/A',
    library_name: row?.library_name || 'E-Book Library System'
  };
  
  toasted(true, 'Generating PDF receipt...');
  generatePaymentReceipt(payment);
}

onBeforeUnmount(() => {
  unsubscribeEntitySync?.();
});
</script>

<template>
  <div class="p-4 sm:p-7 space-y-6 dark:bg-slate-950 min-h-screen">
    <!-- Hero Section -->
    <section class="rounded-[28px] border border-slate-200 dark:border-slate-800 bg-[radial-gradient(circle_at_top_right,_rgba(251,191,36,0.28),_transparent_36%),linear-gradient(145deg,_#111827,_#0f766e_58%,_#34d399)] dark:bg-[radial-gradient(circle_at_top_right,_rgba(251,191,36,0.3),_transparent_36%),linear-gradient(145deg,_#0f172a,_#0d9488_58%,_#059669)] p-6 text-white shadow-xl">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div class="max-w-2xl">
          <p class="text-xs font-semibold uppercase tracking-[0.32em] text-emerald-100/80 dark:text-emerald-200/80">Fine Payments</p>
          <h1 class="mt-3 text-3xl font-bold tracking-tight">Settle overdue fines without leaving your workflow.</h1>
          <p class="mt-3 text-sm text-emerald-50/85 dark:text-emerald-100/85">
            Review your returned materials, see which fines are still pending, and complete payment through Chapa.
          </p>
        </div>

        <button
          class="inline-flex items-center gap-2 rounded-full bg-white/14 px-4 py-2 text-sm font-semibold text-white transition hover:bg-white/22 dark:bg-white/10 dark:hover:bg-white/20"
          @click="loadReturns"
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
            <p class="text-xs uppercase tracking-[0.22em] text-slate-400 dark:text-slate-500">Outstanding</p>
            <p class="mt-2 text-3xl font-bold text-rose-600 dark:text-rose-400">ETB {{ stats.totalOutstanding.toFixed(2) }}</p>
          </div>
          <div class="rounded-2xl bg-rose-50 dark:bg-rose-950/50 p-3 text-rose-600 dark:text-rose-400">
            <BaseIcon :path="mdiAlertCircleOutline" size="22" />
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs uppercase tracking-[0.22em] text-slate-400 dark:text-slate-500">Pending Verification</p>
            <p class="mt-2 text-3xl font-bold text-amber-600 dark:text-amber-400">{{ stats.pendingCount }}</p>
          </div>
          <div class="rounded-2xl bg-amber-50 dark:bg-amber-950/50 p-3 text-amber-600 dark:text-amber-400">
            <BaseIcon :path="mdiClockOutline" size="22" />
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs uppercase tracking-[0.22em] text-slate-400 dark:text-slate-500">Settled Fines</p>
            <p class="mt-2 text-3xl font-bold text-emerald-600 dark:text-emerald-400">{{ stats.settledCount }}</p>
          </div>
          <div class="rounded-2xl bg-emerald-50 dark:bg-emerald-950/50 p-3 text-emerald-600 dark:text-emerald-400">
            <BaseIcon :path="mdiCheckCircleOutline" size="22" />
          </div>
        </div>
      </div>

      <div class="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-sm">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-xs uppercase tracking-[0.22em] text-slate-400 dark:text-slate-500">Paid Total</p>
            <p class="mt-2 text-3xl font-bold text-slate-900 dark:text-white">ETB {{ stats.paidTotal.toFixed(2) }}</p>
          </div>
          <div class="rounded-2xl bg-slate-100 dark:bg-slate-800 p-3 text-slate-700 dark:text-slate-400">
            <BaseIcon :path="mdiCashFast" size="22" />
          </div>
        </div>
      </div>
    </section>

    <!-- Outstanding Fine Payments Table -->
    <section class="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-sm">
      <div class="flex flex-col gap-2">
        <h2 class="text-xl font-semibold text-slate-900 dark:text-white">Outstanding fine payments</h2>
        <p class="text-sm text-slate-500 dark:text-slate-400">Start a new payment or verify a pending transaction that has already been initiated.</p>
      </div>

      <div class="mt-6">
        <Table
          :pending="returnReq.pending.value || initReq.pending.value || verifyReq.pending.value"
          :rows="outstandingRows"
          :show-pagination="false"
          :headers="{
            head: ['Material', 'Returned At', 'Due Date', 'Fine Amount', 'Payment Status', 'Actions'],
            row: ['material_title', 'return_date', 'due_date', 'fine_amount', 'payment_status'],
          }"
          :cells="{
            return_date: (val) => secondDateFormatWithTime(val) || '-',
            due_date: (val) => secondDateFormatWithTime(val) || '-',
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
                :disabled="initReq.pending.value"
                @click="startPayment(row)"
              >
                Pay Now
              </button>
            </div>
          </template>
          <template #placeholder>
            <div class="rounded-2xl border border-dashed border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 p-8 text-center text-sm text-slate-500 dark:text-slate-400">
              No unpaid fines right now.
            </div>
          </template>
        </Table>
      </div>
    </section>

    <!-- Completed Payments Cards -->
    <section class="rounded-3xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-sm">
      <div class="flex flex-col gap-2">
        <h2 class="text-xl font-semibold text-slate-900 dark:text-white">Completed payments</h2>
        <p class="text-sm text-slate-500 dark:text-slate-400">A running record of fine payments that were successfully settled.</p>
      </div>

      <div class="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        <article
          v-for="row in completedRows"
          :key="row?.id || row?.uuid"
          class="rounded-2xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 p-4 shadow-sm hover:shadow-md transition-shadow"
        >
          <div class="flex items-start justify-between gap-3">
            <div>
              <h3 class="text-sm font-semibold text-slate-900 dark:text-white">{{ row?.material_title || 'Material' }}</h3>
              <p class="mt-1 text-xs text-slate-500 dark:text-slate-400">Returned {{ secondDateFormatWithTime(row?.return_date) || '-' }}</p>
            </div>
            <span class="rounded-full bg-emerald-100 dark:bg-emerald-900/50 px-2.5 py-1 text-[11px] font-semibold text-emerald-700 dark:text-emerald-400">
              Paid
            </span>
          </div>

          <div class="mt-4 space-y-2 text-sm">
            <div class="flex items-center justify-between text-slate-500 dark:text-slate-400">
              <span>Amount</span>
              <span class="font-semibold text-slate-900 dark:text-white">ETB {{ amount(row?.fine_amount).toFixed(2) }}</span>
            </div>
            <div class="flex items-center justify-between text-slate-500 dark:text-slate-400">
              <span>Reference</span>
              <span class="font-medium text-slate-800 dark:text-slate-300 font-mono text-xs">{{ row?.payment_reference || '-' }}</span>
            </div>
          </div>

          <div class="mt-4 pt-3 border-t border-slate-100 dark:border-slate-800 flex justify-end">
            <button
              @click="downloadReceipt(row)"
              class="inline-flex items-center gap-1.5 text-xs font-semibold bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-400 hover:bg-emerald-600 hover:text-white px-3 py-1.5 rounded-xl transition-all duration-200"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5M16.5 12L12 16.5m0 0L7.5 12m4.5 4.5V3"></path>
              </svg>
              <span>Download Receipt</span>
            </button>
          </div>
        </article>

        <div
          v-if="!completedRows.length && !returnReq.pending.value"
          class="rounded-2xl border border-dashed border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50 p-8 text-center text-sm text-slate-500 dark:text-slate-400 md:col-span-2 xl:col-span-3"
        >
          No completed fine payments yet.
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* Custom animations */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Smooth card transitions */
article {
  transition: all 0.2s ease;
}

article:hover {
  transform: translateY(-2px);
}
</style>