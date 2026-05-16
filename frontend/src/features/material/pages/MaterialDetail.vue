<template>
  <div class="material-detail-container">
    <!-- Back Button -->
    <button class="back-button" @click="goBack">
      <BaseIcon :path="mdiArrowLeft" size="20" />
      <span>Back to Materials</span>
    </button>

    <!-- Loading State -->
    <div v-if="detailReq.pending.value" class="loading-state">
      <div class="loading-spinner"></div>
      <p>Loading material details...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="!material" class="error-state">
      <BaseIcon :path="mdiAlertCircle" size="48" />
      <h3>Material Not Found</h3>
      <p>The material you're looking for doesn't exist or has been removed.</p>
    </div>

    <!-- Material Content -->
    <template v-else>
      <!-- Hero Section -->
      <div class="hero-section">
        <div class="hero-grid">
          <!-- Image Column -->
          <div class="hero-image">
            <div class="image-wrapper">
              <img
                :src="imageSrc"
                :alt="material?.title || 'Material cover'"
                @error="onImageError"
              />
            </div>
          </div>

          <!-- Info Column -->
          <div class="hero-info">
            <div class="badges">
              <span class="badge-type">{{ activeType }}</span>
              <span v-if="isPhysicalMaterial" class="badge-status" :class="material?.available_copies > 0 ? 'status-available' : 'status-unavailable'">
                {{ material?.available_copies > 0 ? 'Available now' : 'Waitlist only' }}
              </span>
              <span v-else class="badge-status status-digital">Digital access</span>
              <span v-if="material?.library_name" class="badge-library">{{ material?.library_name }}</span>
            </div>

            <h1 class="title">{{ material?.title || 'Untitled' }}</h1>
            <p class="author">
              <BaseIcon :path="mdiAccount" size="18" />
              {{ material?.author || '-' }}
            </p>

            <!-- Action Buttons - Show for all users (members can also bookmark/favorite) -->
            <div class="action-buttons">
              <button class="btn-favorite" @click="toggleFavorite">
                <BaseIcon :path="favoriteRecordId ? mdiHeart : mdiHeartOutline" size="20" />
                {{ favoriteRecordId ? 'Favorited' : 'Favorite' }}
              </button>
              <button class="btn-bookmark" @click="toggleBookmark">
                <BaseIcon :path="bookmarkRecordId ? mdiBookmark : mdiBookmarkOutline" size="20" />
                {{ bookmarkRecordId ? 'Bookmarked' : 'Bookmark' }}
              </button>
            </div>

            <!-- Stats Cards -->
            <div class="stats-cards">
              <div v-for="card in statsCards" :key="card.label" class="stat-card">
                <p class="stat-label">{{ card.label }}</p>
                <p class="stat-value">{{ card.value }}</p>
              </div>
            </div>

            <!-- Action Buttons for Borrow/Read - Hide for members -->
            <div v-if="!currentUserIsMember && ((!isPhysicalMaterial && canShowDigitalActions) || (isPhysicalMaterial && !currentUserIsMember))" class="primary-actions">
              <template v-if="isPhysicalMaterial">
                <button class="btn-primary" :disabled="!canBorrow" @click="goToBorrow">
                  Borrow now
                </button>
                <button class="btn-secondary" :disabled="!canReserve" @click="goToReserve">
                  <BaseIcon :path="mdiLockClock" size="16" />
                  Join reservation queue
                </button>
              </template>
              <template v-else>
                <button class="btn-primary" :disabled="!isPdfMaterial" @click="goToReadMaterial">
                  <BaseIcon :path="mdiFilePdfBox" size="16" />
                  Read PDF
                </button>
                <button class="btn-secondary" :disabled="!hasDigitalFile" @click="openDigitalFile">
                  <BaseIcon :path="mdiOpenInNew" size="16" />
                  Open file
                </button>
              </template>
            </div>
          </div>
        </div>
      </div>

      <!-- Details Grid -->
      <div class="details-grid">
        <!-- Left Column -->
        <div class="details-left">
          <!-- Summary Section -->
          <div class="detail-card">
            <div class="card-header">
              <h3>Summary</h3>
              <p>Auto-generated description for this material</p>
            </div>
            <div class="summary-content">
              <p>{{ summaryText }}</p>
            </div>
          </div>

          <!-- Reader Review Form - Only show for members -->
          <div v-if="currentUserIsMember" class="detail-card">
            <div class="card-header">
              <h3>Write a Review</h3>
              <p>Share your thoughts about this material</p>
            </div>

            <div class="rating-input">
              <button
                v-for="value in [1, 2, 3, 4, 5]"
                :key="value"
                class="star-btn"
                @click="setRating(value)"
              >
                <BaseIcon 
                  :path="reviewForm.rating >= value ? mdiStar : mdiStarOutline" 
                  size="28" 
                  class="star" 
                  :class="{ 'star-filled': reviewForm.rating >= value }"
                />
              </button>
            </div>

            <textarea
              v-model="reviewForm.comment"
              rows="4"
              class="review-textarea"
              placeholder="Share what makes this material useful, memorable, or difficult..."
            />

            <button 
              class="btn-submit" 
              :disabled="reviewReq.pending.value" 
              @click="saveReview"
            >
              <span v-if="reviewReq.pending.value" class="button-spinner"></span>
              <span v-else>{{ feedbackRecordId ? 'Update Review' : 'Submit Review' }}</span>
            </button>
          </div>
        </div>

        <!-- Right Column -->
        <div class="details-right">
          <!-- Specifications -->
          <div class="detail-card">
            <div class="card-header">
              <h3>Specifications</h3>
              <p>Technical details and metadata</p>
            </div>

            <div class="specs-grid">
              <div class="spec-item">
                <BaseIcon :path="mdiTag" size="16" />
                <div>
                  <p class="spec-label">Category</p>
                  <p class="spec-value">{{ material?.category || '-' }}</p>
                </div>
              </div>
              <div class="spec-item">
                <BaseIcon :path="mdiSchoolOutline" size="16" />
                <div>
                  <p class="spec-label">Department</p>
                  <p class="spec-value">{{ material?.department || '-' }}</p>
                </div>
              </div>
              <div class="spec-item">
                <BaseIcon :path="mdiTranslate" size="16" />
                <div>
                  <p class="spec-label">Language</p>
                  <p class="spec-value">{{ material?.language || '-' }}</p>
                </div>
              </div>
              <div class="spec-item">
                <BaseIcon :path="mdiBarcode" size="16" />
                <div>
                  <p class="spec-label">ISBN</p>
                  <p class="spec-value">{{ material?.isbn || 'N/A' }}</p>
                </div>
              </div>
              <div v-if="isPhysicalMaterial" class="spec-item">
                <BaseIcon :path="mdiPackageVariantClosed" size="16" />
                <div>
                  <p class="spec-label">Stock</p>
                  <p class="spec-value">{{ material?.available_copies }}/{{ material?.total_copies }}</p>
                </div>
              </div>
              <div v-else class="spec-item">
                <BaseIcon :path="mdiFilePdfBox" size="16" />
                <div>
                  <p class="spec-label">Format</p>
                  <p class="spec-value">{{ material?.format || 'PDF' }}</p>
                </div>
              </div>
              <div class="spec-item">
                <BaseIcon :path="mdiCalendarClock" size="16" />
                <div>
                  <p class="spec-label">Published</p>
                  <p class="spec-value">{{ material?.published_date || '-' }}</p>
                </div>
              </div>
              <div class="spec-item">
                <BaseIcon :path="mdiBookOpenPageVariant" size="16" />
                <div>
                  <p class="spec-label">Genre</p>
                  <p class="spec-value">{{ material?.genre || '-' }}</p>
                </div>
              </div>
              <div class="spec-item">
                <BaseIcon :path="mdiMapMarkerOutline" size="16" />
                <div>
                  <p class="spec-label">Location</p>
                  <p class="spec-value">{{ material?.location || material?.library_name || '-' }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Community Comments -->
          <div class="detail-card">
            <div class="card-header">
              <h3>Community Comments</h3>
              <p>What other readers think</p>
            </div>

            <div class="comments-list">
              <div v-for="row in feedbackRows" :key="row?.id" class="comment-item">
                <div class="comment-header">
                  <div>
                    <p class="comment-author">{{ row?.user_name || 'Reader' }}</p>
                    <div class="comment-rating">
                      <BaseIcon
                        v-for="value in [1, 2, 3, 4, 5]"
                        :key="`${row?.id}-${value}`"
                        :path="Number(row?.rating || 0) >= value ? mdiStar : mdiStarOutline"
                        size="14"
                        class="star-icon"
                        :class="{ 'star-icon-filled': Number(row?.rating || 0) >= value }"
                      />
                    </div>
                  </div>
                  <span class="comment-date">{{ row?.updated_at?.slice?.(0, 10) || '' }}</span>
                </div>
                <p class="comment-text">{{ row?.comment || 'This reader left a rating without a written note.' }}</p>
              </div>

              <div v-if="!feedbackRows.length && !allFeedbackReq.pending.value" class="empty-comments">
                <BaseIcon :path="mdiCommentTextOutline" size="32" />
                <p>No comments yet</p>
                <span>Be the first to share your thoughts</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useApiRequest } from '@/composables/useApiRequest';
