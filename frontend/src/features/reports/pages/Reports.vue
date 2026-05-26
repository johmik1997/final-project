<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import BaseIcon from '@/components/base/BaseIcon.vue';
import Table from '@/components/Table.vue';
import DashboardPanel from '@/features/dashboard/components/DashboardPanel.vue';
import ReportBarChart from '../components/ReportBarChart.vue';
import ReportDoughnutChart from '../components/ReportDoughnutChart.vue';
import { useApiRequest } from '@/composables/useApiRequest';
import { useAuth } from '@/stores/auth';
import { getAllMaterials } from '@/features/material/api/materialApi';
import { getAllBorrows } from '@/features/borrow/api/borrowApi';
import { getAllReservation } from '@/features/reservation/api/reservationApi';
import { getAllUser } from '@/features/users/Api/UserApi';
import { getAllLibrary } from '@/features/library/api/libraryApi';
import { getAllReturns } from '@/features/returns/api/returnApi';
import { getAllTransferRequests } from '@/features/transfer/api/transferApi';
import { reportsForRole } from '../config/reportTypes';
import {
  amount,
  belongsToCurrentUser,
  belongsToDepartment,
  defaultDateRange,
  exportToCsv,
  filterByDateRange,
  filterByLibrary,
  formatDate,
  getUserId,
  monthBucketSeries,
  normalizeRole,
  normalizeStatus,
  rowsFromPayload,
} from '../utils/reportHelpers';
import { exportReportPdf } from '../utils/reportExport';
import {
  mdiDownload,
  mdiFilePdfBox,
  mdiRefresh,
  mdiChartBar,
} from '@mdi/js';

const auth = useAuth();
const range = ref(defaultDateRange());
const selectedReportId = ref('');
const selectedLibraryId = ref('');

const physicalReq = useApiRequest();
const digitalReq = useApiRequest();
const borrowReq = useApiRequest();
const reservationReq = useApiRequest();
const usersReq = useApiRequest();
const libraryReq = useApiRequest();
const returnReq = useApiRequest();
const transferReq = useApiRequest();

const currentUser = computed(() => auth?.auth?.user || {});
const currentUserId = computed(() => getUserId(currentUser.value));
const currentRole = computed(() => normalizeRole(currentUser.value?.role || currentUser.value?.roleName));
const currentDepartment = computed(() => String(currentUser.value?.department || '').trim());
const isSuperAdmin = computed(() => currentRole.value === 'SUPER ADMIN');

const availableReports = computed(() => reportsForRole(currentRole.value));

function applyLibraryScope(rows) {
  if (!isSuperAdmin.value || !selectedLibraryId.value) return rows;
  return filterByLibrary(rows, selectedLibraryId.value);
}

const physicalMaterials = computed(() => rowsFromPayload(physicalReq.response.value));
const digitalMaterials = computed(() => rowsFromPayload(digitalReq.response.value));
const allMaterials = computed(() => [...physicalMaterials.value, ...digitalMaterials.value]);
const borrows = computed(() => rowsFromPayload(borrowReq.response.value));
const reservations = computed(() => rowsFromPayload(reservationReq.response.value));
const users = computed(() => rowsFromPayload(usersReq.response.value));
const libraries = computed(() => rowsFromPayload(libraryReq.response.value));
const returns = computed(() => rowsFromPayload(returnReq.response.value));
const transfers = computed(() => rowsFromPayload(transferReq.response.value));

const isLoading = computed(
  () =>
    physicalReq.pending.value ||
    digitalReq.pending.value ||
    borrowReq.pending.value ||
    reservationReq.pending.value ||
    usersReq.pending.value ||
    libraryReq.pending.value ||
    returnReq.pending.value ||
    transferReq.pending.value
);

const selectedReport = computed(
  () => availableReports.value.find((report) => report.id === selectedReportId.value) || availableReports.value[0]
);

const reportResult = computed(() => buildReport(selectedReport.value?.id));

const summaryCards = computed(() => reportResult.value.summary || []);
const tableHeaders = computed(() => reportResult.value.headers || []);
const tableRows = computed(() => reportResult.value.rows || []);

