<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, watch } from 'vue';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { useApiRequest } from '@/composables/useApiRequest';
import { getAllLibrary } from '../api/libraryApi';
import {
  createLibraryPolicy,
  getAllLibraryPolicies,
  updateLibraryPolicyById,
} from '../api/policyApi';
import { emitEntityMutation, subscribeEntityMutation } from '@/utils/entitySync';
import { secondDateFormatWithTime, toasted } from '@/utils/utils';
import {
  mdiCalendarSyncOutline,
  mdiCashClock,
  mdiCheckCircle,
  mdiCloseCircle,
  mdiCogOutline,
  mdiLibrary,
  mdiPencil,
  mdiPlus,
  mdiRefresh,
  mdiShieldCheckOutline,
  mdiAlertCircle,
} from '@mdi/js';

const policiesReq = useApiRequest();
const librariesReq = useApiRequest();
const saveReq = useApiRequest();
let unsubscribeEntitySync = () => {};

const defaultForm = () => ({
  id: null,
  name: 'Global Library Policy',
  is_active: true,
  borrow_duration_days: 7,
  max_active_borrows: 3,
  reservation_hold_hours: 24,
  overdue_daily_rate: 0,
  fair_condition_penalty_percent: 10,
  damaged_condition_penalty_percent: 35,
  lost_condition_penalty_percent: 100,
  grace_period_days: 0,
  notes: '',
});

const form = reactive(defaultForm());

function rowsFromPayload(payload, key = null) {
  if (!payload) return [];
  if (key && Array.isArray(payload?.[key])) return payload[key];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.result)) return payload.result; // FIXED: changed from 'results' to 'result'
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.data)) return payload.data;
  return [];
}

function normalizeNumber(value, fallback = 0) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

const policies = computed(() => rowsFromPayload(policiesReq.response.value));
const libraries = computed(() => rowsFromPayload(librariesReq.response.value, 'libraries'));

// Get ALL global policies (library === null)
const globalPolicies = computed(() => {
  const allPolicies = policies.value;
  return allPolicies.filter((row) => row?.library === null || row?.library === undefined);
});

// Use the first global policy (there should be only one)
const globalPolicy = computed(() => globalPolicies.value[0] || null);

// Check if any global policy exists
const hasExistingPolicy = computed(() => globalPolicies.value.length > 0);

// Check if multiple policies exist (error state)
const hasMultiplePolicies = computed(() => globalPolicies.value.length > 1);

// Editing mode: true if a policy exists
const isEditing = computed(() => hasExistingPolicy.value);

// Make name field readonly when editing
const isNameEditable = computed(() => !hasExistingPolicy.value);

const stats = computed(() => ({
  librariesCovered: libraries.value.length,
  activeRate: normalizeNumber(globalPolicy.value?.overdue_daily_rate),
  activeBorrowWindow: normalizeNumber(globalPolicy.value?.borrow_duration_days),
  activeBorrowLimit: normalizeNumber(globalPolicy.value?.max_active_borrows),
}));

const lastUpdatedAt = computed(() => globalPolicy.value?.updated_at || globalPolicy.value?.created_at || null);

function assignDefaultForm() {
  Object.assign(form, defaultForm());
}

function hydrateForm(row) {
  if (!row) {
    assignDefaultForm();
    return;
  }
  
  Object.assign(form, {
    id: row.id,
    name: row.name || 'Global Library Policy',
    is_active: row.is_active === undefined ? true : Boolean(row.is_active),
    borrow_duration_days: normalizeNumber(row.borrow_duration_days, 7),
    max_active_borrows: normalizeNumber(row.max_active_borrows, 3),
    reservation_hold_hours: normalizeNumber(row.reservation_hold_hours, 24),
    overdue_daily_rate: normalizeNumber(row.overdue_daily_rate, 0),
    fair_condition_penalty_percent: normalizeNumber(row.fair_condition_penalty_percent, 10),
    damaged_condition_penalty_percent: normalizeNumber(row.damaged_condition_penalty_percent, 35),
    lost_condition_penalty_percent: normalizeNumber(row.lost_condition_penalty_percent, 100),
    grace_period_days: normalizeNumber(row.grace_period_days, 0),
    notes: row.notes || '',
  });
}