import { normalizeRoleValue } from '@/utils/authNavigation';
import {
  createMaterialBookmark,
  createMaterialFavorite,
  createMaterialFeedback,
  generateMaterialDescription,
  getMaterialBookmarks,
  getMaterialById,
  getMaterialFavorites,
  getMaterialFeedback,
  getMaterialInteractionStats,
  removeMaterialBookmark,
  removeMaterialFavorite,
  updateMaterialFeedback,
} from '../api/materialApi';
import { toasted } from '@/utils/utils';
import BaseIcon from '@/components/base/BaseIcon.vue';
import {
  mdiAccount,
  mdiAlertCircle,
  mdiArrowLeft,
  mdiBarcode,
  mdiBookOpenPageVariant,
  mdiBookmarkOutline,
  mdiBookmark,
  mdiCalendarClock,
  mdiCommentTextOutline,
  mdiFilePdfBox,
  mdiHeartOutline,
  mdiHeart,
  mdiLockClock,
  mdiMapMarkerOutline,
  mdiOpenInNew,
  mdiPackageVariantClosed,
  mdiSchoolOutline,
  mdiStar,
  mdiStarOutline,
  mdiTag,
  mdiTranslate,
} from '@mdi/js';
import defaultCover from '@/assets/default-coverpage.png';