const trendChart = computed(() => {
  const borrowTrend = monthBucketSeries(scopedBorrows(), ['borrow_date', 'created_at']);
  const returnTrend = monthBucketSeries(scopedReturns(), ['return_date', 'created_at']);
  return {
    labels: borrowTrend.labels,
    borrows: borrowTrend.data,
    returns: returnTrend.data,
  };
});

const statusChart = computed(() => {
  const active = scopedBorrows().filter((row) => !row?.is_returned).length;
  const overdue = scopedBorrows().filter((row) => normalizeStatus(row?.status) === 'OVERDUE').length;
  const returned = scopedReturns().length;
  return {
    labels: ['Active', 'Overdue', 'Returned'],
    values: [active, overdue, returned],
  };
});

const libraryChart = computed(() => {
  if (!isSuperAdmin.value) return { labels: [], values: [] };
  return {
    labels: libraries.value.map((lib) => lib?.name || lib?.library_name || 'Branch'),
    values: libraries.value.map(
      (lib) =>
        borrows.value.filter(
          (row) =>
            !row?.is_returned &&
            String(row?.library_id || row?.material_library_id || '') === String(lib?.id)
        ).length
    ),
  };
});

function scopedBorrows() {
  let rows = applyLibraryScope(borrows.value);
  if (currentRole.value === 'MEMBER') {
    rows = rows.filter((row) => belongsToCurrentUser(row, currentUserId.value));
  } else if (currentRole.value === 'DEPARTMENT HEAD' && currentDepartment.value) {
    rows = rows.filter((row) => belongsToDepartment(row, currentDepartment.value));
  }
  return filterByDateRange(rows, range.value.from, range.value.to, ['borrow_date', 'created_at']);
}

function scopedReturns() {
  let rows = applyLibraryScope(returns.value);
  if (currentRole.value === 'MEMBER') {
    rows = rows.filter((row) => belongsToCurrentUser(row, currentUserId.value));
  } else if (currentRole.value === 'DEPARTMENT HEAD' && currentDepartment.value) {
    rows = rows.filter((row) => belongsToDepartment(row, currentDepartment.value));
  }
  return filterByDateRange(rows, range.value.from, range.value.to, ['return_date', 'created_at']);
}

function scopedReservations() {
  let rows = applyLibraryScope(reservations.value);
  if (currentRole.value === 'MEMBER') {
    rows = rows.filter((row) => belongsToCurrentUser(row, currentUserId.value));
  } else if (currentRole.value === 'DEPARTMENT HEAD' && currentDepartment.value) {
    rows = rows.filter((row) => belongsToDepartment(row, currentDepartment.value));
  }
  return filterByDateRange(rows, range.value.from, range.value.to, ['reserve_date', 'created_at']);
}

function scopedMembers() {
  let rows = applyLibraryScope(users.value.filter((user) => normalizeRole(user?.role) === 'MEMBER'));
  if (currentRole.value === 'DEPARTMENT HEAD' && currentDepartment.value) {
    rows = rows.filter(
      (user) => String(user?.department || '').trim().toLowerCase() === currentDepartment.value.toLowerCase()
    );
  }
  return rows;
}

function buildReport(reportId) {
  switch (reportId) {
    case 'my-borrows':
      return buildMyBorrowsReport();
    case 'my-fines':
      return buildFinesReport(true);
    case 'my-reservations':
      return buildReservationsReport(true);
    case 'circulation-summary':
      return buildCirculationSummary();
    case 'overdue-list':
      return buildOverdueReport();
    case 'fines-report':
      return buildFinesReport(false);
    case 'transfer-report':
      return buildTransferReport();
    case 'catalog-inventory':
      return buildCatalogReport(false);
    case 'low-stock':
      return buildCatalogReport(true);
    case 'borrow-activity':
      return buildBorrowActivityReport();
    case 'member-roster':
      return buildMemberRosterReport();
    case 'reservation-report':
      return buildReservationsReport(false);
    case 'system-overview':
      return buildSystemOverview();
    case 'library-comparison':
      return buildLibraryComparison();
    case 'department-usage':
      return buildDepartmentUsage();
    case 'department-members':
      return buildMemberRosterReport();
    case 'popular-materials':
      return buildPopularMaterials();
    default:
      return { summary: [], headers: [], rows: [] };
  }
}

