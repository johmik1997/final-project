<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import BaseIcon from '@/components/base/BaseIcon.vue';
import BorrowHeader from '@/features/borrow/components/BorrowHeader.vue';
import MaterialCard from '@/features/borrow/components/MaterialCard.vue';
import { useApiRequest } from '@/composables/useApiRequest';
import { getAllMaterials } from '@/features/material/api/materialApi';
import { createReservation, getAllReservation } from '@/features/reservation/api/reservationApi';
import { useReservation } from '@/features/reservation/store/reservationStore';
import { useAuth } from '@/stores/auth';
import { toasted } from '@/utils/utils';
import { mdiMagnify, mdiClose, mdiAlertCircle } from '@mdi/js';
import ReservationStepNav from '../components/ReservationStepNav.vue';
import ReservationDetailsCard from '../components/ReservationDetailsCard.vue';
import ReservationHistoryTable from '../components/ReservationHistoryTable.vue';
import { emitEntityMutation, subscribeEntityMutation } from '@/utils/entitySync';

const auth = useAuth();
const route = useRoute();
const reservationStore = useReservation();

const materialReq = useApiRequest();
const reservationReq = useApiRequest();
const listReq = useApiRequest();

const searchQuery = ref('');
const viewMode = ref('grid');
const activeView = ref('reserve');
const selectedMaterial = ref(null);
const reserveDate = ref('');
const hasAppliedPrefill = ref(false);
let unsubscribeEntitySync = () => {};

onMounted(() => {
  materialReq.send(() => getAllMaterials({ page: 1, size: 500 }, 'physical'));
  refreshReservations();
  unsubscribeEntitySync = subscribeEntityMutation('reservations', () => {
    refreshReservations();
  });
});

onBeforeUnmount(() => {
  unsubscribeEntitySync?.();
});

function refreshReservations() {
  listReq.send(() => getAllReservation({ page: 1, size: 200 }));
}

function normalizeString(value) {
  return String(value || '').trim().toLowerCase();
}

function resolveMaterialId(row) {
  return row?.id || row?.uuid || row?.materialUuid;
}

function sameId(a, b) {
  if (a === null || a === undefined || b === null || b === undefined) return false;
  return String(a) === String(b);
}

const currentUser = computed(() => auth?.auth?.user || {});

function getCurrentUserId() {
  const user = currentUser.value || {};
  return user?.id || user?.user_id || user?.userId || user?.uuid || null;
}

const materials = computed(() => {
  const payload = materialReq.response.value;
  if (!payload) return [];

  let rows = [];
  if (Array.isArray(payload)) rows = payload;
  else if (Array.isArray(payload?.content)) rows = payload.content;
  else if (Array.isArray(payload?.response)) rows = payload.response;
  else if (Array.isArray(payload?.data)) rows = payload.data;
  else if (Array.isArray(payload?.results)) rows = payload.results;
  else if (Array.isArray(payload?.result)) rows = payload.result;

  return rows.map((item) => {
    const total = Number(item?.total_copies || 0);
    const availableRaw = item?.available_copies;
    const available = Number(availableRaw ?? total ?? 0);

    return {
      ...item,
      total_copies: Number.isNaN(total) ? 0 : total,
      available_copies: Number.isNaN(available) ? 0 : available,
    };
  });
});

const stats = computed(() => ({
  total: materials.value.length,
  available: materials.value.filter((m) => Number(m?.available_copies || 0) > 0).length,
  borrowed: materials.value.filter((m) => {
    const total = Number(m?.total_copies || 0);
    const available = Number(m?.available_copies || 0);
    return total - available > 0;
  }).length,
  categories: new Set(materials.value.map((m) => m?.category).filter(Boolean)).size,
}));

const filteredMaterials = computed(() => {
  const rows = materials.value || [];
  const q = normalizeString(searchQuery.value);
  if (!q) return rows;

  return rows.filter((m) => {
    return [m?.title, m?.author, m?.isbn, m?.category]
      .filter(Boolean)
      .some((val) => normalizeString(val).includes(q));
  });
});

const reservableMaterials = computed(() => {
  return filteredMaterials.value.filter((m) => Number(m?.available_copies || 0) <= 0);
});

function applyPrefillMaterialFromQuery() {
  if (hasAppliedPrefill.value) return;

  const queryMaterialId = route.query?.materialId;
  if (!queryMaterialId) {
    hasAppliedPrefill.value = true;
    return;
  }

  if (materialReq.pending.value) return;

  const match = materials.value.find((row) => String(resolveMaterialId(row)) === String(queryMaterialId));
  if (!match) {
    hasAppliedPrefill.value = true;
    return;
  }

  if (Number(match?.available_copies || 0) > 0) {
    toasted(false, 'This material is available now. Please borrow it instead of reserving.');
    hasAppliedPrefill.value = true;
    return;
  }

  selectedMaterial.value = match;
  activeView.value = 'reserve';
  hasAppliedPrefill.value = true;
}