const route = useRoute();
const router = useRouter();
const detailReq = useApiRequest();
const aiReq = useApiRequest();
const statsReq = useApiRequest();
const myFeedbackReq = useApiRequest();
const allFeedbackReq = useApiRequest();
const favoriteReq = useApiRequest();
const bookmarkReq = useApiRequest();
const reviewReq = useApiRequest();

const imageSrc = ref(defaultCover);
const generatedDescription = ref('');
const favoriteRecordId = ref(null);
const bookmarkRecordId = ref(null);
const feedbackRecordId = ref(null);
const hasGeneratedSummary = ref(false);
const reviewForm = reactive({
  rating: 5,
  comment: '',
});

const activeType = computed(() =>
  String(route.query?.type || 'physical').toLowerCase() === 'digital' ? 'digital' : 'physical'
);

const isPhysicalMaterial = computed(() => activeType.value === 'physical');

function extractRow(payload) {
  if (!payload) return null;
  if (Array.isArray(payload)) return payload[0] || null;
  if (Array.isArray(payload?.content)) return payload.content[0] || null;
  if (Array.isArray(payload?.data)) return payload.data[0] || null;
  if (Array.isArray(payload?.results)) return payload.results[0] || null;
  return payload;
}

function rowsFromPayload(payload) {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.content)) return payload.content;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.data)) return payload.data;
  return [];
}

