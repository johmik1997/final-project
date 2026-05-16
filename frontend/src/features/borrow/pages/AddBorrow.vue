<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useApiRequest } from '@/composables/useApiRequest';
import { createBorrow } from '../api/borrowApi';
import { getAllMaterials } from '../../material/api/materialApi';
import { getAllUser } from '../../users/Api/UserApi';
import { getAllReservation } from '@/features/reservation/api/reservationApi';
import { useBorrow } from '../store/borrowStore';
import { secondDateFormatWithTime, toasted } from '@/utils/utils';
import BorrowForm from '../components/borrowForm.vue';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiArrowLeft, mdiAlertCircle, mdiCloseCircle } from '@mdi/js';
import { emitEntityMutation } from '@/utils/entitySync';

const router = useRouter();
const route = useRoute();
const borrowStore = useBorrow();
const req = useApiRequest();
const materialReq = useApiRequest();
const memberReq = useApiRequest();
const reservationReq = useApiRequest();

const selectedMaterial = ref(null);
const selectedMember = ref(null);
const selectedReservation = ref(null);
const errorMessage = ref('');
const borrowMode = ref('direct');
const reservationSearch = ref('');

onMounted(() => {
  loadMaterials();
  loadMembers();
  loadReservations();
});

async function loadMaterials() {
  try {
    await materialReq.send(() => getAllMaterials({ page: 1, size: 500 }, 'physical'));
  } catch (error) {
    console.error('Error loading materials:', error);
    toasted(false, 'Failed to load materials');
  }
}

async function loadMembers(search = '') {
  try {
    await memberReq.send(() => getAllUser({ page: 1, size: 50, role: 'MEMBER', search }));
  } catch (error) {
    console.error('Error loading members:', error);
    toasted(false, 'Failed to load members');
  }
}

async function loadReservations() {
  try {
    await reservationReq.send(() => getAllReservation({ page: 1, size: 200 }));
  } catch (error) {
    console.error('Error loading reservations:', error);
    toasted(false, 'Failed to load reservations');
  }
}

const materials = computed(() => {
  const payload = materialReq.response.value;
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.content)) return payload.content;
  if (Array.isArray(payload?.response)) return payload.response;
  if (Array.isArray(payload?.data)) return payload.data;
  if (payload?.results && Array.isArray(payload.results)) return payload.results;
  if (payload?.result && Array.isArray(payload.result)) return payload.result;
  return [];
});

const members = computed(() => {
  const payload = memberReq.response.value;
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.content)) return payload.content;
  if (Array.isArray(payload?.response)) return payload.response;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.data)) return payload.data;
  if (Array.isArray(payload?.result)) return payload.result;
  return [];
});

const reservations = computed(() => {
  const payload = reservationReq.response.value;
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.content)) return payload.content;
  if (Array.isArray(payload?.response)) return payload.response;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.data)) return payload.data;
  if (Array.isArray(payload?.result)) return payload.result;
  return [];
});

const activeReservations = computed(() => {
  return reservations.value.filter((row) => String(row?.status || '').toUpperCase() === 'RESERVED');
});

const filteredReservations = computed(() => {
  const query = reservationSearch.value.trim().toLowerCase();
  const rows = activeReservations.value;
  if (!query) return rows;
  return rows.filter((row) => {
    return [
      row?.member_id_number,
      row?.member_name,
      row?.material_title,
      row?.material_author,
    ]
      .filter(Boolean)
      .some((val) => String(val).toLowerCase().includes(query));
  });
});

const hasAppliedPrefill = ref(false);

function resolveMaterialId(material) {
  return material?.id || material?.uuid || material?.materialUuid;
}

function prefillSelectedMaterialFromQuery() {
  if (hasAppliedPrefill.value) return;

  const queryMaterialId = route.query?.materialId;
  if (!queryMaterialId) {
    hasAppliedPrefill.value = true;
    return;
  }

  if (materialReq.pending.value) return;

  const match = materials.value.find((row) => String(resolveMaterialId(row)) === String(queryMaterialId));
  if (match) {
    selectedMaterial.value = match;
  }
  hasAppliedPrefill.value = true;
}

watch([materials, () => materialReq.pending.value], prefillSelectedMaterialFromQuery, { immediate: true });

function resetDirectSelection() {
  selectedMaterial.value = null;
  selectedMember.value = null;
}