watch([materials, () => materialReq.pending.value], applyPrefillMaterialFromQuery, { immediate: true });

const rawReservations = computed(() => {
  const payload = listReq.response.value;
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.content)) return payload.content;
  if (Array.isArray(payload?.response)) return payload.response;
  if (Array.isArray(payload?.data)) return payload.data;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.result)) return payload.result;
  return reservationStore.reservations || [];
});

function belongsToCurrentMember(row) {
  const user = currentUser.value || {};
  const currentUserId = getCurrentUserId();

  const rowIds = [
    row?.member,
    row?.member_id,
    row?.memberId,
    row?.member_uuid,
    row?.member?.id,
    row?.member?.uuid,
    row?.user,
    row?.user_id,
    row?.userId,
    row?.created_by,
  ];

  if (currentUserId && rowIds.some((id) => sameId(id, currentUserId))) return true;

  const currentIdNumber = user?.id_number || user?.idNumber;
  const rowIdNumber = row?.member_id_number || row?.member?.id_number || row?.member?.idNumber;
  if (currentIdNumber && rowIdNumber && sameId(currentIdNumber, rowIdNumber)) return true;

  const currentName = normalizeString(`${user?.first_name || ''} ${user?.last_name || ''}`);
  const rowName = normalizeString(row?.member_name || row?.member?.full_name || row?.member?.name);
  if (currentName && rowName && rowName.includes(currentName)) return true;

  const hasMemberMarkers = rowIds.some((id) => id !== undefined && id !== null) || Boolean(rowIdNumber || rowName);
  return !hasMemberMarkers;
}

const myReservations = computed(() => {
  return (rawReservations.value || [])
    .filter((row) => belongsToCurrentMember(row))
    .sort((a, b) => {
      const aDate = new Date(a?.reserve_date || a?.created_at || 0).getTime();
      const bDate = new Date(b?.reserve_date || b?.created_at || 0).getTime();
      return bDate - aDate;
    });
});

function clearSearch() {
  searchQuery.value = '';
}

function selectMaterial(material) {
  if (Number(material?.available_copies || 0) > 0) {
    toasted(false, 'This material is available now. Please borrow it instead of reserving.');
    return;
  }
  selectedMaterial.value = material;
}

function resetSelection() {
  selectedMaterial.value = null;
  reserveDate.value = '';
}

function switchToReserve() {
  activeView.value = 'reserve';
}

function switchToHistory() {
  activeView.value = 'history';
}

function submitReservation() {
  if (!selectedMaterial.value?.id) {
    toasted(false, 'Please select a material first');
    return;
  }

  if (!reserveDate.value) {
    toasted(false, 'Please choose a reservation date');
    return;
  }

  const payload = {
    material_id: selectedMaterial.value.id,
    status: 'RESERVED',
    reserve_date: reserveDate.value,
  };

  reservationReq.send(
    () => createReservation(payload),
    (res) => {
      if (res?.success) {
        const created = {
          ...(res?.data || {}),
          material_title: res?.data?.material_title || selectedMaterial.value?.title,
          material_author: res?.data?.material_author || selectedMaterial.value?.author,
          reserve_date: res?.data?.reserve_date || reserveDate.value,
        };

        if (res?.data) reservationStore.add(created);
        emitEntityMutation('reservations', { action: 'created', id: created?.id });
        toasted(true, 'Reservation created successfully');
        resetSelection();
        refreshReservations();
        switchToHistory();
      } else {
        toasted(false, res?.error || 'Failed to create reservation');
      }
    }
  );
}
</script>

<template>
  <div class="p-4 sm:p-7">
    <div class="mb-6">
      <BorrowHeader :stats="stats" v-model:viewMode="viewMode" />
    </div>

  <div class="mb-6 bg-white p-1.5 rounded-2xl border border-gray-100 shadow-sm">
  <div class="grid grid-cols-2 gap-2">
    <button
      @click="switchToReserve"
      class="px-4 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200"
      :class="activeView === 'reserve' 
        ? 'bg-gray-900 text-white shadow-md' 
        : 'bg-transparent text-gray-500 hover:bg-gray-100 hover:text-gray-900'"
    >
      Reserve Material
    </button>

    <button
      @click="switchToHistory"
      class="px-4 py-2.5 rounded-xl text-sm font-semibold transition-all duration-200"
      :class="activeView === 'history' 
        ? 'bg-gray-900 text-white shadow-md' 
        : 'bg-transparent text-gray-500 hover:bg-gray-100 hover:text-gray-900'"
    >
      View History
    </button>
  </div>