function normalizeNumber(value, fallback = 0) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

const material = computed(() => {
  const row = extractRow(detailReq.response.value);
  if (!row) return null;

  const total = normalizeNumber(row?.total_copies, 0);
  const available = normalizeNumber(row?.available_copies ?? total, 0);

  return {
    ...row,
    total_copies: total,
    available_copies: available,
  };
});

const interactionStats = computed(() => statsReq.response.value || {});
const feedbackRows = computed(() => rowsFromPayload(allFeedbackReq.response.value));

const summaryText = computed(() => {
  const storedDescription = String(material.value?.description || '').trim();
  const generated = String(generatedDescription.value || '').trim();
  return storedDescription || generated || 'No summary available yet.';
});

const materialId = computed(() => route.params.materialId);
const materialIdentity = computed(() => material.value?.id || material.value?.uuid || materialId.value);
const currentUserRole = computed(() => {
  const stored = JSON.parse(localStorage.getItem('userDetail') || '{}');
  const user = stored?.user || stored || {};
  return normalizeRoleValue(user?.roleName || user?.role || user?.userRole);
});
const currentUserIsMember = computed(() => currentUserRole.value === 'MEMBER');
const canBorrow = computed(() => isPhysicalMaterial.value && Number(material.value?.available_copies || 0) > 0 && !currentUserIsMember.value);
const canReserve = computed(() => isPhysicalMaterial.value && Number(material.value?.available_copies || 0) <= 0 && !currentUserIsMember.value);
const canShowDigitalActions = computed(() => !isPhysicalMaterial.value);
const digitalFileUrl = computed(() =>
  toAbsoluteUrl(material.value?.file || material.value?.file_url || material.value?.download_url || '')
);
const hasDigitalFile = computed(() => !isPhysicalMaterial.value && Boolean(digitalFileUrl.value));
const isPdfMaterial = computed(() => {
  if (!hasDigitalFile.value) return false;
  const format = String(material.value?.format || '').toLowerCase();
  if (format === 'pdf') return true;
  return digitalFileUrl.value.toLowerCase().split('?')[0].endsWith('.pdf');
});

const statsCards = computed(() => [
  {
    label: 'Average rating',
    value: Number(interactionStats.value?.average_rating || 0).toFixed(1),
  },
  {
    label: 'Favorites',
    value: normalizeNumber(interactionStats.value?.favorites_count),
  },
  {
    label: 'Bookmarks',
    value: normalizeNumber(interactionStats.value?.bookmarks_count),
  },
  {
    label: 'Comments',
    value: normalizeNumber(interactionStats.value?.comments_count),
  },
]);

watch(
  material,
  (row) => {
    imageSrc.value = row?.cover_image || row?.image || row?.thumbnail || defaultCover;
  },
  { immediate: true }
);

function loadMaterial() {
  if (!materialId.value) return;

  detailReq.send(
    () => getMaterialById(materialId.value, activeType.value),
    (res) => {
      if (!res?.success) {
        toasted(false, 'Failed to load material details');
      }
    },
    true
  );
}

function loadInteractions() {
  if (!materialIdentity.value) return;

  statsReq.send(() => getMaterialInteractionStats(materialIdentity.value, activeType.value));
  myFeedbackReq.send(
    () => getMaterialFeedback({ material_id: materialIdentity.value, material_type: activeType.value, mine: true }),
    (res) => {
      const row = rowsFromPayload(res?.data || res)?.[0] || null;
      feedbackRecordId.value = row?.id || null;
      reviewForm.rating = normalizeNumber(row?.rating, normalizeNumber(statsReq.response.value?.my_rating, 5) || 5);
      reviewForm.comment = row?.comment || statsReq.response.value?.my_comment || '';
    }
  );
  allFeedbackReq.send(() => getMaterialFeedback({ material_id: materialIdentity.value, material_type: activeType.value }));
  favoriteReq.send(
    () => getMaterialFavorites({ material_id: materialIdentity.value, material_type: activeType.value }),
    (res) => {
      favoriteRecordId.value = rowsFromPayload(res?.data || res)?.[0]?.id || null;
    }
  );
  bookmarkReq.send(
    () => getMaterialBookmarks({ material_id: materialIdentity.value, material_type: activeType.value }),
    (res) => {
      bookmarkRecordId.value = rowsFromPayload(res?.data || res)?.[0]?.id || null;
    }
  );
}

