<script setup>
import DataTable from "./DataTable.vue";
import { inject, ref, useAttrs, watch, computed } from "vue";
import GenericTableRow from "./GenericTableRow.vue";
import icons from "@/utils/icons";
import TableRowSkeleton from "./TableRowSkeleton.vue";

const emit = defineEmits([
  "row",
  "action:certificate",
  "action:delete",
  "action:review",
  "action:suspend",
  "action:edit",
  "bottom",
  "page-change",
  "next-page",
  "prev-page",
  "page-size-change"
]);

const props = defineProps({
  showPagination: {
    type: Boolean,
    default: true,
  },
  rowCom: Object,
  actionHide: String,
  headers: [Array, Object],
  rows: {
    type: Array,
    default: [],
  },
  firstCol: { type: Boolean, default: false },
  placeholder: String,
  photoRow: Object,
  cells: Object,
  actions: Array,
  exceptions: Array,
  length: Number,
  Fallback: {
    type: Object,
    default: TableRowSkeleton
  },
  pending: Boolean,
  // Pagination props
  pagination: {
    type: Object,
    default: () => ({})
  },
  // Current page for external control
  currentPage: {
    type: Number,
    default: 1
  }
});

// Computed properties for pagination
const currentPage = computed(() => {
  return props.pagination?.number !== undefined ? props.pagination.number + 1 : props.currentPage;
});

const totalPages = computed(() => {
  return props.pagination?.totalPages || 1;
});

const totalElements = computed(() => {
  return props.pagination?.totalElements || props.rows?.length || 0;
});

const pageSize = computed(() => {
  return props.pagination?.size || props.pagination?.pageSize || 25;
});

// Selected page size
const selectedPageSize = ref(pageSize.value);

function toUpper(str) {
  let words = str.split(" ");
  if (words.length == 0) return str;

  for (let i = 1; i < words.length; i++) {
    words[0] += words[i].charAt(0).toUpperCase() + words[i].substring(1);
  }

  return words[0];
}

const spec = ref({ head: [], row: [] });

function format() {
  if (Array.isArray(props.headers)) {
    spec.value.head = props.headers;

    const res = props.headers.reduce((state, el) => {
      const temp = el.toLowerCase();
      state.push(toUpper(temp));
      return state;
    }, []);

    spec.value.row = res.filter((el) => el != "modify");
  } else {
    spec.value.head = props.headers?.head || [];
    spec.value.row = props.headers?.row || [];
  }
}

format();

function getUrl(blob) {
  if (blob.toString().includes("File")) {
    const url = URL.createObjectURL(blob);
    return url;
  }

  return blob;
}

watch(props, () => {
  format();
  // Update selected page size if it changes from parent
  if (props.pagination?.size !== undefined) {
    selectedPageSize.value = props.pagination.size;
  }
});

// Check if there's data to show
const hasData = computed(() => {
  return props.rows?.length > 0;
});

// Pagination functions
function goToNextPage() {
  if (currentPage.value < totalPages.value) {
    emit('next-page');
    emit('page-change', currentPage.value + 1);
  }
}

function goToPrevPage() {
  if (currentPage.value > 1) {
    emit('prev-page');
    emit('page-change', currentPage.value - 1);
  }
}

function goToPage(page) {
  if (page >= 1 && page <= totalPages.value) {
    emit('page-change', page);
  }
}

function changePageSize(size) {
  selectedPageSize.value = size;
  emit('page-size-change', size);
}

// Helper function to generate number ranges
function range(start, end) {
  const result = [];
  for (let i = start; i <= end; i++) {
    result.push(i);
  }
  return result;
}

// Generate page numbers for pagination
const pageNumbers = computed(() => {
  const pages = [];
  const maxVisiblePages = 5;
  const startPage = Math.max(1, currentPage.value - Math.floor(maxVisiblePages / 2));
  const endPage = Math.min(totalPages.value, startPage + maxVisiblePages - 1);
  
  for (let i = startPage; i <= endPage; i++) {
    pages.push(i);
  }
  
  return pages;
});

function getCellValue(row, key) {
  return key.split(".").reduce((all, el) => all?.[el], row);
}