function buildMyBorrowsReport() {
  const rows = scopedBorrows();
  return {
    summary: [
      { label: 'Total borrows', value: rows.length },
      { label: 'Active', value: rows.filter((r) => !r?.is_returned).length },
      { label: 'Overdue', value: rows.filter((r) => normalizeStatus(r?.status) === 'OVERDUE').length },
    ],
    headers: [
      { key: 'material', label: 'Material' },
      { key: 'status', label: 'Status' },
      { key: 'borrow_date', label: 'Borrowed' },
      { key: 'due_date', label: 'Due' },
    ],
    rows: rows.map((row) => ({
      material: row?.material_title || '-',
      status: row?.status || '-',
      borrow_date: formatDate(row?.borrow_date || row?.created_at),
      due_date: formatDate(row?.due_date),
    })),
  };
}

function buildFinesReport(personalOnly) {
  const rows = scopedReturns().filter((row) => amount(row?.fine_amount) > 0);
  const outstanding = rows.filter((row) => normalizeStatus(row?.payment_status) !== 'COMPLETED');
  const paid = rows.filter((row) => normalizeStatus(row?.payment_status) === 'COMPLETED');

  return {
    summary: [
      { label: personalOnly ? 'Your fines' : 'Fine records', value: rows.length },
      { label: 'Outstanding (ETB)', value: outstanding.reduce((s, r) => s + amount(r?.fine_amount), 0).toFixed(2) },
      { label: 'Collected (ETB)', value: paid.reduce((s, r) => s + amount(r?.fine_amount), 0).toFixed(2) },
    ],
    headers: [
      { key: 'material', label: 'Material' },
      { key: 'member', label: personalOnly ? 'Account' : 'Member' },
      { key: 'amount', label: 'Amount (ETB)' },
      { key: 'status', label: 'Payment' },
      { key: 'date', label: 'Return date' },
    ],
    rows: rows.map((row) => ({
      material: row?.material_title || '-',
      member: personalOnly ? 'You' : row?.member_name || '-',
      amount: amount(row?.fine_amount).toFixed(2),
      status: row?.payment_status || 'PENDING',
      date: formatDate(row?.return_date),
    })),
  };
}

function buildReservationsReport(personalOnly) {
  const rows = scopedReservations();
  return {
    summary: [
      { label: 'Reservations', value: rows.length },
      { label: 'Active holds', value: rows.filter((r) => normalizeStatus(r?.status) === 'RESERVED').length },
      { label: 'Cancelled', value: rows.filter((r) => normalizeStatus(r?.status) === 'CANCELLED').length },
    ],
    headers: [
      { key: 'material', label: 'Material' },
      { key: 'member', label: personalOnly ? 'Account' : 'Member' },
      { key: 'status', label: 'Status' },
      { key: 'date', label: 'Reserved' },
    ],
    rows: rows.map((row) => ({
      material: row?.material_title || '-',
      member: personalOnly ? 'You' : row?.member_name || '-',
      status: row?.status || '-',
      date: formatDate(row?.reserve_date || row?.created_at),
    })),
  };
}

function buildCirculationSummary() {
  const borrowRows = scopedBorrows();
  const returnRows = scopedReturns();
  const overdue = borrowRows.filter((r) => normalizeStatus(r?.status) === 'OVERDUE' && !r?.is_returned);

  return {
    summary: [
      { label: 'Borrows issued', value: borrowRows.length },
      { label: 'Returns processed', value: returnRows.length },
      { label: 'Currently overdue', value: overdue.length },
    ],
    headers: [
      { key: 'metric', label: 'Metric' },
      { key: 'value', label: 'Count' },
    ],
    rows: [
      { metric: 'Borrows in period', value: borrowRows.length },
      { metric: 'Returns in period', value: returnRows.length },
      { metric: 'Active borrows (now)', value: borrows.value.filter((r) => !r?.is_returned).length },
      { metric: 'Overdue (now)', value: borrows.value.filter((r) => normalizeStatus(r?.status) === 'OVERDUE').length },
      { metric: 'Reservations waiting', value: reservations.value.filter((r) => normalizeStatus(r?.status) === 'RESERVED').length },
    ],
  };
}