watch([materialId, activeType], loadMaterial, { immediate: true });
watch([materialIdentity, activeType], () => {
  generatedDescription.value = '';
  hasGeneratedSummary.value = false;
  if (materialIdentity.value) {
    loadInteractions();
  }
});

watch([materialIdentity, material], ([id, mat]) => {
  if (!id) return;
  if (mat?.description?.trim()) {
    generatedDescription.value = mat.description;
    return;
  }

  if (!hasGeneratedSummary.value && material.value?.title && material.value?.author) {
    hasGeneratedSummary.value = true;
    generateAiDescription();
  }
});

function goBack() {
  router.push('/material');
}

function onImageError() {
  imageSrc.value = defaultCover;
}

function resolveBackendOrigin() {
  const raw = import.meta.env.VITE_API_URL || import.meta.env.v_API_URL || '';
  if (!raw) return window.location.origin;
  try {
    return new URL(raw).origin;
  } catch {
    return window.location.origin;
  }
}

function toAbsoluteUrl(filePath) {
  if (!filePath) return '';
  const value = String(filePath).trim();
  if (!value) return '';
  if (/^https?:\/\//i.test(value)) return value;
  if (value.startsWith('//')) return `${window.location.protocol}${value}`;
  return `${resolveBackendOrigin()}${value.startsWith('/') ? '' : '/'}${value}`;
}

function goToBorrow() {
  if (!canBorrow.value) return;
  router.push({
    path: '/borrows/add',
    query: { materialId: String(materialIdentity.value), type: activeType.value },
  });
}

function goToReserve() {
  if (!canReserve.value) return;
  router.push({
    path: '/reservations',
    query: { materialId: String(materialIdentity.value), type: activeType.value },
  });
}

function goToReadMaterial() {
  if (!isPdfMaterial.value) return;
  router.push({
    path: `/material/${String(materialIdentity.value)}/read`,
    query: { type: 'digital' },
  });
}

function openDigitalFile() {
  if (!digitalFileUrl.value) return;
  window.open(digitalFileUrl.value, '_blank', 'noopener');
}

function generateAiDescription() {
  const title = String(material.value?.title || '').trim();
  const author = String(material.value?.author || '').trim();

  if (!title || !author) {
    toasted(false, 'Title and author are required to generate a description.');
    return;
  }

  aiReq.send(
    () => generateMaterialDescription({ title, author }),
    (res) => {
      if (!res?.success) {
        toasted(false, 'Failed to generate description', res?.error || 'AI generation failed');
        return;
      }

      const description = String(res?.data?.description || '').trim();
      if (!description) {
        toasted(false, 'AI returned an empty description.');
        return;
      }

      generatedDescription.value = description;
      toasted(true, 'Description generated');
    }
  );
}

function toggleFavorite() {
  const request = favoriteRecordId.value
    ? () => removeMaterialFavorite(favoriteRecordId.value)
    : () => createMaterialFavorite({ material_id: materialIdentity.value, material_type: activeType.value });

  favoriteReq.send(request, (res) => {
    if (!res?.success) {
      toasted(false, 'Failed to update favorites', res?.error || 'Unknown error');
      return;
    }

    toasted(true, favoriteRecordId.value ? 'Removed from favorites' : 'Added to favorites');
    loadInteractions();
  });
}

function toggleBookmark() {
  const request = bookmarkRecordId.value
    ? () => removeMaterialBookmark(bookmarkRecordId.value)
    : () => createMaterialBookmark({ material_id: materialIdentity.value, material_type: activeType.value });

  bookmarkReq.send(request, (res) => {
    if (!res?.success) {
      toasted(false, 'Failed to update bookmarks', res?.error || 'Unknown error');
      return;
    }

    toasted(true, bookmarkRecordId.value ? 'Removed from bookmarks' : 'Bookmarked for later');
    loadInteractions();
  });
}

function setRating(value) {
  reviewForm.rating = value;
}

function saveReview() {
  if (!currentUserIsMember.value) {
    toasted(false, 'Please log in as a member to leave a review.');
    return;
  }
  
  if (!materialIdentity.value) return;
  if (!reviewForm.rating) {
    toasted(false, 'Please select a rating first.');
    return;
  }

  const payload = {
    material_id: materialIdentity.value,
    material_type: activeType.value,
    rating: reviewForm.rating,
    comment: reviewForm.comment?.trim() || '',
  };

  const request = feedbackRecordId.value
    ? () => updateMaterialFeedback(feedbackRecordId.value, payload)
    : () => createMaterialFeedback(payload);

  reviewReq.send(request, (res) => {
    if (!res?.success) {
      toasted(false, 'Failed to save review', res?.error || 'Unknown error');
      return;
    }

    toasted(true, feedbackRecordId.value ? 'Review updated successfully' : 'Review submitted successfully');
    loadInteractions();
  });
}
</script>

<style scoped>
/* All styles remain the same as before */
/* Container */
.material-detail-container {
  min-height: 100vh;
  padding: 1rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  transition: background 0.3s ease;
}

.dark .material-detail-container {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

@media (min-width: 768px) {
  .material-detail-container {
    padding: 1.5rem;
  }
}

@media (min-width: 1024px) {
  .material-detail-container {
    padding: 2rem;
  }
}

/* Back Button */
.back-button {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.75rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(203, 213, 225, 0.5);
  color: #475569;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
}

.dark .back-button {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(51, 65, 85, 0.5);
  color: #94a3b8;
}

.back-button:hover {
  transform: translateX(-4px);
  border-color: #f59e0b;
  color: #f59e0b;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  gap: 1rem;
}

.loading-spinner {
  width: 3rem;
  height: 3rem;
  border: 3px solid rgba(245, 158, 11, 0.2);
  border-top-color: #f59e0b;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-state p {
  color: #64748b;
  font-size: 0.875rem;
}

.dark .loading-state p {
  color: #94a3b8;
}

/* Error State */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  text-align: center;
  gap: 1rem;
}

.error-state h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #0f172a;
}

