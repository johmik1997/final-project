<template>
  <div class="dashboard-panel">
    <header class="panel-header">
      <div class="panel-header-content">
        <h2 class="panel-title">{{ title }}</h2>
        <p v-if="subtitle" class="panel-subtitle">{{ subtitle }}</p>
      </div>
    </header>
    <div class="panel-body">
      <slot />
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: '',
  },
  subtitle: {
    type: String,
    default: '',
  },
});
</script>

<style scoped>
.dashboard-panel {
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(203, 213, 225, 0.5);
  overflow: hidden;
  transition: all 0.2s ease;
}

.dark .dashboard-panel {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(51, 65, 85, 0.5);
}

.dashboard-panel:hover {
  border-color: rgba(245, 158, 11, 0.3);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.dark .dashboard-panel:hover {
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
  border-color: rgba(245, 158, 11, 0.2);
}

.panel-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid rgba(203, 213, 225, 0.5);
}

.dark .panel-header {
  border-bottom: 1px solid rgba(51, 65, 85, 0.5);
}

.panel-header-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.panel-title {
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: #0f172a;
}

.dark .panel-title {
  color: #f1f5f9;
}

@media (min-width: 640px) {
  .panel-title {
    font-size: 1.125rem;
  }
}

.panel-subtitle {
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.25rem;
}

.dark .panel-subtitle {
  color: #94a3b8;
}

.panel-body {
  padding: 1.25rem;
}

@media (min-width: 640px) {
  .panel-body {
    padding: 1.5rem;
  }
}
</style>