function buildOverdueReport() {
  const rows = borrows.value.filter(
    (row) => normalizeStatus(row?.status) === 'OVERDUE' && !row?.is_returned
  );
  return {
    summary: [
      { label: 'Overdue items', value: rows.length },
      {
        label: 'Est. fines (ETB)',
        value: rows.reduce((s, r) => s + amount(r?.fine_amount), 0).toFixed(2),
      },
    ],
    headers: [
      { key: 'material', label: 'Material' },
      { key: 'member', label: 'Member' },
      { key: 'due_date', label: 'Due date' },
      { key: 'status', label: 'Status' },
    ],
    rows: rows.map((row) => ({
      material: row?.material_title || '-',
      member: row?.member_name || '-',
      due_date: formatDate(row?.due_date),
      status: row?.status || 'OVERDUE',
    })),
  };
}

function buildTransferReport() {
  const rows = filterByDateRange(transfers.value, range.value.from, range.value.to, ['created_at', 'updated_at']);
  return {
    summary: [
      { label: 'Transfer requests', value: rows.length },
      { label: 'Pending', value: rows.filter((r) => normalizeStatus(r?.status) === 'PENDING').length },
      { label: 'Fulfilled', value: rows.filter((r) => normalizeStatus(r?.status) === 'FULFILLED').length },
    ],
    headers: [
      { key: 'material', label: 'Material' },
      { key: 'from', label: 'From' },
      { key: 'to', label: 'To' },
      { key: 'status', label: 'Status' },
      { key: 'date', label: 'Requested' },
    ],
    rows: rows.map((row) => ({
      material: row?.material_title || row?.material?.title || '-',
      from: row?.from_location || row?.source_location || '-',
      to: row?.to_location || row?.destination_location || '-',
      status: row?.status || '-',
      date: formatDate(row?.created_at),
    })),
  };
}

function buildCatalogReport(lowStockOnly) {
  const physical = physicalMaterials.value;
  const rows = lowStockOnly
    ? physical.filter((row) => amount(row?.available_copies) > 0 && amount(row?.available_copies) <= 1)
    : allMaterials.value;

  return {
    summary: [
      { label: lowStockOnly ? 'Low stock items' : 'Total materials', value: rows.length },
      { label: 'Physical', value: physicalMaterials.value.length },
      { label: 'Digital', value: digitalMaterials.value.length },
    ],
    headers: [
      { key: 'title', label: 'Title' },
      { key: 'type', label: 'Type' },
      { key: 'category', label: 'Category' },
      { key: 'copies', label: 'Available' },
      { key: 'location', label: 'Location' },
    ],
    rows: rows.map((row) => ({
      title: row?.title || '-',
      type: row?.material_type || '-',
      category: row?.category || '-',
      copies: String(row?.available_copies ?? row?.copy_number ?? '-'),
      location: row?.location || '-',
    })),
  };
}

function buildBorrowActivityReport() {
  const rows = scopedBorrows();
  return {
    summary: [
      { label: 'Borrow events', value: rows.length },
      { label: 'Unique materials', value: new Set(rows.map((r) => r?.material || r?.material_id)).size },
    ],
    headers: [
      { key: 'material', label: 'Material' },
      { key: 'member', label: 'Member' },
      { key: 'status', label: 'Status' },
      { key: 'date', label: 'Borrowed' },
    ],
    rows: rows.map((row) => ({
      material: row?.material_title || '-',
      member: row?.member_name || '-',
      status: row?.status || '-',
      date: formatDate(row?.borrow_date || row?.created_at),
    })),
  };
}

function buildMemberRosterReport() {
  const rows = scopedMembers();
  return {
    summary: [
      { label: 'Members', value: rows.length },
      {
        label: 'Departments',
        value: new Set(rows.map((r) => r?.department).filter(Boolean)).size,
      },
    ],
    headers: [
      { key: 'name', label: 'Name' },
      { key: 'id_number', label: 'ID' },
      { key: 'department', label: 'Department' },
      { key: 'library', label: 'Library' },
      { key: 'status', label: 'Status' },
    ],
    rows: rows.map((row) => ({
      name: `${row?.first_name || ''} ${row?.last_name || ''}`.trim() || row?.name || '-',
      id_number: row?.id_number || '-',
      department: row?.department || '-',
      library: row?.library_name || '-',
      status: row?.status || '-',
    })),
  };
}

