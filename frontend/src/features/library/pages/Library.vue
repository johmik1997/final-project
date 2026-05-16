<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import Table from '@/components/Table.vue';
import { useApiRequest } from '@/composables/useApiRequest';
import { getAllLibrary, removeLibraryById } from '../api/libraryApi';
import { toasted } from '@/utils/utils';
import { openModal } from '@customizer/modal-x';
import BaseIcon from '@/components/base/BaseIcon.vue';
import {
  mdiDeleteAlert,
  mdiFilter,
  mdiLibrary,
  mdiMagnify,
  mdiMapMarker,
  mdiPhone,
  mdiPlus,
  mdiSchool,
  mdiPencil,
} from '@mdi/js';
import { usePaginations } from '@/composables/usePaginationTemp';
import { useLibrary } from '../store/libraryStore';
import { emitEntityMutation, subscribeEntityMutation } from '@/utils/entitySync';

const libraryStore = useLibrary();
let unsubscribeEntitySync = () => {};

const searchQuery = ref('');
const campusFilter = ref('');

const pagination = usePaginations({
  store: libraryStore,
  cb: getAllLibrary,
});

onMounted(() => {
  unsubscribeEntitySync = subscribeEntityMutation('libraries', () => {
    pagination.refresh();
  });
});

onBeforeUnmount(() => {
  unsubscribeEntitySync?.();
});

const removeReq = useApiRequest();

function getLibraryId(library) {
  return library?.id || library?.uuid || library?.libraryUuid;
}

function remove(id) {
  openModal(
    'Confirmation',
    {
      title: 'Remove Library',
      message: 'Are you sure you want to delete this library? This action cannot be undone.',
    },
    (confirm) => {
      if (!confirm) return;

      removeReq.send(
        () => removeLibraryById(id),
        (res) => {
          if (res.success) {
            libraryStore.remove(id);
            emitEntityMutation('libraries', { action: 'deleted', id });
            toasted(true, 'Library removed successfully');
          } else {
            toasted(false, 'Failed to remove library', res.error);
          }
        }
      );
    }
  );
}

const uniqueCampuses = computed(() => {
  const libraries = libraryStore.libraries || [];
  return Array.from(new Set(libraries.map((library) => library?.campus).filter(Boolean))).sort();
});

const filteredLibraries = computed(() => {
  let libraries = libraryStore.libraries || [];

  if (campusFilter.value) {
    libraries = libraries.filter((library) => library?.campus === campusFilter.value);
  }

  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim();
    libraries = libraries.filter((library) =>
      library?.name?.toLowerCase().includes(query) ||
      library?.location?.toLowerCase().includes(query) ||
      library?.campus?.toLowerCase().includes(query) ||
      library?.phone?.includes(query)
    );
  }

  return libraries;
});

const stats = computed(() => {
  const libraries = libraryStore.libraries || [];

  return {
    total: libraries.length,
    campuses: new Set(libraries.map((library) => library?.campus).filter(Boolean)).size,
    withPhone: libraries.filter((library) => library?.phone).length,
  };
});

const hasActiveFilters = computed(() => Boolean(searchQuery.value || campusFilter.value));

function clearFilters() {
  searchQuery.value = '';
  campusFilter.value = '';
}
</script>

