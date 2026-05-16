<script setup>
import { computed, onBeforeUnmount, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { useApiRequest } from '@/composables/useApiRequest';
import { useAuth } from '@/stores/auth';
import { getAllMaterials } from '@/features/material/api/materialApi';
import { getAllBorrows } from '@/features/borrow/api/borrowApi';
import { getAllReservation } from '@/features/reservation/api/reservationApi';
import { getAllUser } from '@/features/users/Api/UserApi';
import { getAllLibrary } from '@/features/library/api/libraryApi';
import { getAllReturns } from '@/features/returns/api/returnApi';
import { getRecommendedMaterials } from '../api/recommendationApi';
import { subscribeEntityMutation } from '@/utils/entitySync';
import DashboardStatCard from '../components/DashboardStatCard.vue';
import DashboardPanel from '../components/DashboardPanel.vue';
import DashboardActivityBarChart from '../components/DashboardActivityBarChart.vue';
import DashboardMaterialPieChart from '../components/DashboardMaterialPieChart.vue';
import {
  mdiAccountGroup,
  mdiAlertCircle,
  mdiArrowRight,
  mdiBookOpenPageVariant,
  mdiBookshelf,
  mdiCashMultiple,
  mdiChartTimelineVariant,
  mdiCheckCircle,
  mdiClockOutline,
  mdiCreditCardCheckOutline,
  mdiKeyboardReturn,
  mdiLibrary,
  mdiPlus,
  mdiRefresh,
  mdiShieldCrown,
  mdiStarFourPoints,
  mdiViewDashboard,
} from '@mdi/js';

const router = useRouter();
const auth = useAuth();

const physicalReq = useApiRequest();
const digitalReq = useApiRequest();
const borrowReq = useApiRequest();
const reservationReq = useApiRequest();
const usersReq = useApiRequest();
const libraryReq = useApiRequest();
const returnReq = useApiRequest();
const recommendationReq = useApiRequest();

let unsubscribeEntitySync = () => {};

function rowsFromPayload(payload) {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.content)) return payload.content;
  if (Array.isArray(payload?.response)) return payload.response;
  if (Array.isArray(payload?.data)) return payload.data;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.result)) return payload.result;
  if (Array.isArray(payload?.libraries)) return payload.libraries;
  if (Array.isArray(payload?.users)) return payload.users;
  return [];
}

function amount(value) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

function normalizeStatus(value) {
  return String(value || '').trim().toUpperCase();
}

function normalizeRole(value) {
  return normalizeStatus(value).replace(/^ROLE_/, '');
}

function newestFirst(rows = [], fields = []) {
  return [...rows].sort((a, b) => {
    const aDate = new Date(fields.map((field) => a?.[field]).find(Boolean) || 0).getTime();
    const bDate = new Date(fields.map((field) => b?.[field]).find(Boolean) || 0).getTime();
    return bDate - aDate;
  });
}

function formatDate(value) {
  if (!value) return '-';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '-';
  return date.toLocaleString();
}

function getUserId(user) {
  return user?.id || user?.user_id || user?.userId || user?.uuid || null;
}

function sameId(a, b) {
  if (a === null || a === undefined || b === null || b === undefined) return false;
  return String(a) === String(b);
}