.dark .error-state h3 {
  color: #f1f5f9;
}

.error-state p {
  color: #64748b;
  font-size: 0.875rem;
}

.dark .error-state p {
  color: #94a3b8;
}

/* Hero Section */
.hero-section {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(203, 213, 225, 0.5);
  border-radius: 1.5rem;
  overflow: hidden;
  margin-bottom: 1.5rem;
  transition: all 0.2s ease;
}

.dark .hero-section {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(51, 65, 85, 0.5);
}

.hero-section:hover {
  border-color: rgba(245, 158, 11, 0.3);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.hero-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 768px) {
  .hero-grid {
    grid-template-columns: 280px 1fr;
  }
}

@media (min-width: 1024px) {
  .hero-grid {
    grid-template-columns: 320px 1fr;
  }
}

/* Hero Image */
.hero-image {
  padding: 1.5rem;
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.05), rgba(0, 0, 0, 0.02));
}

.dark .hero-image {
  background: linear-gradient(135deg, rgba(0, 0, 0, 0.2), rgba(0, 0, 0, 0.1));
}

.image-wrapper {
  aspect-ratio: 3/4;
  border-radius: 1rem;
  overflow: hidden;
  background: #f1f5f9;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.dark .image-wrapper {
  background: #1e293b;
}

.image-wrapper img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.image-wrapper:hover img {
  transform: scale(1.05);
}