<template>
  <div class="libraries-page">
    <section class="library-hero">
      <div class="flex flex-col gap-5 lg:flex-row lg:items-end lg:justify-between">
        <div class="max-w-2xl">
          <div class="mb-3 flex items-center gap-2">
            <div class="rounded-xl bg-white/20 p-2 backdrop-blur-sm">
              <BaseIcon :path="mdiLibrary" size="20" class="text-white" />
            </div>
            <p class="text-xs font-semibold uppercase tracking-[0.32em] text-white/80">Branch Directory</p>
          </div>

          <h1 class="text-3xl font-bold tracking-tight text-white">Library Management</h1>
          <p class="mt-3 text-sm text-white/85">
            Manage campus branches, keep contact details accurate, and make each library easier to find across the
            reservation and borrowing workflows.
          </p>
        </div>

        <button
          @click="openModal('AddLibrary')"
          class="inline-flex items-center justify-center gap-2 rounded-xl bg-white/20 px-5 py-3 text-sm font-semibold text-white backdrop-blur-sm transition-all hover:scale-[1.02] hover:bg-white/30"
        >
          <BaseIcon :path="mdiPlus" size="18" />
          <span>Add New Library</span>
        </button>
      </div>
    </section>

    <section class="grid grid-cols-1 gap-4 md:grid-cols-3">
      <div class="stat-card tone-amber">
        <div class="stat-card-copy">
          <p class="stat-label">Total Libraries</p>
          <p class="stat-value text-amber-600 dark:text-amber-400">{{ stats.total }}</p>
          <p class="stat-description">Registered library branches</p>
        </div>
        <div class="stat-icon tone-amber-icon">
          <BaseIcon :path="mdiLibrary" size="22" />
        </div>
      </div>

      <div class="stat-card tone-blue">
        <div class="stat-card-copy">
          <p class="stat-label">Campuses</p>
          <p class="stat-value text-blue-600 dark:text-blue-400">{{ stats.campuses }}</p>
          <p class="stat-description">Distinct campus locations</p>
        </div>
        <div class="stat-icon tone-blue-icon">
          <BaseIcon :path="mdiSchool" size="22" />
        </div>
      </div>

      <div class="stat-card tone-green">
        <div class="stat-card-copy">
          <p class="stat-label">With Contact</p>
          <p class="stat-value text-emerald-600 dark:text-emerald-400">{{ stats.withPhone }}</p>
          <p class="stat-description">Libraries with phone numbers</p>
        </div>
        <div class="stat-icon tone-green-icon">
          <BaseIcon :path="mdiPhone" size="22" />
        </div>
      </div>
    </section>

    <section class="panel-surface">
      <div class="panel-header">
        <div>
          <h2 class="panel-title">Search & Filters</h2>
          <p class="panel-subtitle">Find libraries by branch name, campus, location, or contact phone</p>
        </div>
      </div>

      <div class="panel-body">
        <div class="grid grid-cols-1 gap-4 lg:grid-cols-[minmax(0,1fr)_240px_auto]">
          <div class="relative">
            <BaseIcon
              :path="mdiMagnify"
              size="18"
              class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-slate-500"
            />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search by name, location, campus, or phone..."
              class="filter-input pl-10 w-3/4"
            />
          </div>

          <div class="relative">
            <BaseIcon
              :path="mdiFilter"
              size="18"
              class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-slate-500"
            />
            <select v-model="campusFilter" class="filter-input pl-10">
              <option value="">All Campuses</option>
              <option v-for="campus in uniqueCampuses" :key="campus" :value="campus">{{ campus }}</option>
            </select>
          </div>

          <button
            v-if="hasActiveFilters"
            @click="clearFilters"
            class="inline-flex items-center justify-center rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm font-semibold text-amber-700 transition-colors hover:bg-amber-100 dark:border-amber-900 dark:bg-amber-950/30 dark:text-amber-300 dark:hover:bg-amber-950/50"
          >
            Clear Filters
          </button>
        </div>

        <div v-if="campusFilter" class="mt-4 flex items-center gap-2">
          <span class="text-xs text-gray-500 dark:text-slate-400">Active filter:</span>
          <span class="inline-flex items-center gap-1 rounded-lg bg-amber-100 px-2.5 py-1 text-xs font-medium text-amber-700 dark:bg-amber-900/60 dark:text-amber-300">
            <BaseIcon :path="mdiSchool" size="12" />
            {{ campusFilter }}
          </span>
        </div>
      </div>
    </section>

    <section class="panel-surface overflow-hidden">
      <div class="panel-header">
        <div>
          <h2 class="panel-title">Library Directory</h2>
          <p class="panel-subtitle">Browse and maintain the list of library branches available in the system</p>
        </div>
      </div>

      <div class="panel-table">
        <Table
          :pending="pagination.pending.value"
          :headers="{
            head: ['Library Name', 'Location', 'Contact Phone', 'Campus', 'Actions'],
            row: ['name', 'location', 'phone', 'campus'],
          }"
          :rows="filteredLibraries"
          :pagination="pagination.meta.value"
          @next-page="pagination.next"
          @prev-page="pagination.previous"
          @page-change="pagination.goToPage"
          @page-size-change="pagination.setPerPage"
        >
          <template #cell-name="{ value }">
            <div class="flex items-center gap-2">
              <div class="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-amber-100 to-orange-100 dark:from-amber-950/50 dark:to-orange-950/40">
                <BaseIcon :path="mdiLibrary" size="14" class="text-amber-600 dark:text-amber-400" />
              </div>
              <span class="font-medium text-gray-900 dark:text-white">{{ value || '-' }}</span>
            </div>
          </template>

          <template #cell-location="{ value }">
            <div class="flex items-center gap-1.5">
              <BaseIcon :path="mdiMapMarker" size="14" class="text-gray-400 dark:text-slate-500" />
              <span class="text-gray-700 dark:text-slate-300">{{ value || '-' }}</span>
            </div>
          </template>

          <template #cell-phone="{ value }">
            <div v-if="value" class="flex items-center gap-1.5">
              <BaseIcon :path="mdiPhone" size="14" class="text-gray-400 dark:text-slate-500" />
              <span class="font-mono text-sm text-gray-700 dark:text-slate-300">{{ value }}</span>
            </div>
            <span v-else class="text-sm text-gray-400 dark:text-slate-500">-</span>
          </template>

          <template #cell-campus="{ value }">
            <span class="inline-flex items-center gap-1 rounded-lg bg-blue-50 px-2 py-1 text-xs text-blue-700 dark:bg-blue-950/50 dark:text-blue-300">
              <BaseIcon :path="mdiSchool" size="12" />
              {{ value || '-' }}
            </span>
          </template>

          <template #actions="{ row }">
            <div class="flex justify-center gap-2">
              <button
                class="group relative rounded-lg bg-amber-50 p-2 text-amber-600 transition-all duration-200 hover:bg-gradient-to-r hover:from-amber-500 hover:to-orange-500 hover:text-white dark:bg-amber-950/50 dark:text-amber-400"
                title="Edit Library"
                @click="openModal('EditLibrary', { library: row })"
              >
                <BaseIcon :path="mdiPencil" size="18" />
                <span class="action-tooltip">Edit</span>
              </button>

              <button
                class="group relative rounded-lg bg-red-50 p-2 text-red-600 transition-all duration-200 hover:bg-red-600 hover:text-white dark:bg-red-950/50 dark:text-red-400"
                title="Delete Library"
                @click="remove(getLibraryId(row))"
              >
                <BaseIcon :path="mdiDeleteAlert" size="18" />
                <span class="action-tooltip">Delete</span>
              </button>
            </div>
          </template>

          <template #placeholder>
            <div class="py-12 text-center">
              <div class="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-2xl bg-gray-100 dark:bg-slate-800">
                <BaseIcon :path="mdiLibrary" size="32" class="text-gray-400 dark:text-slate-500" />
              </div>
              <p class="font-medium text-gray-600 dark:text-slate-300">No libraries found</p>
              <p class="mt-1 text-sm text-gray-400 dark:text-slate-500">Click "Add New Library" to get started</p>
            </div>
          </template>
        </Table>
      </div>
    </section>
  </div>
