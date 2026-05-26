<script setup>
import { computed, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useApiRequest } from '@/composables/useApiRequest';
import {
  getMaterialBookmarks,
  getMaterialFavorites,
  removeMaterialBookmark,
  removeMaterialFavorite,
} from '../api/materialApi';
import { secondDateFormat, toasted } from '@/utils/utils';
import BaseIcon from '@/components/base/BaseIcon.vue';
import defaultCover from '@/assets/default-coverpage.png';
import {
  mdiBookmark,
  mdiBookOpenVariant,
  mdiChevronRight,
  mdiDeleteOutline,
  mdiHeart,
  mdiLibraryShelves,
  mdiOpenInNew,
} from '@mdi/js';

const router = useRouter();
const favoritesReq = useApiRequest();
const bookmarksReq = useApiRequest();
const actionReq = useApiRequest();
const activeTab = ref('favorites');

function rowsFromPayload(payload) {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.result)) return payload.result;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.data)) return payload.data;
  return [];
}

const favoriteRows = computed(() => rowsFromPayload(favoritesReq.response.value));
const bookmarkRows = computed(() => rowsFromPayload(bookmarksReq.response.value));
const visibleRows = computed(() =>
  activeTab.value === 'favorites' ? favoriteRows.value : bookmarkRows.value
);

const statCards = computed(() => [
  { label: 'Favorite Materials', value: favoriteRows.value.length, icon: mdiHeart, tone: 'favorite' },
  { label: 'Bookmark Collection', value: bookmarkRows.value.length, icon: mdiBookmark, tone: 'bookmark' },
]);

function loadSavedMaterials() {
  favoritesReq.send(() => getMaterialFavorites());
  bookmarksReq.send(() => getMaterialBookmarks());
}

function openMaterial(row) {
  const materialId = row?.material?.id || row?.material_id;
  if (!materialId) return;
  router.push({
    path: `/material/${materialId}`,
    query: { type: row?.material_type || 'physical' },
  });
}

function removeSavedItem(row) {
  const isFavoritesTab = activeTab.value === 'favorites';
  const request = isFavoritesTab
    ? () => removeMaterialFavorite(row.id)
    : () => removeMaterialBookmark(row.id);

  actionReq.send(request, (res) => {
    if (!res?.success) {
      toasted(false, '', res?.error || 'Failed to remove saved material');
      return;
    }
    toasted(true, isFavoritesTab ? 'Removed from favorites' : 'Removed from bookmarks');
    loadSavedMaterials();
  });
}

function getMaterialMeta(row) {
  const material = row?.material || {};
  if (row?.material_type === 'digital') return material?.format || 'Digital';
  return material?.condition || 'Physical';
}

function getSecondaryMeta(row) {
  const material = row?.material || {};
  if (row?.material_type === 'digital') return material?.file_size || material?.language || '-';
  const available = Number(material?.available_copies ?? 0);
  const total = Number(material?.total_copies ?? 0);
  return `${available}/${total}`;
}

loadSavedMaterials();
</script>