function belongsToCurrentUser(row, currentUserId) {
  if (!currentUserId) return false;

  const ids = [
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

  return ids.some((id) => sameId(id, currentUserId));
}

function monthBucketSeries(rows, fields) {
  const keys = [];
  const now = new Date();

  for (let index = 5; index >= 0; index -= 1) {
    const date = new Date(now.getFullYear(), now.getMonth() - index, 1);
    keys.push({
      label: date.toLocaleDateString(undefined, { month: 'short', year: '2-digit' }),
      key: `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`,
    });
  }

  const counts = new Map(keys.map((item) => [item.key, 0]));
  rows.forEach((row) => {
    const rawDate = fields.map((field) => row?.[field]).find(Boolean);
    const date = new Date(rawDate || 0);
    if (Number.isNaN(date.getTime())) return;
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
    if (counts.has(key)) {
      counts.set(key, (counts.get(key) || 0) + 1);
    }
  });

  return {
    labels: keys.map((item) => item.label),
    data: keys.map((item) => counts.get(item.key) || 0),
  };
}

const currentUser = computed(() => auth?.auth?.user || {});
const currentUserId = computed(() => getUserId(currentUser.value));
const currentRole = computed(() => normalizeRole(currentUser.value?.role || currentUser.value?.roleName));
const isMember = computed(() => currentRole.value === 'MEMBER');
const isStackStaff = computed(() => currentRole.value === 'STACK STAFF');
const isTechnicalStaff = computed(() => currentRole.value === 'TECHNICAL STAFF');
const isAdminLike = computed(() => ['ADMIN', 'SUPER ADMIN'].includes(currentRole.value));

const physicalMaterials = computed(() => rowsFromPayload(physicalReq.response.value));
const digitalMaterials = computed(() => rowsFromPayload(digitalReq.response.value));
const allMaterials = computed(() => [...physicalMaterials.value, ...digitalMaterials.value]);
const borrows = computed(() => rowsFromPayload(borrowReq.response.value));
const reservations = computed(() => rowsFromPayload(reservationReq.response.value));
const users = computed(() => rowsFromPayload(usersReq.response.value));
const libraries = computed(() => rowsFromPayload(libraryReq.response.value));
const returns = computed(() => rowsFromPayload(returnReq.response.value));
const recommendations = computed(() => recommendationReq.response.value?.results || []);
const recommendationStrategy = computed(() => recommendationReq.response.value?.strategy || 'popular');

const availableMaterials = computed(() =>
  allMaterials.value.filter((row) => amount(row?.available_copies ?? row?.copy_number) > 0).length
);
const totalMembers = computed(() =>
  users.value.filter((user) => normalizeRole(user?.role) === 'MEMBER').length
);
const activeBorrows = computed(() =>
  borrows.value.filter((row) => ['BORROWED', 'OVERDUE'].includes(normalizeStatus(row?.status)) && !row?.is_returned).length
);
const activeReservations = computed(() =>
  reservations.value.filter((row) => normalizeStatus(row?.status) === 'RESERVED').length
);
const overdueBorrows = computed(() =>
  borrows.value.filter((row) => normalizeStatus(row?.status) === 'OVERDUE' && !row?.is_returned).length
);
const pendingReturns = computed(() =>
  borrows.value.filter((row) => !row?.is_returned && ['BORROWED', 'OVERDUE'].includes(normalizeStatus(row?.status))).length
);
const returnedToday = computed(() =>
  returns.value.filter((row) => {
    const returnedAt = new Date(row?.return_date || 0);
    const now = new Date();
    return (
      returnedAt.getFullYear() === now.getFullYear() &&
      returnedAt.getMonth() === now.getMonth() &&
      returnedAt.getDate() === now.getDate()
    );
  }).length
);
const lowStockMaterials = computed(() =>
  physicalMaterials.value.filter((row) => amount(row?.available_copies) > 0 && amount(row?.available_copies) <= 1).length
);
const unpaidFineTotal = computed(() =>
  returns.value.reduce((sum, row) => {
    if (amount(row?.fine_amount) <= 0 || normalizeStatus(row?.payment_status) === 'COMPLETED') {
      return sum;
    }
    return sum + amount(row?.fine_amount);
  }, 0)
);

const myBorrows = computed(() =>
  newestFirst(
    borrows.value.filter((row) => belongsToCurrentUser(row, currentUserId.value)),
    ['borrow_date', 'created_at']
  )
);
const myReservations = computed(() =>
  newestFirst(
    reservations.value.filter((row) => belongsToCurrentUser(row, currentUserId.value)),
    ['reserve_date', 'created_at']
  )
);
const myOutstandingReturns = computed(() =>
  newestFirst(
    returns.value.filter((row) => belongsToCurrentUser(row, currentUserId.value) && amount(row?.fine_amount) > 0),
    ['return_date', 'created_at']
  )
);
const myOutstandingFineTotal = computed(() =>
  myOutstandingReturns.value.reduce((sum, row) => {
    if (normalizeStatus(row?.payment_status) === 'COMPLETED') return sum;
    return sum + amount(row?.fine_amount);
  }, 0)
);

const monthlyBorrows = computed(() => {
  const scopedRows = isMember.value ? myBorrows.value : borrows.value;
  return monthBucketSeries(scopedRows, ['borrow_date', 'created_at']);
});

const monthlyReservations = computed(() => {
  const scopedRows = isMember.value ? myReservations.value : reservations.value;
  return monthBucketSeries(scopedRows, ['reserve_date', 'created_at']);
});

const unavailableMaterials = computed(() => Math.max(allMaterials.value.length - availableMaterials.value, 0));

const recentBorrows = computed(() => newestFirst(borrows.value, ['borrow_date', 'created_at']).slice(0, 5));
const recentReturns = computed(() => newestFirst(returns.value, ['return_date', 'created_at']).slice(0, 5));
const recentReservations = computed(() => newestFirst(reservations.value, ['reserve_date', 'created_at']).slice(0, 5));

const quickActions = computed(() => {
  if (isMember.value) {
    return [
      { label: 'Browse Materials', path: '/material', icon: mdiBookOpenPageVariant, tone: 'blue' },
      { label: 'My Borrows', path: '/my-borrows', icon: mdiBookshelf, tone: 'amber' },
      { label: 'My Reservations', path: '/reservations', icon: mdiClockOutline, tone: 'green' },
      { label: 'Fine Payments', path: '/fine-payments', icon: mdiCreditCardCheckOutline, tone: 'violet' },
    ];
  }

  if (isStackStaff.value) {
    return [
      { label: 'Issue Borrow', path: '/borrows/add', icon: mdiPlus, tone: 'blue' },
      { label: 'Process Returns', path: '/returns', icon: mdiKeyboardReturn, tone: 'green' },
      { label: 'Borrow Records', path: '/borrows', icon: mdiBookshelf, tone: 'amber' },
      { label: 'Materials', path: '/material', icon: mdiBookOpenPageVariant, tone: 'violet' },
    ];
  }

  if (isTechnicalStaff.value) {
    return [
      { label: 'Materials', path: '/material', icon: mdiBookOpenPageVariant, tone: 'blue' },
      { label: 'Add Material', path: '/material', icon: mdiPlus, tone: 'green' },
      { label: 'Catalog Overview', path: '/dashboard', icon: mdiChartTimelineVariant, tone: 'amber' },
      { label: 'Borrow Activity', path: '/borrows', icon: mdiBookshelf, tone: 'violet' },
    ];
  }

  return [
    { label: 'Users', path: '/users', icon: mdiAccountGroup, tone: 'blue' },
    { label: 'Libraries', path: '/library', icon: mdiLibrary, tone: 'green' },
    { label: 'Returns', path: '/returns', icon: mdiKeyboardReturn, tone: 'amber' },
    { label: 'Materials', path: '/material', icon: mdiBookOpenPageVariant, tone: 'violet' },
  ];
});

const dashboardTitle = computed(() => {
  if (isMember.value) return 'Your reading journey, organized.';
  if (isStackStaff.value) return 'Circulation desk at a glance.';
  if (isTechnicalStaff.value) return 'Collection health and digital readiness.';
  return 'Operational visibility across the library system.';
});

const dashboardSubtitle = computed(() => {
  if (isMember.value) {
    return 'Track borrows, reservations, recommendations, and overdue fines from one role-focused home screen.';
  }
  if (isStackStaff.value) {
    return 'Keep borrow and return traffic moving with instant visibility into overdue items, pending returns, and fines.';
  }
  if (isTechnicalStaff.value) {
    return 'Monitor material availability, catalog coverage, and low-stock pressure without bouncing between pages.';
  }
  return 'See the system-wide state of libraries, users, materials, circulation, and payments in a single dashboard.';
});

const statCards = computed(() => {
  if (isMember.value) {
    return [
      {
        label: 'Active Borrows',
        value: myBorrows.value.filter((row) => ['BORROWED', 'OVERDUE'].includes(normalizeStatus(row?.status)) && !row?.is_returned).length,
        description: 'Items currently in your account',
        icon: mdiBookshelf,
        tone: 'blue',
      },
      {
        label: 'Reservations',
        value: myReservations.value.filter((row) => normalizeStatus(row?.status) === 'RESERVED').length,
        description: 'Books waiting in your queue',
        icon: mdiClockOutline,
        tone: 'green',
      },
      {
        label: 'Outstanding Fine',
        value: `ETB ${myOutstandingFineTotal.value.toFixed(2)}`,
        description: 'Only unpaid overdue charges',
        icon: mdiCashMultiple,
        tone: 'amber',
      },
      {
        label: 'Recommended Picks',
        value: recommendations.value.length,
        description: recommendationStrategy.value === 'personalized' ? 'Based on your activity' : 'Popular across the library',
        icon: mdiStarFourPoints,
        tone: 'violet',
      },
    ];
  }

  if (isStackStaff.value) {
    return [
      {
        label: 'Pending Returns',
        value: pendingReturns.value,
        description: 'Borrowed items still out',
        icon: mdiKeyboardReturn,
        tone: 'blue',
      },
      {
        label: 'Overdue Borrows',
        value: overdueBorrows.value,
        description: 'Need follow-up attention',
        icon: mdiAlertCircle,
        tone: 'amber',
      },
      {
        label: 'Returned Today',
        value: returnedToday.value,
        description: 'Processed during this day',
        icon: mdiCheckCircle,
        tone: 'green',
      },
      {
        label: 'Unpaid Fines',
        value: `ETB ${unpaidFineTotal.value.toFixed(2)}`,
        description: 'From returned overdue materials',
        icon: mdiCashMultiple,
        tone: 'violet',
      },
    ];
  }

  if (isTechnicalStaff.value) {
    return [
      {
        label: 'Total Materials',
        value: allMaterials.value.length,
        description: `${physicalMaterials.value.length} physical, ${digitalMaterials.value.length} digital`,
        icon: mdiBookshelf,
        tone: 'blue',
      },
      {
        label: 'Available Materials',
        value: availableMaterials.value,
        description: 'Borrow-ready or immediately accessible',
        icon: mdiCheckCircle,
        tone: 'green',
      },
      {
        label: 'Low Stock',
        value: lowStockMaterials.value,
        description: 'Physical items with one copy left',
        icon: mdiAlertCircle,
        tone: 'amber',
      },
      {
        label: 'Digital Assets',
        value: digitalMaterials.value.length,
        description: 'Downloadable and readable resources',
        icon: mdiViewDashboard,
        tone: 'violet',
      },
    ];
  }

  return [
    {
      label: 'Members',
      value: totalMembers.value,
      description: 'Registered users with MEMBER role',
      icon: mdiAccountGroup,
      tone: 'blue',
    },
    {
      label: 'Libraries',
      value: libraries.value.length,
      description: 'Configured library branches',
      icon: mdiLibrary,
      tone: 'green',
    },
    {
      label: 'Active Borrows',
      value: activeBorrows.value,
      description: 'Borrowed and overdue items still out',
      icon: mdiClockOutline,
      tone: 'amber',
    },
    {
      label: 'Unpaid Fines',
      value: `ETB ${unpaidFineTotal.value.toFixed(2)}`,
      description: 'Across completed returns',
      icon: mdiShieldCrown,
      tone: 'violet',
    },
  ];
});

const dashboardError = computed(() =>
  [
    physicalReq.error.value,
    digitalReq.error.value,
    borrowReq.error.value,
    reservationReq.error.value,
    usersReq.error.value,
    libraryReq.error.value,
    returnReq.error.value,
    recommendationReq.error.value,
  ].find(Boolean)
);

const isLoading = computed(
  () =>
    physicalReq.pending.value ||
    digitalReq.pending.value ||
    borrowReq.pending.value ||
    reservationReq.pending.value ||
    usersReq.pending.value ||
    libraryReq.pending.value ||
    returnReq.pending.value ||
    recommendationReq.pending.value
);

function openMaterial(material) {
  const type = normalizeStatus(material?.material_type) === 'DIGITAL' ? 'digital' : 'physical';
  router.push({
    path: `/material/${material?.id}`,
    query: { type },
  });
}

function loadDashboard() {
  physicalReq.send(() => getAllMaterials({ page: 1, size: 200 }, 'physical'));
  digitalReq.send(() => getAllMaterials({ page: 1, size: 200 }, 'digital'));
  borrowReq.send(() => getAllBorrows({ page: 1, size: 200 }));
  reservationReq.send(() => getAllReservation({ page: 1, size: 200 }));
  usersReq.send(() => getAllUser({ page: 1, size: 200 }));
  libraryReq.send(() => getAllLibrary({ page: 1, size: 200 }));
  returnReq.send(() => getAllReturns({ page: 1, size: 200 }));

  if (isMember.value) {
    recommendationReq.send(() => getRecommendedMaterials({ limit: 6, type: 'all' }));
  } else {
    recommendationReq.response.value = { results: [] };
  }
}

onMounted(() => {
  loadDashboard();
  unsubscribeEntitySync = subscribeEntityMutation('*', ({ entity }) => {
    if (['materials', 'borrows', 'reservations', 'returns', 'payments', 'users', 'libraries'].includes(entity)) {
      loadDashboard();
    }
  });
});

onBeforeUnmount(() => {
  unsubscribeEntitySync?.();
});
</script>

<template>
  <div class="dashboard-container">
    <!-- Hero Banner -->
    <section class="dashboard-hero">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">{{ dashboardTitle }}</h1>
          <p class="hero-subtitle">{{ dashboardSubtitle }}</p>
        </div>

        <div class="hero-actions">
          <button class="btn-outline" @click="loadDashboard">
            <BaseIcon :path="mdiRefresh" size="18" />
            Refresh
          </button>
          <button class="btn-primary" @click="router.push('/material')">
            <BaseIcon :path="mdiArrowRight" size="18" />
            Open materials
          </button>
        </div>
      </div>
    </section>

    <!-- Stat Cards Grid -->
    <div class="stats-grid">
      <DashboardStatCard
        v-for="card in statCards"
        :key="card.label"
        :label="card.label"
        :value="card.value"
        :description="card.description"
        :icon="card.icon"
        :tone="card.tone"
      />
    </div>

    <!-- Error & Loading States -->
    <div v-if="dashboardError" class="alert-error">
      Some dashboard data failed to load. Use refresh to try again.
    </div>

    <div v-if="isLoading" class="alert-info">
      Loading live dashboard insights...
    </div>

    <!-- Charts Row -->
    <div class="charts-grid">
      <div class="charts-main">
        <DashboardPanel
          :title="isMember ? 'My six-month activity' : 'Borrow and reservation momentum'"
          :subtitle="isMember ? 'Your own borrow and reservation history over the last six months' : 'System activity during the last six months'"
        >
          <DashboardActivityBarChart
            :labels="monthlyBorrows.labels"
            :borrow-series="monthlyBorrows.data"
            :reservation-series="monthlyReservations.data"
          />
        </DashboardPanel>
      </div>

      <div class="charts-side">
        <DashboardPanel title="Collection mix" subtitle="Availability and material-type balance">
          <DashboardMaterialPieChart
            :available="availableMaterials"
            :unavailable="unavailableMaterials"
            :physical="physicalMaterials.length"
            :digital="digitalMaterials.length"
          />
        </DashboardPanel>
      </div>
    </div>

    <!-- Quick Actions & Recommendations Row -->
    <div class="actions-grid">
      <div class="actions-side">
        <DashboardPanel title="Quick actions" subtitle="Jump directly into the work that matches your role">
          <div class="actions-list">
            <button
              v-for="action in quickActions"
              :key="action.label"
              class="action-card"
              @click="router.push(action.path)"
            >
              <div class="action-card-left">
                <div class="action-icon" :class="`tone-${action.tone}`">
                  <BaseIcon :path="action.icon" size="20" />
                </div>
                <div>
                  <p class="action-label">{{ action.label }}</p>
                  <p class="action-hint">Open page</p>
                </div>
              </div>
              <BaseIcon :path="mdiArrowRight" size="18" class="action-arrow" />
            </button>
          </div>
        </DashboardPanel>
      </div>

      <!-- Recommendations for Members -->
      <div v-if="isMember" class="actions-main">
        <DashboardPanel
          title="Recommended for you"
          :subtitle="recommendationStrategy === 'personalized' ? 'Built from your borrow and reservation history' : 'Popular resources when there is not enough personal history yet'"
        >
          <div v-if="recommendations.length" class="recommendations-grid">
            <button
              v-for="item in recommendations"
              :key="item.id"
              class="recommendation-card"
              @click="openMaterial(item)"
            >
              <div class="recommendation-header">
                <span class="badge-material">{{ item.material_type }}</span>
                <span v-if="item.material_type === 'PHYSICAL'" class="badge-stock">
                  {{ item.available_copies }} in stock
                </span>
              </div>
              <h3 class="recommendation-title">{{ item.title }}</h3>
              <p class="recommendation-author">{{ item.author || 'Unknown author' }}</p>
              <div class="recommendation-tags">
                <span class="tag">{{ item.category || 'General' }}</span>
                <span class="tag">{{ item.genre || 'Mixed' }}</span>
              </div>
              <p class="recommendation-reason">
                {{ item.reasons?.[0] || 'Recommended from current library activity' }}
              </p>
            </button>
          </div>

          <div v-else class="empty-state">
            Recommendations will appear here as soon as the dashboard has enough activity to work with.
          </div>
        </DashboardPanel>
      </div>

      <!-- Operational Watchlist for Staff/Admin -->
      <div v-else class="actions-main">
        <DashboardPanel title="Operational watchlist" subtitle="What needs attention first">
          <div class="watchlist-grid">
            <div class="watchlist-card">
              <p class="watchlist-title">Circulation</p>
              <div class="watchlist-stats">
                <div class="watchlist-stat">
                  <span class="stat-label">Active borrows</span>
                  <span class="stat-value">{{ activeBorrows }}</span>
                </div>
                <div class="watchlist-stat">
                  <span class="stat-label">Overdue borrows</span>
                  <span class="stat-value overdue">{{ overdueBorrows }}</span>
                </div>
                <div class="watchlist-stat">
                  <span class="stat-label">Reservations waiting</span>
                  <span class="stat-value">{{ activeReservations }}</span>
                </div>
              </div>
            </div>

            <div class="watchlist-card">
              <p class="watchlist-title">Collection</p>
              <div class="watchlist-stats">
                <div class="watchlist-stat">
                  <span class="stat-label">Total materials</span>
                  <span class="stat-value">{{ allMaterials.length }}</span>
                </div>
                <div class="watchlist-stat">
                  <span class="stat-label">Available now</span>
                  <span class="stat-value available">{{ availableMaterials }}</span>
                </div>
                <div class="watchlist-stat">
                  <span class="stat-label">Low stock alerts</span>
                  <span class="stat-value low-stock">{{ lowStockMaterials }}</span>
                </div>
              </div>
            </div>

            <div class="watchlist-card">
              <p class="watchlist-title">Users & branches</p>
              <div class="watchlist-stats">
                <div class="watchlist-stat">
                  <span class="stat-label">Members</span>
                  <span class="stat-value">{{ totalMembers }}</span>
                </div>
                <div class="watchlist-stat">
                  <span class="stat-label">Libraries</span>
                  <span class="stat-value">{{ libraries.length }}</span>
                </div>
                <div class="watchlist-stat">
                  <span class="stat-label">Digital resources</span>
                  <span class="stat-value">{{ digitalMaterials.length }}</span>
                </div>
              </div>
            </div>

            <div class="watchlist-card">
              <p class="watchlist-title">Fine status</p>
              <div class="watchlist-stats">
                <div class="watchlist-stat">
                  <span class="stat-label">Returned today</span>
                  <span class="stat-value">{{ returnedToday }}</span>
                </div>
                <div class="watchlist-stat">
                  <span class="stat-label">Unpaid fine total</span>
                  <span class="stat-value fine">ETB {{ unpaidFineTotal.toFixed(2) }}</span>
                </div>
                <div class="watchlist-stat">
                  <span class="stat-label">Return records</span>
                  <span class="stat-value">{{ returns.length }}</span>
                </div>
              </div>
            </div>
          </div>
        </DashboardPanel>
      </div>
    </div>

    <!-- Recent Activity Row -->
    <div class="recent-grid">
      <DashboardPanel
        :title="isMember ? 'My latest borrows' : 'Recent borrows'"
        :subtitle="isMember ? 'Your newest borrowing activity' : 'Latest circulation movement across the system'"
      >
        <div v-if="(isMember ? myBorrows : recentBorrows).length" class="recent-list">
          <div
            v-for="row in (isMember ? myBorrows.slice(0, 5) : recentBorrows)"
            :key="row?.id || row?.uuid"
            class="recent-item"
          >
            <div class="recent-item-header">
              <div>
                <p class="recent-item-title">{{ row?.material_title || 'Material' }}</p>
                <p class="recent-item-meta">
                  {{ isMember ? (row?.status || '-') : `${row?.member_name || '-'} • ${row?.status || '-'}` }}
                </p>
              </div>
              <span class="status-badge" :class="normalizeStatus(row?.status) === 'OVERDUE' ? 'status-overdue' : 'status-active'">
                {{ row?.status || 'UNKNOWN' }}
              </span>
            </div>
            <p class="recent-item-date">{{ formatDate(row?.borrow_date || row?.created_at) }}</p>
          </div>
        </div>
        <p v-else class="empty-message">No borrow activity found yet.</p>
      </DashboardPanel>

      <DashboardPanel
        :title="isMember ? 'My fines and reservations' : 'Returns and reservations'"
        :subtitle="isMember ? 'Outstanding charges and your latest holds' : 'Latest return records and reservation queue activity'"
      >
        <div v-if="isMember" class="member-fines">
          <div class="fine-card">
            <div>
              <p class="fine-label">Outstanding fine total</p>
              <p class="fine-amount">ETB {{ myOutstandingFineTotal.toFixed(2) }}</p>
            </div>
            <button class="btn-small" @click="router.push('/fine-payments')">
              Open payments
            </button>
          </div>

          <div v-if="myReservations.length" class="reservations-list">
            <div
              v-for="row in myReservations.slice(0, 4)"
              :key="row?.id || row?.uuid"
              class="reservation-item"
            >
              <p class="reservation-title">{{ row?.material_title || 'Reserved material' }}</p>
              <p class="reservation-status">{{ row?.status || '-' }}</p>
              <p class="reservation-date">{{ formatDate(row?.reserve_date || row?.created_at) }}</p>
            </div>
          </div>
          <p v-else class="empty-message">You do not have any reservation activity yet.</p>
        </div>

        <div v-else class="staff-activity">
          <div v-if="recentReturns.length" class="returns-list">
            <div
              v-for="row in recentReturns"
              :key="row?.id || row?.uuid"
              class="return-item"
            >
              <div class="return-item-header">
                <div>
                  <p class="return-item-title">{{ row?.material_title || 'Returned material' }}</p>
                  <p class="return-item-member">{{ row?.member_name || '-' }}</p>
                </div>
                <span class="fine-badge" :class="amount(row?.fine_amount) > 0 ? 'fine-positive' : 'fine-zero'">
                  {{ amount(row?.fine_amount) > 0 ? `ETB ${amount(row?.fine_amount).toFixed(2)}` : 'NO FINE' }}
                </span>
              </div>
              <p class="return-item-date">{{ formatDate(row?.return_date || row?.created_at) }}</p>
            </div>
          </div>
          <p v-else class="empty-message">No return activity found yet.</p>

          <div class="queue-card">
            <p class="queue-title">Reservation queue snapshot</p>
            <div class="queue-stats">
              <div>
                <p class="queue-label">Reserved</p>
                <p class="queue-value">{{ activeReservations }}</p>
              </div>
              <div>
                <p class="queue-label">Recent entries</p>
                <p class="queue-value">{{ recentReservations.length }}</p>
              </div>
            </div>
          </div>
        </div>
      </DashboardPanel>
    </div>
  </div>
</template>

<style scoped>
/* Dashboard Container */
.dashboard-container {
  min-height: 100vh;
  padding: 1rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  transition: background 0.3s ease;
 
}

.dark .dashboard-container {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

@media (min-width: 640px) {
  .dashboard-container {
    padding: 1.5rem;
  }
}

.space-y-6 > * + * {
  margin-top: 1.5rem;
}

/* Hero Banner */
.dashboard-hero {
  border-radius: 1.5rem;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(239, 68, 68, 0.1));
  border: 1px solid rgba(245, 158, 11, 0.2);
  padding: 1.5rem;
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
}

.dark .dashboard-hero {
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.3);
}