function resetReservationSelection() {
  selectedReservation.value = null;
}

function setBorrowMode(mode) {
  borrowMode.value = mode;
  errorMessage.value = '';
  if (mode === 'direct') {
    resetReservationSelection();
  } else {
    resetDirectSelection();
  }
}

async function handleSubmit({ material, member }) {
  errorMessage.value = '';

  if (!material || !member) {
    toasted(false, 'Please select both material and member');
    return;
  }

  req.send(
    () => createBorrow({ member: member.id, material: material.id }),
    (res) => {
      if (res?.success) {
        if (res?.data) {
          borrowStore.add(res.data);
        }
        emitEntityMutation('borrows', { action: 'created', id: res?.data?.id });
        toasted(true, 'Borrow created successfully');
        router.push('/borrows');
      } else {
        const msg = res?.error || 'Failed to create borrow';
        toasted(false, msg);
        errorMessage.value = msg;
      }
    }
  );
}

function handleReservationBorrow() {
  errorMessage.value = '';
  if (!selectedReservation.value?.id) {
    toasted(false, 'Please select a reservation');
    return;
  }

  req.send(
    () => createBorrow({ reservation: selectedReservation.value.id }),
    (res) => {
      if (res?.success) {
        if (res?.data) {
          borrowStore.add(res.data);
        }
        emitEntityMutation('borrows', { action: 'created', id: res?.data?.id });
        toasted(true, 'Borrow created successfully');
        router.push('/borrows');
      } else {
        const msg = res?.error || 'Failed to create borrow';
        toasted(false, msg);
        errorMessage.value = msg;
      }
    }
  );
}

function goBack() {
  router.push('/borrows');
}

const isLoading = computed(() => {
  return materialReq.pending.value || memberReq.pending.value || reservationReq.pending.value || req.pending.value;
});

const formattedErrorMessage = computed(() => {
  if (!errorMessage.value) return '';
  if (typeof errorMessage.value === 'string') return errorMessage.value;
  return JSON.stringify(errorMessage.value);
});
</script>

