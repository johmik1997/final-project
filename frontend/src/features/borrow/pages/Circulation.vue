<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue';
import Table from '@/components/Table.vue';
import { useApiRequest } from '@/composables/useApiRequest';
import { openModal } from '@customizer/modal-x';
import BaseIcon from '@/components/base/BaseIcon.vue';
import DashboardPanel from '@/features/dashboard/components/DashboardPanel.vue';
import {
  mdiSwapHorizontal,
  mdiPlus,
  mdiCheck,
  mdiMagnify,
  mdiBookshelf,
  mdiAccountClock,
  mdiCheckCircle,
} from '@mdi/js';
import { secondDateFormatWithTime, toasted } from '@/utils/utils';
import { getAllCirculation, returnCirculation } from '../api/circulationApi';
import { useCirculation } from '../store/circulationStore';
import AddCirculation from './AddCirculation.mdl.vue';
import { emitEntityMutation, subscribeEntityMutation } from '@/utils/entitySync';

const circStore = useCirculation();
const req = useApiRequest();
const returnReq = useApiRequest();
const searchQuery = ref('');
let unsubscribeEntitySync = () => {};

onMounted(() => {
  fetchCirculations();
  unsubscribeEntitySync = subscribeEntityMutation('circulations', () => {
    fetchCirculations();
  });
});

onBeforeUnmount(() => {
  unsubscribeEntitySync?.();
});

function fetchCirculations() {
  req.send(() => getAllCirculation({ size: 100 }), (res) => {
    if (res?.success) {
      circStore.set(res.data?.result || res.data?.results || res.data || []);
    }
  });
}

const filteredCirculations = computed(() => {
  const rows = circStore.circulations || [];
  const query = searchQuery.value.trim().toLowerCase();
  if (!query) return rows;

  return rows.filter((row) =>
    [row?.material_title, row?.material_author, row?.member_name, row?.member_id, row?.status]
      .filter(Boolean)
      .some((value) => String(value).toLowerCase().includes(query))
  );
});

const stats = computed(() => {
  const rows = circStore.circulations || [];
  return {
    total: rows.length,
    active: rows.filter((row) => row?.status === 'BORROWED').length,
    returned: rows.filter((row) => row?.status === 'RETURNED').length,
  };
});

function openAddCirculationModal() {
  openModal('AddCirculation', {}, () => {
    fetchCirculations();
  });
}

function handleReturn(row) {
  openModal(
    'Confirmation',
    {
      title: 'Return Circulation Material',
      message: 'Are you sure you want to mark this material as returned to the shelf?',
    },
    (confirm) => {
      if (!confirm) return;

      returnReq.send(
        () => returnCirculation(row.id),
        (res) => {
          if (res.success) {
            toasted(true, 'Material returned to shelf');
            fetchCirculations();
            emitEntityMutation('circulations', { action: 'updated', id: row.id, status: 'RETURNED' });
          } else {
            toasted(false, res.error || 'Failed to return material');
          }
        }
      );
    }
  );
}
</script>