function buildSystemOverview() {
  return {
    summary: [
      { label: 'Libraries', value: libraries.value.length },
      { label: 'Members', value: users.value.filter((u) => normalizeRole(u?.role) === 'MEMBER').length },
      { label: 'Materials', value: allMaterials.value.length },
      { label: 'Active borrows', value: borrows.value.filter((r) => !r?.is_returned).length },
    ],
    headers: [
      { key: 'metric', label: 'Metric' },
      { key: 'value', label: 'Value' },
    ],
    rows: [
      { metric: 'Total users', value: users.value.length },
      { metric: 'Members', value: users.value.filter((u) => normalizeRole(u?.role) === 'MEMBER').length },
      { metric: 'Staff accounts', value: users.value.filter((u) => normalizeRole(u?.role) !== 'MEMBER').length },
      { metric: 'Physical materials', value: physicalMaterials.value.length },
      { metric: 'Digital materials', value: digitalMaterials.value.length },
      { metric: 'Borrows (period)', value: scopedBorrows().length },
      { metric: 'Returns (period)', value: scopedReturns().length },
      { metric: 'Unpaid fines (ETB)', value: returns.value.filter((r) => amount(r?.fine_amount) > 0 && normalizeStatus(r?.payment_status) !== 'COMPLETED').reduce((s, r) => s + amount(r?.fine_amount), 0).toFixed(2) },
    ],
  };
}

function buildLibraryComparison() {
  const rows = libraries.value.map((library) => {
    const libId = library?.id;
    const libBorrows = borrows.value.filter(
      (b) => String(b?.library_id || b?.material_library_id || '') === String(libId)
    );
    const libMembers = users.value.filter(
      (u) => String(u?.library_id || u?.library) === String(libId) && normalizeRole(u?.role) === 'MEMBER'
    );
    return {
      library: library?.name || library?.library_name || '-',
      members: libMembers.length,
      borrows: libBorrows.filter((b) => !b?.is_returned).length,
      materials: allMaterials.value.filter((m) => String(m?.library || m?.library_id) === String(libId)).length,
    };
  });

  return {
    summary: [
      { label: 'Branches', value: libraries.value.length },
      { label: 'Total members', value: rows.reduce((s, r) => s + r.members, 0) },
    ],
    headers: [
      { key: 'library', label: 'Library' },
      { key: 'members', label: 'Members' },
      { key: 'borrows', label: 'Active borrows' },
      { key: 'materials', label: 'Materials' },
    ],
    rows,
  };
}

function buildDepartmentUsage() {
  const borrowRows = scopedBorrows();
  const reservationRows = scopedReservations();
  return {
    summary: [
      { label: 'Department', value: currentDepartment.value || 'All' },
      { label: 'Borrows', value: borrowRows.length },
      { label: 'Reservations', value: reservationRows.length },
    ],
    headers: [
      { key: 'type', label: 'Activity' },
      { key: 'material', label: 'Material' },
      { key: 'member', label: 'Member' },
      { key: 'status', label: 'Status' },
      { key: 'date', label: 'Date' },
    ],
    rows: [
      ...borrowRows.map((row) => ({
        type: 'Borrow',
        material: row?.material_title || '-',
        member: row?.member_name || '-',
        status: row?.status || '-',
        date: formatDate(row?.borrow_date),
      })),
      ...reservationRows.map((row) => ({
        type: 'Reservation',
        material: row?.material_title || '-',
        member: row?.member_name || '-',
        status: row?.status || '-',
        date: formatDate(row?.reserve_date),
      })),
    ],
  };
}

function buildPopularMaterials() {
  const counts = new Map();
  scopedBorrows().forEach((row) => {
    const title = row?.material_title || 'Unknown';
    counts.set(title, (counts.get(title) || 0) + 1);
  });

  const rows = [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 25)
    .map(([title, count]) => ({ title, borrows: count }));

  return {
    summary: [
      { label: 'Unique titles', value: rows.length },
      { label: 'Total borrows', value: scopedBorrows().length },
    ],
    headers: [
      { key: 'title', label: 'Material' },
      { key: 'borrows', label: 'Borrow count' },
    ],
    rows,
  };
}