<template>
  <div class="p-4 sm:p-7">
    <div class="mb-4">
      <button
        class="text-sm text-gray-600 dark:text-gray-400 hover:text-amber-600 dark:hover:text-amber-400 flex items-center gap-2 transition-colors duration-200"
        @click="goBack"
      >
        <BaseIcon :path="mdiArrowLeft" size="18" />
        Back to Borrow List
      </button>
    </div>

    <div class="bg-white dark:bg-slate-800 rounded-2xl border border-gray-100 dark:border-slate-700 shadow-xl overflow-hidden transition-all duration-300">
      <div class="px-6 py-4 border-b border-gray-100 dark:border-slate-700 bg-gradient-to-r from-gray-50 to-white dark:from-slate-800 dark:to-slate-800">
        <h1 class="text-xl font-bold text-gray-900 dark:text-white">Borrow Materials</h1>
      </div>

      <div class="px-6 py-4">
        <div class="mb-5">
          <div class="inline-flex rounded-xl border border-gray-200 dark:border-slate-700 bg-gray-50 dark:bg-slate-900 p-1">
            <button
              class="px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200"
              :class="borrowMode === 'direct' ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-md' : 'text-gray-600 dark:text-gray-400 hover:text-amber-600 dark:hover:text-amber-400'"
              @click="setBorrowMode('direct')"
            >
              Direct Borrow
            </button>
            <button
              class="px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200"
              :class="borrowMode === 'reservation' ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-md' : 'text-gray-600 dark:text-gray-400 hover:text-amber-600 dark:hover:text-amber-400'"
              @click="setBorrowMode('reservation')"
            >
              From Reservation
            </button>
          </div>
        </div>

        <BorrowForm
          v-if="borrowMode === 'direct'"
          :materials="materials"
          :members="members"
          :selected-material="selectedMaterial"
          :selected-member="selectedMember"
          :loading="isLoading"
          @update:selectedMaterial="selectedMaterial = $event; errorMessage = ''"
          @update:selectedMember="selectedMember = $event; errorMessage = ''"
          @submit="handleSubmit"
        />

        <div v-else class="space-y-4">
          <div class="relative max-w-md">
            <input
              v-model="reservationSearch"
              type="text"
              placeholder="Search by member ID, name, or material..."
              class="w-full px-4 py-2.5 border border-gray-200 dark:border-slate-700 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-400 focus:border-amber-400 bg-white dark:bg-slate-800 text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500 transition-all duration-200"
            />
          </div>

          <div v-if="reservationReq.pending.value" class="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-xl p-4 flex items-center gap-3">
            <div class="animate-spin rounded-full h-5 w-5 border-2 border-amber-600 border-t-transparent"></div>
            <p class="text-sm text-blue-800 dark:text-blue-300">Loading reservations...</p>
          </div>

          <div v-else-if="activeReservations.length === 0" class="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-xl p-4 text-sm text-amber-800 dark:text-amber-300">
            No active reservations found.
          </div>

          <div v-else-if="filteredReservations.length === 0" class="bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-xl p-4 text-sm text-amber-800 dark:text-amber-300">
            No reservations match your search.
          </div>

          <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              v-for="resv in filteredReservations"
              :key="resv.id"
              type="button"
              class="text-left border rounded-xl p-4 shadow-sm transition-all duration-200"
              :class="selectedReservation?.id === resv.id ? 'border-amber-400 bg-amber-50 dark:bg-amber-950/50 ring-2 ring-amber-400 dark:ring-amber-600' : 'border-gray-200 dark:border-slate-700 hover:border-amber-300 dark:hover:border-amber-700 bg-white dark:bg-slate-800'"
              @click="selectedReservation = resv; errorMessage = ''"
            >
              <div class="flex items-center justify-between">
                <h3 class="font-semibold text-gray-900 dark:text-white">{{ resv.material_title || 'Untitled Material' }}</h3>
                <span class="text-xs font-semibold px-2 py-1 rounded-full bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300">
                  {{ resv.status || 'RESERVED' }}
                </span>
              </div>
              <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">{{ resv.member_name || 'Unknown Member' }}</p>
              <div class="text-xs text-gray-500 dark:text-gray-500 mt-2 space-y-1">
                <div>Expires: {{ secondDateFormatWithTime(resv.expiry_date) || '-' }}</div>
                <div>Reserved: {{ secondDateFormatWithTime(resv.reserve_date) || '-' }}</div>
              </div>
            </button>
          </div>

          <div class="flex justify-end">
            <button
              class="bg-gradient-to-r from-amber-500 to-orange-500 text-white px-6 py-2.5 rounded-xl hover:from-amber-600 hover:to-orange-600 transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
              :disabled="!selectedReservation || req.pending.value"
              @click="handleReservationBorrow"
            >
              Create Borrow
            </button>
          </div>
        </div>
      </div>

      <div v-if="errorMessage" class="mx-6 mb-4 bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 rounded-xl p-4">
        <div class="flex items-start gap-3">
          <BaseIcon :path="mdiCloseCircle" size="20" class="text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
          <div>
            <p class="text-sm font-medium text-red-800 dark:text-red-300">Error creating borrow</p>
            <p class="text-xs text-red-700 dark:text-red-400 mt-1">{{ formattedErrorMessage }}</p>
          </div>
        </div>
      </div>

      <div
        v-if="borrowMode === 'direct' && (materialReq.pending.value || memberReq.pending.value)"
        class="mx-6 mb-4 bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-xl p-4 flex items-center gap-3"
      >
        <div class="animate-spin rounded-full h-5 w-5 border-2 border-amber-600 border-t-transparent"></div>
        <p class="text-sm text-blue-800 dark:text-blue-300">Loading library catalog...</p>
      </div>

      <div
        v-if="borrowMode === 'direct' && !materialReq.pending.value && materials.length === 0"
        class="mx-6 mb-4 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-xl p-4 flex items-center gap-3"
      >
        <BaseIcon :path="mdiAlertCircle" size="20" class="text-amber-600 dark:text-amber-400" />
        <p class="text-sm text-amber-800 dark:text-amber-300">No materials available. Please add materials to the catalog first.</p>
      </div>

      <div
        v-if="borrowMode === 'direct' && !memberReq.pending.value && members.length === 0"
        class="mx-6 mb-4 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded-xl p-4 flex items-center gap-3"
      >
        <BaseIcon :path="mdiAlertCircle" size="20" class="text-amber-600 dark:text-amber-400" />
        <p class="text-sm text-amber-800 dark:text-amber-300">No members found. Please add members to the system first.</p>
      </div>
    </div>
  </div>
</template>