@media (min-width: 768px) {
  .dashboard-hero {
    padding: 2rem;
  }
}



@media (min-width: 1024px) {
  .hero-content {
    flex-direction: row;
    align-items: flex-end;
    justify-content: space-between;
  }
}

.hero-text {
  max-width: 64rem;
}

.hero-badge {
  font-size: 1.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.32em;
  color: #f59e0b;
}

.hero-title {
  margin-top: 1rem;
  font-size: 1.5rem;
  font-weight: 800;
  background: linear-gradient( #f59e0b);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.dark .hero-title {
  background: linear-gradient(135deg, #ffffff, #f59e0b);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

@media (min-width: 640px) {
  .hero-title {
    font-size: 2.25rem;
  }
}

.hero-subtitle {
  margin-top: 0.75rem;
  max-width: 36rem;
  font-size: 0.875rem;
  line-height: 1.5rem;
  color: #475569;
}

.dark .hero-subtitle {
  color: #94a3b8;
}

@media (min-width: 640px) {
  .hero-subtitle {
    font-size: 1rem;
  }
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.btn-outline {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  border-radius: 9999px;
  background: rgba(0, 0, 0, 0.05);
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #1e293b;
  transition: all 0.2s ease;
  border: 1px solid rgba(245, 158, 11, 0.3);
  cursor: pointer;
}

.dark .btn-outline {
  background: rgba(255, 255, 255, 0.08);
  color: white;
}

.btn-outline:hover {
  background: rgba(245, 158, 11, 0.1);
  border-color: rgba(245, 158, 11, 0.5);
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  border-radius: 9999px;
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: white;
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px -5px rgba(245, 158, 11, 0.4);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
   margin-top: 24px;
   margin-bottom: 32px;
}

@media (min-width: 640px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1280px) {
  .stats-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* Alerts */
.alert-error {
  border-radius: 1rem;
  border: 1px solid rgba(239, 68, 68, 0.3);
  background: rgba(239, 68, 68, 0.1);
  padding: 1rem;
  font-size: 0.875rem;
  color: #dc2626;
}

.dark .alert-error {
  color: #f87171;
}

.alert-info {
  border-radius: 1rem;
  border: 1px solid rgba(245, 158, 11, 0.3);
  background: rgba(245, 158, 11, 0.1);
  padding: 1rem;
  font-size: 0.875rem;
  color: #d97706;
}

.dark .alert-info {
  color: #fbbf24;
}

/* Charts Grid */
.charts-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 1280px) {
  .charts-grid {
    grid-template-columns: 2fr 1fr;
  }
}

.charts-main,
.charts-side {
  width: 100%;
  margin-bottom: 32px;
}

/* Actions Grid */
.actions-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 1280px) {
  .actions-grid {
    grid-template-columns: 1fr 2fr;
  }
}

.actions-side,
.actions-main {
  width: 100%;
}

/* Actions List */
.actions-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
  padding-right: 16px;
}

@media (min-width: 640px) {
  .actions-list {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1280px) {
  .actions-list {
    grid-template-columns: 1fr;
  }
}

.action-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-radius: 1rem;
  border: 1px solid rgba(203, 213, 225, 0.5);
  background: rgba(255, 255, 255, 0.5);
  padding: 1rem;
  text-align: left;
  transition: all 0.2s ease;
  cursor: pointer;
  width: 100%;
}

.dark .action-card {
  border: 1px solid rgba(51, 65, 85, 0.5);
  background: rgba(30, 41, 59, 0.5);
}

.action-card:hover {
  transform: translateY(-2px);
  border-color: rgba(245, 158, 11, 0.4);
  background: rgba(245, 158, 11, 0.05);
}

.dark .action-card:hover {
  background: rgba(30, 41, 59, 0.8);
}

.action-card-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.action-icon {
  display: grid;
  height: 2.75rem;
  width: 2.75rem;
  place-items: center;
  border-radius: 1rem;
  background: rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.dark .action-icon {
  background: rgba(15, 23, 42, 0.8);
}

.action-icon.tone-blue {
  color: #3b82f6;
}

.action-icon.tone-amber {
  color: #f59e0b;
}

.action-icon.tone-green {
  color: #10b981;
}

.action-icon.tone-violet {
  color: #8b5cf6;
}

.action-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #1e293b;
}

.dark .action-label {
  color: #f1f5f9;
}

.action-hint {
  font-size: 0.75rem;
  color: #64748b;
}

.action-arrow {
  color: #94a3b8;
  transition: transform 0.2s ease;
}

.action-card:hover .action-arrow {
  transform: translateX(4px);
  color: #f59e0b;
}

/* Recommendations Grid */
.recommendations-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 768px) {
  .recommendations-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1280px) {
  .recommendations-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.recommendation-card {
  border-radius: 1rem;
  border: 1px solid rgba(203, 213, 225, 0.5);
  background: rgba(255, 255, 255, 0.5);
  padding: 1rem;
  text-align: left;
  transition: all 0.2s ease;
  cursor: pointer;
}

.dark .recommendation-card {
  border: 1px solid rgba(51, 65, 85, 0.5);
  background: rgba(30, 41, 59, 0.5);
}

.recommendation-card:hover {
  transform: translateY(-2px);
  border-color: rgba(245, 158, 11, 0.4);
  background: rgba(245, 158, 11, 0.05);
}

.dark .recommendation-card:hover {
  background: rgba(30, 41, 59, 0.8);
}

.recommendation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.badge-material {
  border-radius: 9999px;
  background: #e2e8f0;
  padding: 0.25rem 0.625rem;
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.18em;
  color: #f59e0b;
}

.dark .badge-material {
  background: #0f172a;
}

.badge-stock {
  font-size: 0.75rem;
  font-weight: 600;
  color: #10b981;
}

.recommendation-title {
  margin-top: 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #1e293b;
}

.dark .recommendation-title {
  color: #f1f5f9;
}

.recommendation-author {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #64748b;
}

.recommendation-tags {
  margin-top: 1rem;
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  border-radius: 9999px;
  background: rgba(0, 0, 0, 0.05);
  padding: 0.25rem 0.625rem;
  font-size: 0.6875rem;
  font-weight: 500;
  color: #64748b;
}

.dark .tag {
  background: rgba(15, 23, 42, 0.8);
  color: #94a3b8;
}

.recommendation-reason {
  margin-top: 1rem;
  font-size: 0.75rem;
  line-height: 1.25rem;
  color: #94a3b8;
}

/* Watchlist Grid */
.watchlist-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 768px) {
  .watchlist-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.watchlist-card {
  border-radius: 1rem;
  border: 1px solid rgba(203, 213, 225, 0.5);
  background: rgba(255, 255, 255, 0.5);
  padding: 1rem;
}

.dark .watchlist-card {
  border: 1px solid rgba(51, 65, 85, 0.5);
  background: rgba(30, 41, 59, 0.5);
}

.watchlist-title {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  color: #f59e0b;
}

.watchlist-stats {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.watchlist-stat {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.875rem;
}

.stat-label {
  color: #64748b;
}

.stat-value {
  font-weight: 600;
  color: #1e293b;
}

.dark .stat-value {
  color: #f1f5f9;
}

.stat-value.overdue {
  color: #f59e0b;
}

.stat-value.available {
  color: #10b981;
}

.stat-value.low-stock {
  color: #ef4444;
}

.stat-value.fine {
  color: #ef4444;
}

/* Recent Activity Grid */
.recent-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  margin-top: 32px;
  padding-right: 32px;
}

@media (min-width: 1280px) {
  .recent-grid {
    grid-template-columns: 1fr 1fr;
  }
}

/* Recent Lists */
.recent-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.recent-item {
  border-radius: 1rem;
  border: 1px solid rgba(203, 213, 225, 0.5);
  background: rgba(255, 255, 255, 0.5);
  padding: 1rem;
}

.dark .recent-item {
  border: 1px solid rgba(51, 65, 85, 0.5);
  background: rgba(30, 41, 59, 0.5);
}

.recent-item-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.recent-item-title {
  font-weight: 600;
  color: #1e293b;
}

.dark .recent-item-title {
  color: #f1f5f9;
}

.recent-item-meta {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #64748b;
}

.status-badge {
  border-radius: 9999px;
  padding: 0.25rem 0.625rem;
  font-size: 0.6875rem;
  font-weight: 700;
}

.status-overdue {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
}

.status-active {
  background: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.recent-item-date {
  margin-top: 0.75rem;
  font-size: 0.75rem;
  color: #94a3b8;
}

/* Member Fines */
.member-fines {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.fine-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  border-radius: 1rem;
  border: 1px solid rgba(203, 213, 225, 0.5);
  background: rgba(255, 255, 255, 0.5);
  padding: 1rem;
}

.dark .fine-card {
  border: 1px solid rgba(51, 65, 85, 0.5);
  background: rgba(30, 41, 59, 0.5);
}

.fine-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  color: #64748b;
}

.fine-amount {
  margin-top: 0.5rem;
  font-size: 1.5rem;
  font-weight: 700;
  color: #ef4444;
}

.btn-small {
  border-radius: 9999px;
  background: #e2e8f0;
  padding: 0.5rem 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #1e293b;
  transition: all 0.2s ease;
  cursor: pointer;
  border: 1px solid rgba(245, 158, 11, 0.3);
}

.dark .btn-small {
  background: #0f172a;
  color: white;
}

.btn-small:hover {
  background: rgba(245, 158, 11, 0.2);
}

.reservations-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.reservation-item {
  border-radius: 1rem;
  border: 1px solid rgba(203, 213, 225, 0.5);
  background: rgba(255, 255, 255, 0.5);
  padding: 1rem;
}

.dark .reservation-item {
  border: 1px solid rgba(51, 65, 85, 0.5);
  background: rgba(30, 41, 59, 0.5);
}

.reservation-title {
  font-weight: 600;
  color: #1e293b;
}

.dark .reservation-title {
  color: #f1f5f9;
}

.reservation-status {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #64748b;
}

.reservation-date {
  margin-top: 0.75rem;
  font-size: 0.75rem;
  color: #94a3b8;
}

/* Staff Activity */
.staff-activity {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.returns-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.return-item {
  border-radius: 1rem;
  border: 1px solid rgba(203, 213, 225, 0.5);
  background: rgba(255, 255, 255, 0.5);
  padding: 1rem;
}

.dark .return-item {
  border: 1px solid rgba(51, 65, 85, 0.5);
  background: rgba(30, 41, 59, 0.5);
}

.return-item-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.return-item-title {
  font-weight: 600;
  color: #1e293b;
}

.dark .return-item-title {
  color: #f1f5f9;
}

.return-item-member {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #64748b;
}

.fine-badge {
  border-radius: 9999px;
  padding: 0.25rem 0.625rem;
  font-size: 0.6875rem;
  font-weight: 700;
}

.fine-positive {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.fine-zero {
  background: rgba(16, 185, 129, 0.2);
  color: #10b981;
}

.return-item-date {
  margin-top: 0.75rem;
  font-size: 0.75rem;
  color: #94a3b8;
}

.queue-card {
  border-radius: 1rem;
  border: 1px solid rgba(203, 213, 225, 0.5);
  background: rgba(255, 255, 255, 0.5);
  padding: 1rem;
}

.dark .queue-card {
  border: 1px solid rgba(51, 65, 85, 0.5);
  background: rgba(30, 41, 59, 0.5);
}

.queue-title {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  color: #f59e0b;
}

.queue-stats {
  margin-top: 0.75rem;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.queue-label {
  font-size: 0.75rem;
  color: #64748b;
}

.queue-value {
  margin-top: 0.25rem;
  font-size: 1.25rem;
  font-weight: 700;
  color: #1e293b;
}

.dark .queue-value {
  color: #f1f5f9;
}

.empty-state,
.empty-message {
  border-radius: 1rem;
  border: 1px dashed rgba(203, 213, 225, 0.5);
  background: rgba(0, 0, 0, 0.02);
  padding: 1.5rem;
  font-size: 0.875rem;
  text-align: center;
  color: #94a3b8;
}

.dark .empty-state,
.dark .empty-message {
  border: 1px dashed rgba(51, 65, 85, 0.5);
  background: rgba(30, 41, 59, 0.3);
}



/* Hero Banner */
.dashboard-hero {
  border-radius: 1.5rem;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(239, 68, 68, 0.1));
  border: 1px solid rgba(245, 158, 11, 0.2);
  padding: 1.5rem;
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.1);
}

.dark .dashboard-hero {
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.3);
}

@media (min-width: 768px) {
  .dashboard-hero {
    padding: 2rem;
  }
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

@media (min-width: 1024px) {
  .hero-content {
    flex-direction: row;
    align-items: flex-end;
    justify-content: space-between;
  }
}

.hero-text {
  max-width: 64rem;
}

.hero-badge {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.32em;
  color: #f59e0b;
}

.hero-title {
  margin-top: 0.5rem;
  font-size: 1.875rem;
  font-weight: 800;
  line-height: 1.2;
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.dark .hero-title {
  background: linear-gradient(135deg, #fbbf24, #f87171);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

@media (min-width: 640px) {
  .hero-title {
    font-size: 2.5rem;
  }
}

@media (min-width: 1024px) {
  .hero-title {
    font-size: 3rem;
  }
}

.hero-subtitle {
  margin-top: 0.75rem;
  max-width: 36rem;
  font-size: 0.875rem;
  line-height: 1.5rem;
  color: #475569;
}

.dark .hero-subtitle {
  color: #94a3b8;
}

@media (min-width: 640px) {
  .hero-subtitle {
    font-size: 1rem;
  }
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
}
</style>