</div>

    <div v-if="activeView === 'reserve'" class="mb-6">
      <ReservationStepNav :has-selection="Boolean(selectedMaterial)" :has-date="Boolean(reserveDate)" />
    </div>

    <div v-if="activeView === 'reserve'" class="mb-6">
      <div v-if="!selectedMaterial" class="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
        <div class="mb-4">
          <h1 class="text-2xl font-bold text-gray-900">Reserve Material</h1>
          <p class="text-sm text-gray-500">Choose a material card to continue.</p>
        </div>

       <div class="relative w-full max-w-xl mb-5">
  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
    <BaseIcon :path="mdiMagnify" size="20" class="text-gray-400" />
  </div>

  <input
    v-model="searchQuery"
    type="text"
    placeholder="Search by title, author, ISBN, or category..."
    class="w-full pl-10 pr-10 py-2.5 bg-gray-50 border border-gray-200 rounded-xl text-sm transition-all duration-200 
           focus:bg-white focus:ring-4 focus:ring-blue-50 focus:border-blue-400 focus:outline-none"
  />
</div>

        <div v-if="materialReq.pending.value" class="bg-blue-50 border border-blue-200 rounded-lg p-4 flex items-center gap-3">
          <div class="animate-spin rounded-full h-5 w-5 border-2 border-blue-600 border-t-transparent"></div>
          <p class="text-sm text-blue-800">Loading materials...</p>
        </div>

        <div v-else-if="filteredMaterials.length === 0" class="bg-amber-50 border border-amber-200 rounded-lg p-6 text-center">
          <BaseIcon :path="mdiAlertCircle" size="28" class="text-amber-600 mx-auto mb-2" />
          <p class="text-sm text-amber-800">No materials found for your search.</p>
        </div>

        <div v-else-if="reservableMaterials.length === 0" class="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <BaseIcon :path="mdiAlertCircle" size="28" class="text-blue-600 mx-auto mb-2" />
          <p class="text-sm text-blue-800">No unavailable materials to reserve right now.</p>
          <p class="text-xs text-blue-700 mt-1">Available materials can be borrowed directly.</p>
        </div>

        <div v-else>
          <div v-if="viewMode === 'grid'" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            <MaterialCard
              v-for="item in reservableMaterials"
              :key="item.id"
              :material="item"
              :is-selected="selectedMaterial?.id === item.id"
              :select-unavailable-only="true"
              :view-mode="viewMode"
              @select="selectMaterial"
            />
          </div>

          <div v-else class="overflow-x-auto rounded-xl border border-gray-200 bg-white">
            <table class="min-w-full text-sm">
              <thead class="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th class="text-left px-4 py-3 font-semibold text-gray-700">Title</th>
                  <th class="text-left px-4 py-3 font-semibold text-gray-700">Author</th>
                  <th class="text-left px-4 py-3 font-semibold text-gray-700">Category</th>
                  <th class="text-left px-4 py-3 font-semibold text-gray-700">Available</th>
                  <th class="text-left px-4 py-3 font-semibold text-gray-700">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in reservableMaterials"
                  :key="item.id"
                  class="border-b border-gray-100 hover:bg-blue-50/40 transition-colors"
                  :class="selectedMaterial?.id === item.id ? 'bg-blue-50' : ''"
                >
                  <td class="px-4 py-3 font-medium text-gray-900">{{ item.title || 'Untitled' }}</td>
                  <td class="px-4 py-3 text-gray-600">{{ item.author || '-' }}</td>
                  <td class="px-4 py-3 text-gray-600">{{ item.category || 'General' }}</td>
                  <td class="px-4 py-3 text-gray-700">{{ item.available_copies || 0 }}</td>
                  <td class="px-4 py-3">
                    <button
                      class="text-xs px-3 py-1.5 rounded-lg font-medium"
                      :class="item.available_copies <= 0 ? 'bg-blue-600 text-white hover:bg-blue-700' : 'bg-gray-200 text-gray-500 cursor-not-allowed'"
                      :disabled="item.available_copies > 0"
                      @click="selectMaterial(item)"
                    >
                      {{ selectedMaterial?.id === item.id ? 'Selected' : 'Select' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-else class="max-w-3xl mx-auto">
        <ReservationDetailsCard
          :selected-material="selectedMaterial"
          :reserve-date="reserveDate"
          :submitting="reservationReq.pending.value"
          @update:reserveDate="reserveDate = $event"
          @submit="submitReservation"
          @change-material="resetSelection"
        />
      </div>
    </div>

    <ReservationHistoryTable v-if="activeView === 'history'" :rows="myReservations" :loading="listReq.pending.value" />
  </div>
</template>
