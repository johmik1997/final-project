<template>
  <div class="stat-card" :class="`tone-${tone}`">
    <div class="stat-card-content">
      <div class="stat-info">
        <p class="stat-label">{{ label }}</p>
        <p class="stat-value">{{ value }}</p>
        <p v-if="description" class="stat-description">{{ description }}</p>
      </div>
      <div class="stat-icon-wrapper" :class="`icon-tone-${tone}`">
        <BaseIcon :path="icon" size="24" />
      </div>
    </div>
  </div>
</template>

<script setup>
import BaseIcon from '@/components/base/BaseIcon.vue';

defineProps({
  label: {
    type: String,
    default: '',
  },
  value: {
    type: [String, Number],
    default: 0,
  },
  description: {
    type: String,
    default: '',
  },
  icon: {
    type: String,
    default: '',
  },
  tone: {
    type: String,
    default: 'blue',
  },
});
</script>

<style scoped>
.stat-card {
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(203, 213, 225, 0.5);
  padding: 1.25rem;
  transition: all 0.2s ease;
}

.dark .stat-card {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(51, 65, 85, 0.5);
}

.stat-card:hover {
  transform: translateY(-2px);
  border-color: rgba(245, 158, 11, 0.3);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.dark .stat-card:hover {
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
  border-color: rgba(245, 158, 11, 0.2);
}

.stat-card-content {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #64748b;
}

.dark .stat-label {
  color: #94a3b8;
}

.stat-value {
  margin-top: 0.5rem;
  font-size: 1.875rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
}

.dark .stat-value {
  color: #f1f5f9;
}

@media (min-width: 640px) {
  .stat-value {
    font-size: 2.25rem;
  }
}

.stat-description {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #94a3b8;
  line-height: 1.25rem;
}

.dark .stat-description {
  color: #64748b;
}

.stat-icon-wrapper {
  display: flex;
  height: 3rem;
  width: 3rem;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 1rem;
  background: rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(203, 213, 225, 0.5);
  transition: all 0.2s ease;
}

.dark .stat-icon-wrapper {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(51, 65, 85, 0.5);
}

.stat-card:hover .stat-icon-wrapper {
  transform: scale(1.05);
}

/* Tone variations */
.stat-card.tone-blue .stat-icon-wrapper {
  color: #3b82f6;
  border-color: rgba(59, 130, 246, 0.2);
}

.stat-card.tone-blue:hover {
  border-color: rgba(59, 130, 246, 0.4);
}

.stat-card.tone-green .stat-icon-wrapper {
  color: #10b981;
  border-color: rgba(16, 185, 129, 0.2);
}

.stat-card.tone-green:hover {
  border-color: rgba(16, 185, 129, 0.4);
}

.stat-card.tone-amber .stat-icon-wrapper {
  color: #f59e0b;
  border-color: rgba(245, 158, 11, 0.2);
}

.stat-card.tone-amber:hover {
  border-color: rgba(245, 158, 11, 0.4);
}

.stat-card.tone-violet .stat-icon-wrapper {
  color: #8b5cf6;
  border-color: rgba(139, 92, 246, 0.2);
}

.stat-card.tone-violet:hover {
  border-color: rgba(139, 92, 246, 0.4);
}

/* Icon tone classes for the icon wrapper itself */
.icon-tone-blue {
  color: #3b82f6;
}

.icon-tone-green {
  color: #10b981;
}

.icon-tone-amber {
  color: #f59e0b;
}

.icon-tone-violet {
  color: #8b5cf6;
}
</style>