function loadPage() {
  policiesReq.send(() => getAllLibraryPolicies({ page: 1, size: 100 }));
  librariesReq.send(() => getAllLibrary({ page: 1, size: 200 }));
}

function hydrateGlobalPolicy() {
  if (globalPolicy.value) {
    hydrateForm(globalPolicy.value);
  } else {
    assignDefaultForm();
  }
}

function resetForm() {
  hydrateGlobalPolicy();
}

function buildPayload() {
  const payload = {
    library: null,
    name: form.name?.trim() || 'Global Library Policy',
    is_active: Boolean(form.is_active),
    borrow_duration_days: normalizeNumber(form.borrow_duration_days, 7),
    max_active_borrows: normalizeNumber(form.max_active_borrows, 3),
    reservation_hold_hours: normalizeNumber(form.reservation_hold_hours, 24),
    overdue_daily_rate: normalizeNumber(form.overdue_daily_rate, 0),
    fair_condition_penalty_percent: normalizeNumber(form.fair_condition_penalty_percent, 10),
    damaged_condition_penalty_percent: normalizeNumber(form.damaged_condition_penalty_percent, 35),
    lost_condition_penalty_percent: normalizeNumber(form.lost_condition_penalty_percent, 100),
    grace_period_days: normalizeNumber(form.grace_period_days, 0),
    notes: form.notes?.trim() || '',
  };
  
  // If updating existing policy, remove name from payload or keep it (backend might ignore it)
  // But we'll keep it as is since the field is disabled in UI
  
  return payload;
}

function savePolicy() {
  // CRITICAL: If a global policy exists, ALWAYS update it
  if (hasExistingPolicy.value) {
    const existingPolicyId = globalPolicy.value?.id;
    
    if (!existingPolicyId) {
      toasted(false, 'Error', 'Cannot find existing policy ID to update');
      return;
    }
    
    const payload = buildPayload();
    
    saveReq.send(
      () => updateLibraryPolicyById(existingPolicyId, payload),
      (res) => {
        if (!res?.success) {
          toasted(false, 'Failed to update global library policy', res?.error || 'Unknown error');
          return;
        }

        toasted(true, 'Global library policy updated successfully');
        emitEntityMutation('library-policies', {
          action: 'updated',
          id: existingPolicyId,
        });
        loadPage();
      }
    );
  } else {
    // ONLY create if NO policy exists
    const payload = buildPayload();
    
    saveReq.send(
      () => createLibraryPolicy(payload),
      (res) => {
        if (!res?.success) {
          // Check if backend says policy already exists
          const errorMsg = res?.error?.toLowerCase() || '';
          const responseStatus = res?.status;
          
          if (errorMsg.includes('already exists') || errorMsg.includes('global policy') || responseStatus === 400) {
            toasted(false, 'Policy already exists', 'A global policy already exists. Refreshing...');
            loadPage(); // Reload to get the existing policy
          } else {
            toasted(false, 'Failed to create global library policy', res?.error || 'Unknown error');
          }
          return;
        }

        toasted(true, 'Global library policy created successfully');
        emitEntityMutation('library-policies', {
          action: 'created',
          id: res?.data?.id,
        });
        loadPage();
      }
    );
  }
}

// Function to clean up multiple policies (optional - call this manually if needed)
function cleanupMultiplePolicies() {
  if (hasMultiplePolicies.value) {
    console.error('Multiple global policies detected:', globalPolicies.value);
    toasted(false, 'Multiple global policies detected!', 'Please contact admin to delete extra policies. Only the first policy will be used.', 10000);
  }
}