<template>
  <div class="saved-materials-page">
    <section class="page-hero">
      <div>
        <p class="eyebrow">Saved Materials</p>
        <h1>Keep track of your favorite and bookmarked materials in one place</h1>
      </div>
      <div class="hero-icon">
        <BaseIcon :path="mdiLibraryShelves" size="36" />
      </div>
    </section>

    <section class="stats-grid">
      <article
        v-for="card in statCards"
        :key="card.label"
        class="stat-card"
        :class="`stat-card-${card.tone}`"
      >
        <div>
          <p class="stat-label">{{ card.label }}</p>
          <p class="stat-value">{{ card.value }}</p>
        </div>
        <div class="stat-icon" :class="`stat-icon-${card.tone}`">
          <BaseIcon :path="card.icon" size="24" />
        </div>
      </article>
    </section>

    <section class="tab-panel">
      <button
        class="tab-button"
        :class="{ active: activeTab === 'favorites' }"
        @click="activeTab = 'favorites'"
      >
        <BaseIcon :path="mdiHeart" size="18" />
        Favorite Materials
      </button>
      <button
        class="tab-button"
        :class="{ active: activeTab === 'bookmarks' }"
        @click="activeTab = 'bookmarks'"
      >
        <BaseIcon :path="mdiBookmark" size="18" />
        Bookmark Collection
      </button>
    </section>

    <section v-if="favoritesReq.pending.value || bookmarksReq.pending.value" class="loading-state">
      <div class="loading-spinner" />
      <p>Loading saved materials...</p>
    </section>

    <section v-else-if="visibleRows.length" class="saved-grid">
      <article
        v-for="row in visibleRows"
        :key="row.id"
        class="saved-card"
        :class="activeTab === 'favorites' ? 'saved-card-favorite' : 'saved-card-bookmark'"
      >
        <div class="saved-cover">
          <img :src="defaultCover" :alt="row?.material?.title || row?.material_title || 'Material cover'" />
          <span class="saved-type">{{ row?.material_type || 'material' }}</span>
          <span class="saved-badge" :class="activeTab === 'favorites' ? 'badge-favorite' : 'badge-bookmark'">
            <BaseIcon :path="activeTab === 'favorites' ? mdiHeart : mdiBookmark" size="18" />
            {{ activeTab === 'favorites' ? 'Favorited' : 'Bookmarked' }}
          </span>
        </div>

        <div class="saved-content">
          <p class="saved-library">{{ row?.material?.library_name || 'Library collection' }}</p>
          <button type="button" class="saved-title" @click="openMaterial(row)">
            {{ row?.material?.title || row?.material_title || 'Untitled' }}
          </button>
          <p class="saved-author">{{ row?.material?.author || '-' }}</p>

          <div class="saved-meta">
            <span>{{ row?.material?.category || row?.material?.genre || '-' }}</span>
            <span>{{ getMaterialMeta(row) }}</span>
            <span>{{ getSecondaryMeta(row) }}</span>
          </div>

          <p class="saved-date">Saved on {{ secondDateFormat(row?.created_at) }}</p>

          <div class="saved-actions">
            <button type="button" class="primary-action" @click="openMaterial(row)">
              <BaseIcon :path="mdiOpenInNew" size="16" />
              View details
            </button>
            <button
              type="button"
              class="secondary-action"
              :disabled="actionReq.pending.value"
              @click="removeSavedItem(row)"
            >
              <BaseIcon :path="mdiDeleteOutline" size="16" />
              {{ activeTab === 'favorites' ? 'Remove from favorites' : 'Remove from bookmarks' }}
            </button>
          </div>
        </div>
      </article>
    </section>

    <section v-else class="empty-state">
      <div class="empty-icon" :class="activeTab === 'favorites' ? 'empty-icon-favorite' : 'empty-icon-bookmark'">
        <BaseIcon :path="activeTab === 'favorites' ? mdiHeart : mdiBookmark" size="36" />
      </div>
      <h3>{{ activeTab === 'favorites' ? 'No favorite materials yet' : 'No bookmarked materials yet' }}</h3>
      <p>
        {{
          activeTab === 'favorites'
            ? 'Materials you favorite will appear here'
            : 'Materials you bookmark for later will appear here'
        }}
      </p>
      <button type="button" class="browse-action" @click="router.push('/material')">
        <BaseIcon :path="mdiBookOpenVariant" size="18" />
        Open material
        <BaseIcon :path="mdiChevronRight" size="18" />
      </button>
    </section>
  </div>
</template>

<style scoped>
.saved-materials-page {
  min-height: 100%;
  display: grid;
  gap: 1.5rem;
}

.page-hero {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 1.5rem;
  border-radius: 1.5rem;
  background:
    radial-gradient(circle at top left, rgba(245, 158, 11, 0.24), transparent 38%),
    linear-gradient(135deg, #fff7ed 0%, #fffbeb 45%, #ffffff 100%);
  border: 1px solid rgba(245, 158, 11, 0.2);
  box-shadow: 0 20px 40px rgba(15, 23, 42, 0.08);
}

.dark .page-hero {
  background:
    radial-gradient(circle at top left, rgba(245, 158, 11, 0.2), transparent 38%),
    linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.95) 100%);
  border-color: rgba(245, 158, 11, 0.18);
}

.eyebrow {
  margin: 0 0 0.4rem;
  font-size: 0.75rem;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: #c2410c;
  font-weight: 700;
}

.page-hero h1 {
  margin: 0;
  font-size: clamp(1.4rem, 2vw, 2rem);
  line-height: 1.2;
  color: #0f172a;
  max-width: 42rem;
}

.dark .page-hero h1 {
  color: #f8fafc;
}