function renderCell(row, key) {
  if (!props.cells?.[key]) {
    return getCellValue(row, key) ?? "-";
  }

  if (typeof props.cells[key] === "function") {
    return props.cells[key](getCellValue(row, key), row);
  }

  return getCellValue(row, key) ?? "-";
}
</script>
<template>
  <div class="modern-table-container">
    <!-- Mobile Card View (visible on small screens) -->
    <div class="block lg:hidden space-y-4">
      <!-- Loading State for Mobile -->
      <div v-if="pending" class="space-y-4">
        <div
          v-for="num in 3"
          :key="num"
          class="rounded-lg border bg-white p-4 shadow-sm animate-pulse dark:border-slate-700 dark:bg-slate-900"
        >
          <div class="space-y-3">
            <div class="h-4 bg-gray-200 rounded w-3/4"></div>
            <div class="h-3 bg-gray-200 rounded w-1/2"></div>
            <div class="h-3 bg-gray-200 rounded w-2/3"></div>
          </div>
        </div>
      </div>

      <!-- Mobile Cards -->
      <div v-else-if="rows?.length" class="space-y-4">
        <div 
          v-for="(row, index) in rows" 
          :key="index"
          class="rounded-lg border border-gray-100 bg-white p-4 shadow-sm transition-shadow hover:shadow-md dark:border-slate-700 dark:bg-slate-900"
          @click="emit('row', row)"
        >
          <div class="space-y-3">
            <!-- Display key fields -->
            <div v-for="(key, keyIndex) in spec.row.slice(0, 3)" :key="keyIndex" class="flex justify-between items-start">
              <span class="text-xs font-medium uppercase tracking-wide text-gray-500 dark:text-slate-400">
                {{ spec.head[keyIndex] || key }}
              </span>
              <span class="ml-2 flex-1 text-right text-sm font-medium text-gray-900 dark:text-white">
                <template v-if="cells && cells[key] && cells[key].com">
                  <component :is="cells[key].com" :row="row" :key="key" />
                </template>
                <template v-else>
                  {{ renderCell(row, key) }}
                </template>
              </span>
            </div>
            
            <!-- Actions -->
            <div class="pt-2 border-t border-gray-100">
              <slot name="actions" :row="row" />
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State for Mobile -->
      <div class="rounded-lg border border-gray-100 bg-white p-8 text-center shadow-sm dark:border-slate-700 dark:bg-slate-900" v-else>
        <slot name="placeholder">
          <div class="empty-state">
            <div class="empty-icon mx-auto mb-4" v-html="icons.no_data" />
            <h3 class="empty-title text-lg font-semibold text-gray-700 mb-2">No Data Available</h3>
            <p class="empty-subtitle text-gray-500">{{ placeholder || 'There are no items to display at the moment.' }}</p>
          </div>
        </slot>
      </div>
    </div>

    <!-- Desktop Table View (hidden on small screens) -->
    <div class="hidden lg:block table-card">
      <div class="overflow-x-auto">
        <DataTable
          :firstCol="props.firstCol"
          class="modern-table"
          :headers="spec.head"
        >
          <template v-if="firstCol" #headerFirst>
            <slot name="headerFirst" />
          </template>
       <slot name="row">
  <template v-if="rowCom">
    <component
      :is="rowCom"
      v-bind="{
        cells: cells,
        headKeys: spec.head,
        rowData: rows,
        rowKeys: spec.row,
      }"
    />
  </template>

  <template v-else>
    <GenericTableRow
      @row="(row) => emit('row', row)"
      :firstCol="props.firstCol"
      :head-keys="spec.head"
      :row-data="rows"
      :row-keys="spec.row"
      :cells="cells"
    >
      <!-- Select Column -->
      <template v-if="firstCol" #select="{ row }">
        <slot name="select" :row="row" />
      </template>

      <!-- Actions Column -->
      <template #actions="{ row }">
        <td class="w-[110px] min-w-[110px] whitespace-nowrap text-left">
          <slot name="actions" :row="row" />
        </td>
      </template>

      <!-- Reason Column -->
      <template #reason="{ row }">
        <slot name="reason" :row="row" />
      </template>
    </GenericTableRow>

    <!-- Empty State for Desktop -->
    <tr v-if="!rows?.length && !pending" class="empty-state-row">
      <td :colspan="spec.head.length + 1" class="empty-state-cell">
        <slot name="placeholder">
          <div class="empty-state">
            <div class="empty-icon" v-html="icons.no_data" />

            <h3 class="empty-title">
              No Data Available
            </h3>

            <p class="empty-subtitle">
              {{ placeholder || 'There are no items to display at the moment.' }}
            </p>
          </div>
        </slot>
      </td>
    </tr>

  </template>
