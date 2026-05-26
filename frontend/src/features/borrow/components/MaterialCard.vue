<script setup>
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiBook, mdiAccount, mdiStar, mdiCheckCircle } from '@mdi/js';
import { computed } from 'vue';

const props = defineProps({
  material: Object,
  isSelected: Boolean,
  selectUnavailableOnly: {
    type: Boolean,
    default: false,
  },
  viewMode: {
    type: String,
    default: 'grid',
  },
});

const emit = defineEmits(['select']);

const availabilityStatus = computed(() => {
  if (props.material.available_copies === 0) return 'unavailable';
  if (props.material.available_copies < 3) return 'limited';
  return 'available';
});

const statusClasses = {
  available: 'status-available',
  limited: 'status-limited',
  unavailable: 'status-unavailable',
};

const statusText = {
  available: 'Available',
  limited: 'Low stock',
  unavailable: 'Out of stock',
};

const isSelectable = computed(() => {
  const availableCopies = Number(props.material?.available_copies || 0);
  return props.selectUnavailableOnly ? availableCopies <= 0 : availableCopies > 0;
});

const availabilityPercentage = computed(() => {
  const total = Number(props.material?.total_copies || 1);
  const available = Number(props.material?.available_copies || 0);
  return Math.min(100, Math.max(0, (available / total) * 100));
});
</script>

<template>
  <div
    class="material-card"
    :class="[
      isSelected ? 'is-selected' : '',
      !isSelectable ? 'is-disabled' : '',
      viewMode === 'list' ? 'layout-list' : '',
    ]"
    @click="isSelectable && emit('select', material)"
  >
    <div class="card-visual">
      <div class="icon-wrap">
        <BaseIcon :path="mdiBook" size="28" class="text-amber-500" />
      </div>
      <span v-if="isSelected" class="selected-badge">
        <BaseIcon :path="mdiCheckCircle" size="14" />
      </span>
      <span v-if="availabilityStatus === 'limited'" class="low-stock-pill">Low stock</span>
    </div>

    <div class="card-body">
      <p class="card-category">{{ material.category || 'General' }}</p>
      <h5 class="card-title">{{ material.title || 'Untitled' }}</h5>

      <div class="card-author-row">
        <p class="card-author">
          <BaseIcon :path="mdiAccount" size="12" />
          {{ material.author || 'Unknown author' }}
        </p>
        <div v-if="material.average_rating || material.rating" class="card-rating">
          <BaseIcon :path="mdiStar" size="12" />
          {{ Number(material.average_rating || material.rating || 0).toFixed(1) }}
        </div>
      </div>

      <div v-if="viewMode === 'list'" class="list-meta">
        <span>ISBN: {{ material.isbn || 'N/A' }}</span>
      </div>

      <div class="card-footer">
        <span class="status-pill" :class="statusClasses[availabilityStatus]">
          {{ statusText[availabilityStatus] }}
        </span>
        <span class="copies-label">
          {{ material.available_copies || 0 }}/{{ material.total_copies || 0 }} copies
        </span>
      </div>

      <div v-if="viewMode === 'grid'" class="progress-track">
        <div
          class="progress-fill"
          :class="availabilityPercentage > 50 ? 'fill-green' : availabilityPercentage > 0 ? 'fill-amber' : 'fill-red'"
          :style="{ width: `${availabilityPercentage}%` }"
        />
      </div>

      <p v-if="!isSelected && isSelectable" class="select-hint">Click to select</p>
    </div>
  </div>
</template>

<style scoped>
.material-card {
  display: flex;
  flex-direction: column;
  border-radius: 1rem;
  border: 2px solid #e2e8f0;
  background: #fff;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
  box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
}

.material-card:hover:not(.is-disabled) {
  transform: translateY(-2px);
  border-color: #fbbf24;
  box-shadow: 0 14px 28px rgba(245, 158, 11, 0.15);
}

.material-card.is-selected {
  border-color: #f59e0b;
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.2);
}

.material-card.is-disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.material-card.layout-list {
  flex-direction: row;
}

.dark .material-card {
  background: #1e293b;
  border-color: #334155;
}

.card-visual {
  position: relative;
  min-height: 7rem;
  background: linear-gradient(145deg, #fff7ed 0%, #ffedd5 45%, #fef3c7 100%);
  display: grid;
  place-items: center;
  border-bottom: 1px solid #fde68a;
}

.layout-list .card-visual {
  width: 7rem;
  min-height: auto;
  border-bottom: none;
  border-right: 1px solid #fde68a;
}

.dark .card-visual {
  background: linear-gradient(145deg, #1e293b, #334155);
  border-color: #475569;
}

.icon-wrap {
  width: 3.25rem;
  height: 3.25rem;
  border-radius: 0.85rem;
  background: #fff;
  display: grid;
  place-items: center;
  box-shadow: 0 6px 14px rgba(245, 158, 11, 0.2);
}

.selected-badge {
  position: absolute;
  top: 0.6rem;
  right: 0.6rem;
  width: 1.6rem;
  height: 1.6rem;
  border-radius: 0.5rem;
  display: grid;
  place-items: center;
  background: linear-gradient(135deg, #f59e0b, #ea580c);
  color: white;
}

.low-stock-pill {
  position: absolute;
  bottom: 0.55rem;
  left: 0.55rem;
  padding: 0.2rem 0.5rem;
  border-radius: 999px;
  background: #f59e0b;
  color: white;
  font-size: 0.65rem;
  font-weight: 700;
}

.card-body {
  padding: 0.85rem 0.95rem 1rem;
  display: grid;
  gap: 0.45rem;
  flex: 1;
}

.card-category {
  margin: 0;
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #b45309;
}

.card-title {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.dark .card-title {
  color: #f8fafc;
}

.card-author-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.card-author {
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: #64748b;
}

.card-rating {
  display: flex;
  align-items: center;
  gap: 0.2rem;
  font-size: 0.72rem;
  font-weight: 700;
  color: #f59e0b;
}

.list-meta {
  font-size: 0.72rem;
  color: #94a3b8;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
}

.status-pill {
  padding: 0.2rem 0.55rem;
  border-radius: 999px;
  font-size: 0.65rem;
  font-weight: 700;
}

.status-available {
  background: #dcfce7;
  color: #15803d;
}

.status-limited {
  background: #fef3c7;
  color: #b45309;
}

.status-unavailable {
  background: #fee2e2;
  color: #b91c1c;
}

.copies-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: #475569;
}

.progress-track {
  height: 0.28rem;
  border-radius: 999px;
  background: #e2e8f0;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.3s ease;
}

.fill-green {
  background: #22c55e;
}

.fill-amber {
  background: #f59e0b;
}

.fill-red {
  background: #ef4444;
}

.select-hint {
  margin: 0.15rem 0 0;
  font-size: 0.68rem;
  font-weight: 600;
  color: #d97706;
}
</style>