function loadReports() {
  physicalReq.send(() => getAllMaterials({ page: 1, size: 500 }, 'physical'));
  digitalReq.send(() => getAllMaterials({ page: 1, size: 500 }, 'digital'));
  borrowReq.send(() => getAllBorrows({ page: 1, size: 500 }));
  reservationReq.send(() => getAllReservation({ page: 1, size: 500 }));
  usersReq.send(() => getAllUser({ page: 1, size: 500 }));
  libraryReq.send(() => getAllLibrary({ page: 1, size: 100 }));
  returnReq.send(() => getAllReturns({ page: 1, size: 500 }));
  transferReq.send(() => getAllTransferRequests({ page: 1, size: 200 }));
}

function exportCsv() {
  const slug = selectedReport.value?.id || 'report';
  exportToCsv(
    `library_${slug}_${range.value.from}_${range.value.to}.csv`,
    tableHeaders.value,
    tableRows.value
  );
}

function exportPdf() {
  exportReportPdf({
    title: selectedReport.value?.label || 'Report',
    subtitle: selectedReport.value?.description,
    headers: tableHeaders.value,
    rows: tableRows.value,
    filename: `library_${selectedReport.value?.id || 'report'}`,
  });
}

watch(availableReports, (reports) => {
  if (reports.length && !reports.some((report) => report.id === selectedReportId.value)) {
    selectedReportId.value = reports[0].id;
  }
}, { immediate: true });

onMounted(loadReports);
</script>

<template>
  <div class="reports-page">
    <section class="reports-hero">
      <div class="hero-content">
        <div class="hero-text">
          <p class="hero-eyebrow">{{ currentRole }} workspace</p>
          <h1 class="hero-title">Reports</h1>
          <p class="hero-subtitle">
            Role-focused reports for your library workspace. Filter by date range and export to CSV or PDF.
          </p>
        </div>
        <div class="hero-actions">
          <button type="button" class="btn-outline" @click="loadReports">
            <BaseIcon :path="mdiRefresh" size="18" />
            Refresh data
          </button>
        </div>
      </div>
    </section>

    <div class="filters-row">
      <label class="filter-field">
        <span>From</span>
        <input v-model="range.from" type="date" class="filter-input" />
      </label>
      <label class="filter-field">
        <span>To</span>
        <input v-model="range.to" type="date" class="filter-input" />
      </label>
      <label v-if="isSuperAdmin" class="filter-field">
        <span>Library branch</span>
        <select v-model="selectedLibraryId" class="filter-input filter-select">
          <option value="">All libraries</option>
          <option v-for="lib in libraries" :key="lib.id" :value="String(lib.id)">
            {{ lib.name || lib.library_name }}
          </option>
        </select>
      </label>
    </div>

    <div v-if="availableReports.length" class="report-tabs">
      <button
        v-for="report in availableReports"
        :key="report.id"
        type="button"
        class="report-tab"
        :class="{ active: selectedReportId === report.id }"
        @click="selectedReportId = report.id"
      >
        {{ report.label }}
      </button>
    </div>

    <p v-if="selectedReport?.description" class="report-description">
      {{ selectedReport.description }}
    </p>

    <div v-if="summaryCards.length" class="summary-grid">
      <div v-for="card in summaryCards" :key="card.label" class="summary-card">
        <BaseIcon :path="mdiChartBar" size="22" class="summary-icon" />
        <div>
          <p class="summary-label">{{ card.label }}</p>
          <p class="summary-value">{{ card.value }}</p>
        </div>
      </div>
    </div>

    <div v-if="!isLoading" class="reports-charts-grid">
      <DashboardPanel title="Activity trend" subtitle="Borrows and returns over the last six months">
        <ReportBarChart
          :labels="trendChart.labels"
          :values="trendChart.borrows"
          label="Borrows"
          color="#3b82f6"
        />
      </DashboardPanel>
      <DashboardPanel title="Circulation status" subtitle="Active, overdue, and returned in this period">
        <ReportDoughnutChart
          :labels="statusChart.labels"
          :values="statusChart.values"
          :colors="['#3b82f6', '#ef4444', '#10b981']"
        />
      </DashboardPanel>
      <DashboardPanel
        v-if="isSuperAdmin && libraryChart.labels.length"
        title="Active borrows by library"
        subtitle="Cross-branch comparison for the selected filters"
      >
        <ReportBarChart
          :labels="libraryChart.labels"
          :values="libraryChart.values"
          label="Active borrows"
          color="#f59e0b"
        />
      </DashboardPanel>
    </div>

    <DashboardPanel title="Report data" :subtitle="`${tableRows.length} rows in the selected period`">
      <div class="export-actions">
        <button type="button" class="btn-export" :disabled="!tableRows.length" @click="exportCsv">
          <BaseIcon :path="mdiDownload" size="18" />
          Export CSV
        </button>
        <button type="button" class="btn-export" :disabled="!tableRows.length" @click="exportPdf">
          <BaseIcon :path="mdiFilePdfBox" size="18" />
          Export PDF
        </button>
      </div>

      <div v-if="isLoading" class="loading-msg">Loading report data...</div>

      <Table
        v-else
        :pending="isLoading"
        :headers="{
          head: tableHeaders.map((h) => h.label),
          row: tableHeaders.map((h) => h.key),
        }"
        :rows="tableRows"
        :show-pagination="tableRows.length > 15"
        :length="15"
        placeholder="No records match this report and date range."
      />
    </DashboardPanel>
  </div>