onMounted(() => {
  loadPage();
  unsubscribeEntitySync = subscribeEntityMutation('*', ({ entity }) => {
    if (['libraries', 'library-policies'].includes(entity)) {
      loadPage();
    }
  });
});

watch(
  () => policiesReq.response.value,
  () => {
    hydrateGlobalPolicy();
    cleanupMultiplePolicies();
  },
  { immediate: true }
);

onBeforeUnmount(() => {
  unsubscribeEntitySync?.();
});
</script>

<template>
  <div class="library-policy-page">
    <section class="policy-hero">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div class="max-w-2xl">
          <div class="mb-3 flex items-center gap-2">
            <div class="rounded-xl bg-white/20 p-2 backdrop-blur-sm">
              <BaseIcon :path="mdiShieldCheckOutline" size="20" class="text-white" />
            </div>
            <p class="text-xs font-semibold uppercase tracking-[0.32em] text-white/80">Shared Rules</p>
          </div>

          <h1 class="text-3xl font-bold tracking-tight text-white">Global Library Policy</h1>
          <p class="mt-3 text-sm text-white/85">
            Maintain one borrowing and fine policy that applies across every library in the system. Once created, the
            same policy stays loaded here so super admins can update it in place.
          </p>
        </div>

        <button
          class="inline-flex items-center gap-2 rounded-xl bg-white/20 px-5 py-2.5 text-sm font-semibold text-white backdrop-blur-sm transition-all hover:bg-white/30"
          @click="loadPage"
        >
          <BaseIcon :path="mdiRefresh" size="18" />
          Refresh
        </button>
      </div>
    </section>

    <!-- Warning for multiple policies -->
    <section
      v-if="hasMultiplePolicies"
      class="rounded-2xl border border-red-200 bg-gradient-to-r from-red-50 to-red-100 p-4 shadow-sm dark:border-red-800 dark:from-red-950/30 dark:to-red-950/20"
    >
      <div class="flex items-start gap-3">
        <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-red-500 text-white shadow-md">
          <BaseIcon :path="mdiAlertCircle" size="18" />
        </div>
        <div>
          <p class="text-sm font-semibold text-red-800 dark:text-red-300">Multiple global policies detected!</p>
          <p class="mt-1 text-xs text-red-700 dark:text-red-400">
            There are {{ globalPolicies.length }} global policies. This can cause conflicts. Please delete the extra policies and keep only one.
          </p>
        </div>
      </div>
    </section>

    <section class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
      <div class="policy-stat-card">
        <div class="flex items-center justify-between">
          <div>
            <p class="policy-stat-label">Libraries Covered</p>
            <p class="mt-2 text-3xl font-bold text-gray-900 dark:text-white">{{ stats.librariesCovered }}</p>
          </div>
          <div class="policy-stat-icon bg-amber-100 text-amber-600 dark:bg-amber-950 dark:text-amber-400">
            <BaseIcon :path="mdiLibrary" size="22" />
          </div>
        </div>
      </div>

      <div class="policy-stat-card">
        <div class="flex items-center justify-between">
          <div>
            <p class="policy-stat-label">Daily Fine Rate</p>
            <p class="mt-2 text-3xl font-bold text-red-600 dark:text-red-400">ETB {{ stats.activeRate.toFixed(2) }}</p>
          </div>
          <div class="policy-stat-icon bg-red-100 text-red-600 dark:bg-red-950 dark:text-red-400">
            <BaseIcon :path="mdiCashClock" size="22" />
          </div>
        </div>
      </div>

      <div class="policy-stat-card">
        <div class="flex items-center justify-between">
          <div>
            <p class="policy-stat-label">Borrow Window</p>
            <p class="mt-2 text-3xl font-bold text-amber-600 dark:text-amber-400">{{ stats.activeBorrowWindow }} days</p>
          </div>
          <div class="policy-stat-icon bg-amber-100 text-amber-600 dark:bg-amber-950 dark:text-amber-400">
            <BaseIcon :path="mdiCalendarSyncOutline" size="22" />
          </div>
        </div>
      </div>

      <div class="policy-stat-card">
        <div class="flex items-center justify-between">
          <div>
            <p class="policy-stat-label">Max Borrow Limit</p>
            <p class="mt-2 text-3xl font-bold text-emerald-600 dark:text-emerald-400">{{ stats.activeBorrowLimit }}</p>
          </div>
          <div class="policy-stat-icon bg-emerald-100 text-emerald-600 dark:bg-emerald-950 dark:text-emerald-400">
            <BaseIcon :path="mdiCogOutline" size="22" />
          </div>
        </div>
      </div>
    </section>

    <section
      v-if="hasExistingPolicy"
      class="rounded-2xl border border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50 p-4 shadow-sm dark:border-amber-800 dark:from-amber-950/30 dark:to-orange-950/20"
    >
      <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div class="flex items-start gap-3">
          <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-md">
            <BaseIcon :path="mdiCheckCircle" size="18" />
          </div>

          <div>
            <p class="text-sm font-semibold text-amber-800 dark:text-amber-300">Active policy: {{ globalPolicy?.name }}</p>
            <p class="mt-1 text-xs text-amber-700 dark:text-amber-400">
              This policy is currently active and applies to all libraries in the system.
            </p>
            <p v-if="lastUpdatedAt" class="mt-2 text-xs text-amber-700 dark:text-amber-400">
              Last updated: {{ secondDateFormatWithTime(lastUpdatedAt) }}
            </p>
          </div>
        </div>

        <button
          @click="resetForm"
          class="inline-flex items-center gap-2 rounded-xl bg-amber-100 px-4 py-2 text-sm font-semibold text-amber-700 transition-colors hover:bg-amber-200 dark:bg-amber-900 dark:text-amber-300 dark:hover:bg-amber-800"
        >
          <BaseIcon :path="mdiPencil" size="16" />
          Reload Saved Values
        </button>
      </div>
    </section>

    <section class="policy-panel">
      <div class="policy-panel-header">
        <div class="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div class="mb-1 flex items-center gap-2">
              <div class="rounded-lg bg-gradient-to-r from-amber-500 to-orange-500 p-1.5">
                <BaseIcon :path="isEditing ? mdiPencil : mdiPlus" size="16" class="text-white" />
              </div>
              <h2 class="text-xl font-semibold text-gray-900 dark:text-white">
                {{ isEditing ? 'Update Global Policy' : 'Create Global Policy' }}
              </h2>
            </div>
            <p class="text-sm text-gray-500 dark:text-slate-400">
              Super admins maintain one shared configuration for borrowing limits, fines, and reservation timing.
            </p>
          </div>

          <button
            class="inline-flex items-center gap-2 rounded-xl border border-gray-300 px-4 py-2 text-sm font-semibold text-gray-700 transition-all hover:bg-gray-50 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800"
            @click="resetForm"
          >
            <BaseIcon :path="mdiCloseCircle" size="16" />
            {{ hasExistingPolicy ? 'Reset to Saved Policy' : 'Reset Form' }}
          </button>
        </div>
      </div>

      <div class="policy-panel-body">
        <div class="mb-6 rounded-2xl border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-950/30">
          <div class="flex items-start gap-3">
            <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300">
              <BaseIcon :path="mdiAlertCircle" size="18" />
            </div>
            <div>
              <p class="text-sm font-semibold text-blue-800 dark:text-blue-300">Global policy coverage</p>
              <p class="mt-1 text-xs text-blue-700 dark:text-blue-400">
                Leave this policy active to let every library use the same borrowing window, reservation hold, and
                fine settings.
              </p>
            </div>
          </div>
        </div>

        <div class="grid grid-cols-1 gap-6 md:grid-cols-2">
          <div class="md:col-span-2">
            <label class="policy-label">
              <span class="flex items-center gap-2">
                <BaseIcon :path="mdiLibrary" size="16" class="text-amber-500" />
                Policy Name
                <span class="text-red-500">*</span>
                <span v-if="!isNameEditable" class="ml-2 text-xs text-gray-500">(Read-only after creation)</span>
              </span>
            </label>
            <input
              v-model="form.name"
              type="text"
              class="policy-input"
              :class="{ 'bg-gray-100 cursor-not-allowed dark:bg-slate-800': !isNameEditable }"
              :readonly="!isNameEditable"
              :disabled="!isNameEditable"
              placeholder="e.g., Global Library Policy"
            />
          </div>

          <div>
            <label class="policy-label">
              Borrow Duration
              <span class="policy-unit">(days)</span>
            </label>
            <input v-model="form.borrow_duration_days" type="number" min="1" class="policy-input" />
          </div>

          <div>
            <label class="policy-label">
              Max Active Borrows
              <span class="policy-unit">(items)</span>
            </label>
            <input v-model="form.max_active_borrows" type="number" min="1" class="policy-input" />
          </div>

          <div>
            <label class="policy-label">
              Reservation Hold
              <span class="policy-unit">(hours)</span>
            </label>
            <input v-model="form.reservation_hold_hours" type="number" min="1" class="policy-input" />
          </div>

          <div>
            <label class="policy-label">
              Grace Period
              <span class="policy-unit">(days)</span>
            </label>
            <input v-model="form.grace_period_days" type="number" min="0" class="policy-input" />
          </div>

          <div class="md:col-span-2">
            <label class="policy-label">
              Overdue Daily Rate
              <span class="policy-unit">(ETB)</span>
            </label>
            <input v-model="form.overdue_daily_rate" type="number" min="0" step="0.01" class="policy-input" />
          </div>

          <div class="md:col-span-2 rounded-2xl border border-amber-200 bg-amber-50/60 p-4 dark:border-amber-800 dark:bg-amber-950/20">
            <p class="mb-3 flex items-center gap-2 text-sm font-semibold text-gray-900 dark:text-white">
              <BaseIcon :path="mdiAlertCircle" size="16" class="text-amber-500" />
              Material Condition Penalties (% of replacement cost)
            </p>

            <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
              <div>
                <label class="policy-mini-label">Fair Condition</label>
                <input
                  v-model="form.fair_condition_penalty_percent"
                  type="number"
                  min="0"
                  max="100"
                  step="0.01"
                  class="policy-input policy-input-sm"
                />
              </div>

              <div>
                <label class="policy-mini-label">Damaged Condition</label>
                <input
                  v-model="form.damaged_condition_penalty_percent"
                  type="number"
                  min="0"
                  max="100"
                  step="0.01"
                  class="policy-input policy-input-sm"
                />
              </div>

              <div>
                <label class="policy-mini-label">Lost Condition</label>
                <input
                  v-model="form.lost_condition_penalty_percent"
                  type="number"
                  min="0"
                  max="100"
                  step="0.01"
                  class="policy-input policy-input-sm"
                />
              </div>
            </div>
          </div>

          <div class="md:col-span-2">
            <label class="policy-label">Additional Notes</label>
            <textarea
              v-model="form.notes"
              rows="4"
              class="policy-input"
              placeholder="Optional instructions for library staff about how this policy should be applied..."
            ></textarea>
          </div>

          <div class="md:col-span-2">
            <label class="flex cursor-pointer items-center gap-3">
              <input
                v-model="form.is_active"
                type="checkbox"
                class="h-5 w-5 rounded border-gray-300 text-amber-600 focus:ring-2 focus:ring-amber-500 dark:border-slate-600"
              />
              <span class="text-sm text-gray-700 dark:text-slate-300">Set this policy as active</span>
            </label>
            <p class="ml-8 mt-1 text-xs text-gray-500 dark:text-slate-400">
              The shared global policy should stay active so all libraries continue using the same rules.
            </p>
          </div>
        </div>
      </div>

      <div class="policy-panel-actions">
        <button
          class="policy-primary-btn"
          :disabled="saveReq.pending.value"
          @click="savePolicy"
        >
          <BaseIcon :path="mdiCheckCircle" size="18" />
          {{ saveReq.pending.value ? 'Saving...' : (isEditing ? 'Update Policy' : 'Create Policy') }}
        </button>

        <button class="policy-secondary-btn" @click="resetForm">
          <BaseIcon :path="mdiCloseCircle" size="18" />
          {{ hasExistingPolicy ? 'Reset to Saved Policy' : 'Reset Form' }}
        </button>
      </div>
    </section>
  </div>