.hero-icon {
  display: grid;
  place-items: center;
  width: 4rem;
  height: 4rem;
  border-radius: 1.25rem;
  background: linear-gradient(135deg, #f59e0b, #ea580c);
  color: white;
  box-shadow: 0 14px 28px rgba(245, 158, 11, 0.28);
  flex-shrink: 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.stat-card {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  padding: 1.25rem;
  border-radius: 1.25rem;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(226, 232, 240, 0.9);
}

.stat-card-favorite {
  border-color: rgba(239, 68, 68, 0.25);
}

.stat-card-bookmark {
  border-color: rgba(16, 185, 129, 0.25);
}

.dark .stat-card {
  background: rgba(15, 23, 42, 0.82);
  border-color: rgba(51, 65, 85, 0.9);
}

.stat-label {
  margin: 0;
  color: #64748b;
  font-size: 0.88rem;
}

.stat-value {
  margin: 0.35rem 0 0;
  font-size: 1.7rem;
  font-weight: 700;
  color: #0f172a;
}

.dark .stat-value {
  color: #f8fafc;
}

.stat-icon {
  display: grid;
  place-items: center;
  width: 3rem;
  height: 3rem;
  border-radius: 1rem;
}

.stat-icon-favorite {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.12);
}

.stat-icon-bookmark {
  color: #10b981;
  background: rgba(16, 185, 129, 0.12);
}

.tab-panel {
  display: inline-flex;
  width: fit-content;
  gap: 0.5rem;
  padding: 0.35rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(226, 232, 240, 0.9);
}

.dark .tab-panel {
  background: rgba(15, 23, 42, 0.82);
  border-color: rgba(51, 65, 85, 0.9);
}

.tab-button {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.7rem 1rem;
  border-radius: 999px;
  font-size: 0.92rem;
  color: #475569;
  transition: all 0.2s ease;
}

.tab-button.active {
  color: white;
  background: linear-gradient(135deg, #f59e0b, #ea580c);
  box-shadow: 0 10px 22px rgba(245, 158, 11, 0.24);
}

.saved-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.25rem;
}

.saved-card {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-radius: 1.25rem;
  background: #fff;
  border: 1px solid #e2e8f0;
  box-shadow: 0 12px 28px rgba(15, 23, 42, 0.08);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.saved-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 18px 36px rgba(15, 23, 42, 0.12);
}

.saved-card-favorite {
  border-top: 3px solid #ef4444;
}

.saved-card-bookmark {
  border-top: 3px solid #10b981;
}

.dark .saved-card {
  background: rgba(15, 23, 42, 0.92);
  border-color: rgba(51, 65, 85, 0.9);
}

.saved-cover {
  position: relative;
  aspect-ratio: 16 / 10;
  background: linear-gradient(135deg, #f8fafc, #e2e8f0);
}

.saved-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.saved-type {
  position: absolute;
  top: 0.75rem;
  left: 0.75rem;
  padding: 0.3rem 0.65rem;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.75);
  color: white;
  font-size: 0.7rem;
  text-transform: capitalize;
}

.saved-badge {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.4rem 0.7rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  color: white;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
}

.badge-favorite {
  background: #ef4444;
}

.badge-bookmark {
  background: #10b981;
}

.saved-content {
  display: grid;
  gap: 0.65rem;
  padding: 1.1rem 1.15rem 1.2rem;
  flex: 1;
}

.saved-library,
.saved-author,
.saved-date {
  margin: 0;
  color: #64748b;
  font-size: 0.85rem;
}

.saved-title {
  padding: 0;
  text-align: left;
  font-size: 1.05rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.35;
}

.dark .saved-title {
  color: #f8fafc;
}

.saved-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}

.saved-meta span {
  padding: 0.3rem 0.6rem;
  border-radius: 999px;
  background: rgba(245, 158, 11, 0.1);
  color: #9a3412;
  font-size: 0.72rem;
  font-weight: 600;
}

.saved-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: auto;
  padding-top: 0.5rem;
}

.primary-action,
.secondary-action,
.browse-action {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  border-radius: 0.85rem;
  padding: 0.65rem 0.9rem;
  font-size: 0.85rem;
  transition: all 0.2s ease;
}

.primary-action,
.browse-action {
  color: white;
  background: linear-gradient(135deg, #f59e0b, #ea580c);
}

.secondary-action {
  color: #64748b;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
}

.dark .secondary-action {
  background: #1e293b;
  border-color: #334155;
  color: #cbd5e1;
}

.loading-state,
.empty-state {
  min-height: 280px;
  display: grid;
  place-items: center;
  text-align: center;
  gap: 0.75rem;
  padding: 2rem;
  border-radius: 1.4rem;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(226, 232, 240, 0.9);
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  display: grid;
  place-items: center;
  border-radius: 1rem;
}

.empty-icon-favorite {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}

.empty-icon-bookmark {
  background: rgba(16, 185, 129, 0.12);
  color: #10b981;
}

.loading-spinner {
  width: 3rem;
  height: 3rem;
  border-radius: 999px;
  border: 3px solid rgba(245, 158, 11, 0.2);
  border-top-color: #f59e0b;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 640px) {
  .tab-panel {
    width: 100%;
    display: grid;
  }

  .tab-button {
    justify-content: center;
  }

  .saved-actions {
    display: grid;
  }
}
</style>