</template>

<style scoped>
.reports-page {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding-bottom: 2rem;
  width: 100%;
  max-width: 72rem;
  margin-left: auto;
  margin-right: auto;
  padding-left: 1rem;
  padding-right: 1rem;
  box-sizing: border-box;
}

.reports-hero {
  border-radius: 1rem;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(239, 68, 68, 0.1));
  padding: 1.5rem 1.75rem;
  color: #f8fafc;
}

.hero-content {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.hero-eyebrow {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #fbbf24;
  margin-bottom: 0.35rem;
}

.hero-title {
  font-size: 1.75rem;
  font-weight: 800;
  letter-spacing: -0.02em;
  background: linear-gradient(135deg, #f59e0b, #facc15);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  margin-top: 0.5rem;
  max-width: 36rem;
  font-size: 0.9rem;
  color: #f59e0b;
  line-height: 1.5;
}

.hero-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-outline {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.25);
  background: transparent;
  color: #f8fafc;
  font-size: 0.875rem;
  cursor: pointer;
}

.btn-outline:hover {
  background: rgba(255, 255, 255, 0.08);
}

.filters-row {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
}

.filter-input {
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
  background: #fff;
  font-size: 0.875rem;
}

.dark .filter-input {
  background: #1e293b;
  border-color: #334155;
  color: #f1f5f9;
}

.report-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.report-tab {
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  border: 1px solid #e2e8f0;
  background: #fff;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.15s ease;
}

.report-tab.active {
  background: #f59e0b;
  border-color: #f59e0b;
  color: #0f172a;
}

.dark .report-tab {
  background: #1e293b;
  border-color: #334155;
  color: #cbd5e1;
}

.report-description {
  font-size: 0.875rem;
  color: #64748b;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.75rem;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 0.75rem;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid #e2e8f0;
}

.dark .summary-card {
  background: rgba(30, 41, 59, 0.6);
  border-color: #334155;
}

.summary-icon {
  color: #f59e0b;
}

.summary-label {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #64748b;
}

.summary-value {
  font-size: 1.25rem;
  font-weight: 800;
  color: #0f172a;
}

.dark .summary-value {
  color: #f1f5f9;
}

.export-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.btn-export {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.45rem 0.9rem;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #334155;
  cursor: pointer;
}

.btn-export:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-export:not(:disabled):hover {
  border-color: #f59e0b;
  color: #b45309;
}

.loading-msg {
  padding: 2rem;
  text-align: center;
  color: #64748b;
}

.filter-select {
  min-width: 180px;
  cursor: pointer;
}

.reports-charts-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 1024px) {
  .reports-charts-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