</template>

<style scoped>
.library-policy-page {
  @apply space-y-6 p-4 sm:p-7;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 45%, #fff7ed 100%);
  min-height: 100%;
}

.dark .library-policy-page {
  background: linear-gradient(135deg, #0f172a 0%, #111827 45%, #1f2937 100%);
}

.policy-hero {
  @apply rounded-3xl p-6 text-white shadow-xl;
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 45%, #ef4444 100%);
}

.policy-stat-card {
  @apply rounded-2xl border border-gray-200 bg-white p-5 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:shadow-md;
  @apply dark:border-slate-700 dark:bg-slate-900/95;
}

.policy-stat-label {
  @apply text-xs uppercase tracking-[0.22em] text-gray-500 dark:text-slate-400;
}

.policy-stat-icon {
  @apply rounded-xl p-3;
}

.policy-panel {
  @apply overflow-hidden rounded-3xl border border-gray-200 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-900/95;
}

.policy-panel-header {
  @apply border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white px-6 py-5 dark:border-slate-700 dark:from-slate-900 dark:to-slate-900;
}

.policy-panel-body {
  @apply p-6;
}

.policy-panel-actions {
  @apply flex flex-col gap-3 border-t border-gray-200 bg-gray-50/50 px-6 py-4 dark:border-slate-700 dark:bg-slate-950/40 sm:flex-row;
}

.policy-label {
  @apply mb-2 block text-sm font-semibold text-gray-700 dark:text-slate-300;
}

.policy-unit {
  @apply text-xs font-normal text-gray-500 dark:text-slate-400;
}

.policy-mini-label {
  @apply mb-1 block text-xs font-medium text-gray-600 dark:text-slate-400;
}

.policy-input {
  @apply w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-gray-900 outline-none transition-all duration-200;
  @apply focus:border-amber-400 focus:ring-2 focus:ring-amber-400/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100;
  @apply dark:placeholder:text-slate-500;
}

.policy-input-sm {
  @apply rounded-lg px-3 py-2;
}

.policy-primary-btn {
  @apply inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 px-6 py-2.5 text-sm font-semibold text-white shadow-md transition-all duration-300 hover:from-amber-600 hover:to-orange-600 disabled:cursor-not-allowed disabled:opacity-60;
}

.policy-secondary-btn {
  @apply inline-flex items-center justify-center gap-2 rounded-xl border border-gray-300 px-6 py-2.5 text-sm font-semibold text-gray-700 transition-all hover:bg-gray-100 dark:border-slate-600 dark:text-slate-300 dark:hover:bg-slate-800;
}

input[type='number']::-webkit-inner-spin-button,
input[type='number']::-webkit-outer-spin-button {
  opacity: 0.5;
}

input[type='number']:hover::-webkit-inner-spin-button,
input[type='number']:hover::-webkit-outer-spin-button {
  opacity: 1;
}

input:read-only, input:disabled {
  cursor: not-allowed;
  opacity: 0.85;
}
</style>