/* Hero Info */
.hero-info {
  padding: 1.5rem 1.5rem 1.5rem 0;
}

@media (max-width: 768px) {
  .hero-info {
    padding: 0 1.5rem 1.5rem 1.5rem;
  }
}

.badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.badge-type {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  font-size: 0.75rem;
  font-weight: 700;
  color: white;
}

.badge-status {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 700;
}

.status-available {
  background: rgba(16, 185, 129, 0.9);
  color: white;
}

.status-unavailable {
  background: rgba(239, 68, 68, 0.9);
  color: white;
}

.status-digital {
  background: rgba(139, 92, 246, 0.9);
  color: white;
}

.badge-library {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  background: rgba(0, 0, 0, 0.05);
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
}

.dark .badge-library {
  background: rgba(15, 23, 42, 0.5);
  color: #94a3b8;
}

.title {
  font-size: 1.5rem;
  font-weight: 800;
  color: #0f172a;
  margin-bottom: 0.5rem;
}

.dark .title {
  color: #f1f5f9;
}

@media (min-width: 640px) {
  .title {
    font-size: 2rem;
  }
}

@media (min-width: 1024px) {
  .title {
    font-size: 2.5rem;
  }
}

.author {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 1rem;
}

.dark .author {
  color: #94a3b8;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.btn-favorite,
.btn-bookmark {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
  transition: all 0.2s ease;
  cursor: pointer;
  background: rgba(0, 0, 0, 0.05);
  color: #475569;
  border: none;
}

.dark .btn-favorite,
.dark .btn-bookmark {
  background: rgba(15, 23, 42, 0.5);
  color: #94a3b8;
}

.btn-favorite:hover,
.btn-bookmark:hover {
  transform: translateY(-2px);
  background: #f59e0b;
  color: white;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

@media (min-width: 640px) {
  .stats-cards {
    grid-template-columns: repeat(4, 1fr);
  }
}

.stat-card {
  padding: 0.75rem;
  border-radius: 0.75rem;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(203, 213, 225, 0.3);
}

.dark .stat-card {
  background: rgba(15, 23, 42, 0.3);
  border-color: rgba(51, 65, 85, 0.3);
}

.stat-label {
  font-size: 0.625rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #94a3b8;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
}

.dark .stat-value {
  color: #f1f5f9;
}

.primary-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-primary {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  font-weight: 600;
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px -5px rgba(245, 158, 11, 0.4);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  flex: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  font-weight: 600;
  background: rgba(0, 0, 0, 0.05);
  color: #475569;
  border: 1px solid rgba(203, 213, 225, 0.5);
  cursor: pointer;
  transition: all 0.2s ease;
}

.dark .btn-secondary {
  background: rgba(15, 23, 42, 0.5);
  color: #94a3b8;
  border-color: rgba(51, 65, 85, 0.5);
}

.btn-secondary:hover:not(:disabled) {
  background: #f59e0b;
  border-color: #f59e0b;
  color: white;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Details Grid */
.details-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

@media (min-width: 1024px) {
  .details-grid {
    grid-template-columns: 1fr 1fr;
  }
}

/* Detail Cards */
.detail-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(203, 213, 225, 0.5);
  border-radius: 1.5rem;
  overflow: hidden;
  transition: all 0.2s ease;
  margin-bottom: 1.5rem;
}

.dark .detail-card {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(51, 65, 85, 0.5);
}

.detail-card:hover {
  border-color: rgba(245, 158, 11, 0.3);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.card-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid rgba(203, 213, 225, 0.5);
}

.dark .card-header {
  border-bottom: 1px solid rgba(51, 65, 85, 0.5);
}

.card-header h3 {
  font-size: 1rem;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 0.25rem;
}

.dark .card-header h3 {
  color: #f1f5f9;
}

@media (min-width: 640px) {
  .card-header h3 {
    font-size: 1.125rem;
  }
}

.card-header p {
  font-size: 0.75rem;
  color: #64748b;
}

.dark .card-header p {
  color: #94a3b8;
}

/* Summary Content */
.summary-content {
  padding: 1.25rem;
}

.summary-content p {
  font-size: 0.875rem;
  line-height: 1.6;
  color: #475569;
}

.dark .summary-content p {
  color: #cbd5e1;
}

/* Rating Input */
.rating-input {
  padding: 1.25rem;
  display: flex;
  gap: 0.5rem;
  justify-content: center;
  border-bottom: 1px solid rgba(203, 213, 225, 0.5);
}

.star-btn {
  background: none;
  border: none;
  cursor: pointer;
  transition: transform 0.2s ease;
}

.star-btn:hover {
  transform: scale(1.1);
}

.star {
  color: #cbd5e1;
  transition: color 0.2s ease;
}

.star-filled {
  color: #fbbf24;
}

.star-btn:hover .star:not(.star-filled) {
  color: #fde68a;
}

/* Review Textarea */
.review-textarea {
  margin: 1.25rem;
  width: calc(100% - 2.5rem);
  padding: 0.75rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(203, 213, 225, 0.5);
  background: rgba(255, 255, 255, 0.5);
  font-size: 0.875rem;
  color: #0f172a;
  resize: vertical;
}

.dark .review-textarea {
  background: rgba(15, 23, 42, 0.5);
  border-color: rgba(51, 65, 85, 0.5);
  color: #f1f5f9;
}

.review-textarea:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.1);
}