</template>

<style scoped>
.libraries-page {
  @apply space-y-6 p-4 sm:p-7;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 45%, #fff7ed 100%);
  min-height: 100%;
}

.dark .libraries-page {
  background: linear-gradient(135deg, #0f172a 0%, #111827 45%, #1f2937 100%);
}

.library-hero {
  @apply rounded-3xl p-6 shadow-xl;
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 45%, #ef4444 100%);
}

.stat-card {
  @apply flex items-center justify-between rounded-2xl border p-5 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:shadow-md;
  @apply border-gray-200 bg-white dark:border-slate-700 dark:bg-slate-900/90;
}

.tone-amber {
  @apply bg-gradient-to-br from-white to-amber-50 dark:from-slate-900 dark:to-amber-950/20;
}

.tone-blue {
  @apply bg-gradient-to-br from-white to-blue-50 dark:from-slate-900 dark:to-blue-950/20;
}

.tone-green {
  @apply bg-gradient-to-br from-white to-emerald-50 dark:from-slate-900 dark:to-emerald-950/20;
}

.stat-card-copy {
  @apply space-y-1;
}

.stat-label {
  @apply text-xs font-semibold uppercase tracking-[0.22em] text-gray-500 dark:text-slate-400;
}

.stat-value {
  @apply text-3xl font-bold;
}

.stat-description {
  @apply text-sm text-gray-500 dark:text-slate-400;
}

.stat-icon {
  @apply flex h-12 w-12 items-center justify-center rounded-2xl border;
}

.tone-amber-icon {
  @apply border-amber-200 bg-amber-100 text-amber-600 dark:border-amber-900 dark:bg-amber-950/50 dark:text-amber-400;
}

.tone-blue-icon {
  @apply border-blue-200 bg-blue-100 text-blue-600 dark:border-blue-900 dark:bg-blue-950/50 dark:text-blue-400;
}

.tone-green-icon {
  @apply border-emerald-200 bg-emerald-100 text-emerald-600 dark:border-emerald-900 dark:bg-emerald-950/50 dark:text-emerald-400;
}

.panel-surface {
  @apply overflow-hidden rounded-3xl border border-gray-200 bg-white/95 shadow-sm backdrop-blur-sm dark:border-slate-700 dark:bg-slate-900/95;
}

.panel-header {
  @apply border-b border-gray-200 bg-gradient-to-r from-gray-50 to-white px-6 py-5 dark:border-slate-700 dark:from-slate-900 dark:to-slate-900;
}

.panel-title {
  @apply text-xl font-semibold text-gray-900 dark:text-white;
}

.panel-subtitle {
  @apply mt-1 text-sm text-gray-500 dark:text-slate-400;
}

.panel-body {
  @apply p-6;
}

.panel-table {
  @apply p-3 sm:p-5;
}

.filter-input {
  @apply w-3/4 rounded-xl border border-gray-200 bg-white px-4 py-3 text-gray-900 outline-none transition-all duration-200;
  @apply focus:border-amber-400 focus:ring-2 focus:ring-amber-400/20 dark:border-slate-700 dark:bg-slate-900 dark:text-slate-100;
  @apply dark:placeholder:text-slate-500;
}

.action-tooltip {
  @apply pointer-events-none absolute -top-8 left-1/2 -translate-x-1/2 whitespace-nowrap rounded bg-gray-800 px-2 py-1 text-xs text-white opacity-0 transition-opacity;
}

.group:hover .action-tooltip {
  opacity: 1;
  transition-delay: 0.2s;
}

:deep(.table-row:hover) {
  background-color: rgba(245, 158, 11, 0.05);
}

:deep(.dark .table-row:hover) {
  background-color: rgba(245, 158, 11, 0.1);
}

:deep(.table-container::-webkit-scrollbar) {
  width: 6px;
  height: 6px;
}

:deep(.table-container::-webkit-scrollbar-track) {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 10px;
}

:deep(.dark .table-container::-webkit-scrollbar-track) {
  background: rgba(255, 255, 255, 0.05);
}

:deep(.table-container::-webkit-scrollbar-thumb) {
  background: rgba(245, 158, 11, 0.4);
  border-radius: 10px;
}

:deep(.table-container::-webkit-scrollbar-thumb:hover) {
  background: rgba(245, 158, 11, 0.6);
}
</style>