</slot>
          
          <!-- Loading State for Desktop -->
          <template v-if="pending">
            <component
              :cols="spec.head.length + 1"
              :key="num"
              v-for="num in 8"
              :is="Fallback"
            />
          </template>
        </DataTable>
      </div>
    </div>

    <!-- Enhanced Pagination with the requested format -->
    <div
      v-if="!pending && showPagination && hasData"
      class="mt-4 flex flex-wrap items-center justify-between gap-4 rounded-lg border border-gray-100 bg-white p-4 dark:border-slate-700 dark:bg-slate-900"
    >
      <div class="flex gap-5 items-center">
        <span class="text-gray-600 dark:text-slate-300">Show</span>
        <select
          @change="changePageSize(parseInt($event.target.value))"
          class="rounded-md border border-gray-300 bg-gray-100 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
          v-model="selectedPageSize"
        >
          <option value="25">25</option>
          <option value="50">50</option>
          <option value="75">75</option>
          <option value="100">100</option>
        </select>
        <span class="text-gray-600 dark:text-slate-300">entries</span>
      </div>

      <div class="text-gray-600 dark:text-slate-300">
        Showing {{ rows?.length || 0 }} of {{ totalElements || 0 }} records
      </div>

      <div class="flex gap-2 items-center justify-center flex-wrap">
        <button
          @click="goToPrevPage"
          class="pagination-button"
          :disabled="currentPage === 1 || pending"
        >
          <i v-html="icons.chevron_left"></i>
        </button>

        <template v-if="totalPages <= 7">
          <button
            v-for="pageNum in totalPages"
            :key="pageNum"
            @click="goToPage(pageNum)"
            class="pagination-button"
            :class="{ 'active-page': currentPage === pageNum }"
          >
            {{ pageNum }}
          </button>
        </template>

        <template v-else>
          <button
            @click="goToPage(1)"
            class="pagination-button"
            :class="{ 'active-page': currentPage === 1 }"
          >
            1
          </button>

          <template v-if="currentPage < 4">
            <button
              v-for="pageNum in range(2, 4)"
              :key="pageNum"
              @click="goToPage(pageNum)"
              class="pagination-button"
              :class="{ 'active-page': currentPage === pageNum }"
            >
              {{ pageNum }}
            </button>
            <span class="px-2">...</span>
          </template>

          <template v-else-if="currentPage > totalPages - 3">
            <span class="px-2">...</span>
            <button
              v-for="pageNum in range(totalPages - 3, totalPages - 1)"
              :key="pageNum"
              @click="goToPage(pageNum)"
              class="pagination-button"
              :class="{ 'active-page': currentPage === pageNum }"
            >
              {{ pageNum }}
            </button>
          </template>

          <template v-else>
            <span class="px-2">...</span>
            <button
              v-for="pageNum in [currentPage - 1, currentPage, currentPage + 1]"
              :key="pageNum"
              @click="goToPage(pageNum)"
              class="pagination-button"
              :class="{ 'active-page': currentPage === pageNum }"
            >
              {{ pageNum }}
            </button>
            <span class="px-2">...</span>
          </template>

          <button
            @click="goToPage(totalPages)"
            class="pagination-button"
            :class="{ 'active-page': currentPage === totalPages }"
          >
            {{ totalPages }}
          </button>
        </template>

        <button
          @click="goToNextPage"
          class="pagination-button"
          :disabled="currentPage === totalPages || pending"
        >
          <i v-html="icons.chevron_right"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modern-table-container {
  @apply w-full space-y-4;
  overflow: visible !important;
}

.table-card {
  @apply bg-white rounded-xl shadow-sm border border-gray-100;
  overflow: visible !important;
}

.dark .table-card {
  @apply bg-slate-900 border-slate-700;
}

.modern-table {
  @apply w-full;
  overflow: visible !important;
}

/* Table layout fix for actions column */
:deep(.modern-table table) {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
}

:deep(.modern-table th:last-child),
:deep(.modern-table td:last-child) {
  width: 100px;
  min-width: 100px;
  max-width: 100px;
  text-align: left !important;
}

:deep(.modern-table th:first-child),
:deep(.modern-table td:first-child) {
  text-align: left;
}

:deep(.modern-table td:last-child .actions-wrapper) {
  display: flex;
  justify-content: flex-start;
  align-items: center;
}

/* CRITICAL FIX: Dark mode base table styles */
.dark .modern-table :deep(table) {
  @apply bg-slate-900;
}

.dark .modern-table :deep(thead) {
  @apply bg-slate-800;
}

.dark .modern-table :deep(th) {
  @apply text-slate-200 border-slate-700 font-semibold bg-slate-800;
}