<template>
  <div class="circulation-page">
    <section class="circulation-hero">
      <div class="hero-text">
        <p class="hero-eyebrow">Shelf circulation</p>
        <h1>On-site shelf circulation</h1>
        <p class="hero-subtitle">In-library reading checkouts for materials currently on the shelf.</p>
      </div>
      <button type="button" class="btn-primary" @click="openAddCirculationModal">
        <BaseIcon :path="mdiPlus" size="18" />
        Log shelf circulation
      </button>
    </section>

    <div class="stats-grid">
      <article class="stat-card">
        <div>
          <p class="stat-label">Total circulations</p>
          <p class="stat-value">{{ stats.total }}</p>
        </div>
        <div class="stat-icon tone-blue">
          <BaseIcon :path="mdiBookshelf" size="22" />
        </div>
      </article>
      <article class="stat-card">
        <div>
          <p class="stat-label">Reading now</p>
          <p class="stat-value">{{ stats.active }}</p>
        </div>
        <div class="stat-icon tone-amber">
          <BaseIcon :path="mdiAccountClock" size="22" />
        </div>
      </article>
      <article class="stat-card">
        <div>
          <p class="stat-label">Returned to shelf</p>
          <p class="stat-value">{{ stats.returned }}</p>
        </div>
        <div class="stat-icon tone-green">
          <BaseIcon :path="mdiCheckCircle" size="22" />
        </div>
      </article>
    </div>

    <DashboardPanel title="Circulation records" subtitle="Search and manage on-site shelf sessions">
      <div class="toolbar">
        <div class="search-wrap">
          <BaseIcon :path="mdiMagnify" size="20" class="search-icon" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by material, member, or status..."
            class="search-input"
          />
        </div>
      </div>

      <Table
        :pending="req.pending.value"
        :show-pagination="false"
        :rows="filteredCirculations"
        :headers="{
          head: ['Material', 'Member', 'Status', 'Logged At', 'Actions'],
          row: ['material_title', 'member_name', 'status', 'created_at'],
        }"
        :cells="{
          created_at: (val) => secondDateFormatWithTime(val) || '-',
          status: (val) => {
            const map = {
              BORROWED: 'Reading in-site',
              RETURNED: 'On shelf',
            };
            return map[val] || val;
          },
        }"
      >
        <template #actions="{ row }">
          <div class="table-actions">
            <button
              v-if="row.status === 'BORROWED'"
              type="button"
              class="btn-return"
              @click="handleReturn(row)"
            >
              <BaseIcon :path="mdiCheck" size="16" />
              Return to shelf
            </button>
            <span v-else class="text-muted">Completed</span>
          </div>
        </template>
      </Table>
    </DashboardPanel>
  </div>
</template>

<style scoped>
.circulation-page {
  display: grid;
  gap: 1.25rem;
  padding-bottom: 2rem;
}

.circulation-hero {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1.5rem 1.75rem;
  border-radius: 1rem;
  background: linear-gradient(
    135deg,
    rgba(245, 158, 11, 0.15),
    rgba(239, 68, 68, 0.1)
  );
  border: 1px solid #fde68a;
}

/* Dark Mode */
.dark .circulation-hero {
  background: linear-gradient(
    135deg,
    rgba(245, 158, 11, 0.18),
    rgba(239, 68, 68, 0.16)
  );
  border-color: rgba(216, 157, 54, 0.2);
}

.hero-eyebrow {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #fbbf24;
  margin: 0 0 0.35rem;
}

.circulation-hero h1 {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 800;
}

.hero-subtitle {
  margin: 0.5rem 0 0;
  max-width: 32rem;
  font-size: 0.9rem;
  color: #f59e0b;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  padding: 0.65rem 1.1rem;
  border-radius: 0.65rem;
  background: linear-gradient(135deg, #f59e0b, #ea580c);
  color: #0f172a;
  font-weight: 700;
  font-size: 0.875rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.1rem 1.2rem;
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid #e2e8f0;
}

.dark .stat-card {
  background: rgba(30, 41, 59, 0.7);
  border-color: #334155;
}

.stat-label {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #64748b;
}

.stat-value {
  margin: 0.35rem 0 0;
  font-size: 1.6rem;
  font-weight: 800;
  color: #0f172a;
}

.dark .stat-value {
  color: #f1f5f9;
}

.stat-icon {
  width: 2.75rem;
  height: 2.75rem;
  display: grid;
  place-items: center;
  border-radius: 0.85rem;
}

.tone-blue {
  background: rgba(59, 130, 246, 0.12);
  color: #3b82f6;
}

.tone-amber {
  background: rgba(245, 158, 11, 0.12);
  color: #f59e0b;
}

.tone-green {
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
}

.toolbar {
  margin-bottom: 1rem;
}

.search-wrap {
  position: relative;
  max-width: 28rem;
}

.search-icon {
  position: absolute;
  left: 0.9rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
}

.search-input {
  width: 100%;
  padding: 0.65rem 0.9rem 0.65rem 2.6rem;
  border-radius: 0.65rem;
  border: 1px solid #e2e8f0;
  background: #fff;
  font-size: 0.875rem;
}

.dark .search-input {
  background: #1e293b;
  border-color: #334155;
  color: #f1f5f9;
}

.table-actions {
  display: flex;
  justify-content: flex-end;
  margin-left:-48px;
}

.btn-return {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.45rem 0.85rem;
  border-radius: 0.5rem;
  background: linear-gradient(135deg, #f59e0b, #ea580c);
  color: #0f172a;
  font-size: 0.75rem;
  font-weight: 700;
}

.text-muted {
  font-size: 0.75rem;
  color: #94a3b8;
}
</style>