/* Submit Button */
.btn-submit {
  margin: 0 1.25rem 1.25rem 1.25rem;
  width: calc(100% - 2.5rem);
  padding: 0.75rem;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  font-weight: 600;
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px -5px rgba(245, 158, 11, 0.4);
}

.btn-submit:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.button-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  display: inline-block;
  animation: spin 0.8s linear infinite;
}

/* Specifications Grid */
.specs-grid {
  padding: 1.25rem;
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 640px) {
  .specs-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.spec-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.75rem;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(203, 213, 225, 0.3);
  color: #64748b;
}

.dark .spec-item {
  background: rgba(15, 23, 42, 0.3);
  border-color: rgba(51, 65, 85, 0.3);
  color: #94a3b8;
}

.spec-label {
  font-size: 0.625rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #94a3b8;
}

.spec-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #0f172a;
}

.dark .spec-value {
  color: #f1f5f9;
}

/* Comments List */
.comments-list {
  padding: 1.25rem;
  max-height: 400px;
  overflow-y: auto;
}

.comments-list::-webkit-scrollbar {
  width: 6px;
}

.comments-list::-webkit-scrollbar-track {
  background: rgba(203, 213, 225, 0.3);
  border-radius: 3px;
}

.comments-list::-webkit-scrollbar-thumb {
  background: rgba(245, 158, 11, 0.5);
  border-radius: 3px;
}

.comment-item {
  padding: 1rem;
  border-radius: 0.75rem;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(203, 213, 225, 0.3);
  margin-bottom: 0.75rem;
}

.dark .comment-item {
  background: rgba(15, 23, 42, 0.3);
  border-color: rgba(51, 65, 85, 0.3);
}

.comment-item:last-child {
  margin-bottom: 0;
}

.comment-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
}

.comment-author {
  font-size: 0.875rem;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 0.25rem;
}

.dark .comment-author {
  color: #f1f5f9;
}

.comment-rating {
  display: flex;
  gap: 0.125rem;
}

.star-icon {
  color: #cbd5e1;
}

.star-icon-filled {
  color: #fbbf24;
}

.comment-date {
  font-size: 0.6875rem;
  color: #94a3b8;
}

.comment-text {
  font-size: 0.8125rem;
  line-height: 1.5;
  color: #475569;
}

.dark .comment-text {
  color: #cbd5e1;
}

.empty-comments {
  text-align: center;
  padding: 2rem;
  color: #94a3b8;
}

.empty-comments p {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.empty-comments span {
  font-size: 0.75rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>