/* FIX: Normal row styles (non-hover) */
.dark .modern-table :deep(tbody tr) {
  @apply border-b border-slate-800 bg-slate-900;
}

.dark .modern-table :deep(tbody tr:nth-child(even)) {
  @apply bg-slate-900/80;
}

.dark .modern-table :deep(tbody tr:nth-child(odd)) {
  @apply bg-slate-900;
}

/* FIX: Cell styles for better visibility */
.dark .modern-table :deep(td) {
  @apply text-slate-200 border-slate-800;
}

/* Hover state - keep this as is */
.dark .modern-table :deep(tbody tr:hover) {
  @apply bg-slate-800;
}

.dark .modern-table :deep(tbody tr:hover td) {
  @apply text-slate-100;
}

/* Pagination button styles */
.pagination-button {
  @apply w-8 h-8 flex items-center justify-center rounded-md border border-gray-300 text-sm font-medium transition-colors duration-200;
}

.pagination-button:not(:disabled) {
  @apply text-gray-700 bg-white hover:bg-gray-100;
}

.dark .pagination-button:not(:disabled) {
  @apply border-slate-600 bg-slate-800 text-slate-200 hover:bg-slate-700;
}

.pagination-button:disabled {
  @apply text-gray-400 bg-gray-50 cursor-not-allowed;
}

.dark .pagination-button:disabled {
  @apply border-slate-700 bg-slate-900 text-slate-500;
}

.pagination-button.active-page {
  @apply bg-blue-600 text-white border-blue-600;
}

.dark .pagination-button.active-page {
  @apply bg-blue-500 border-blue-500;
}

/* Empty State Styles */
.empty-state-row {
  @apply bg-gray-50/50;
}

.dark .empty-state-row {
  @apply bg-slate-900/60;
}

.empty-state-cell {
  @apply p-12 text-center;
}

.empty-state {
  @apply flex flex-col items-center justify-center space-y-4 max-w-md mx-auto;
}

.empty-icon {
  @apply w-16 h-16 lg:w-20 lg:h-20 text-gray-300;
}

.dark .empty-icon {
  @apply text-slate-600;
}

.empty-title {
  @apply text-lg lg:text-xl font-semibold text-gray-700;
}

.dark .empty-title {
  @apply text-slate-200;
}

.empty-subtitle {
  @apply text-sm lg:text-base text-gray-500 text-center leading-relaxed;
}

.dark .empty-subtitle {
  @apply text-slate-400;
}

/* Mobile Card View Dark Mode */
.dark .rounded-lg.border {
  @apply border-slate-700;
}

.dark .bg-white {
  @apply bg-slate-900;
}

.dark .text-gray-900 {
  @apply text-slate-100;
}

.dark .text-gray-500 {
  @apply text-slate-400;
}

.dark .border-gray-100 {
  @apply border-slate-700;
}

.dark .bg-gray-200 {
  @apply bg-slate-700;
}

/* Select dropdown dark mode */
.dark select {
  @apply bg-slate-800 border-slate-600 text-slate-100;
}

.dark select option {
  @apply bg-slate-800 text-slate-100;
}

/* Info text dark mode */
.dark .text-gray-600 {
  @apply text-slate-300;
}

/* Table container overflow fix */
:deep(.modern-table) {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

/* Improve contrast for dark mode links/actions */
.dark :deep(.text-blue-600) {
  @apply text-blue-400;
}

.dark :deep(.hover\:text-blue-800:hover) {
  @apply text-blue-300;
}

.dark :deep(.text-red-600) {
  @apply text-red-400;
}

.dark :deep(.text-green-600) {
  @apply text-green-400;
}

/* Status badges dark mode */
.dark :deep(.bg-green-100) {
  @apply bg-green-900/30 text-green-300;
}

.dark :deep(.bg-red-100) {
  @apply bg-red-900/30 text-red-300;
}

.dark :deep(.bg-yellow-100) {
  @apply bg-yellow-900/30 text-yellow-300;
}

.dark :deep(.bg-blue-100) {
  @apply bg-blue-900/30 text-blue-300;
}

.dark :deep(.bg-gray-100) {
  @apply bg-slate-800 text-slate-300;
}

/* Ensure consistent row background */
:deep(.modern-table tbody tr) {
  transition: background-color 0.2s ease;
}

/* Fix for action buttons alignment */
:deep(.modern-table td:last-child) {
  vertical-align: middle;
  padding: 0.75rem 1rem;
}

:deep(.modern-table td:last-child > div) {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  justify-content: flex-start;
}
</style>