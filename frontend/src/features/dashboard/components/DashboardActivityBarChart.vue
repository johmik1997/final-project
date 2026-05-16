<script setup>
import { computed } from 'vue';
import { Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  Title,
  Tooltip,
  Legend,
  BarElement,
  CategoryScale,
  LinearScale,
} from 'chart.js';

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

const props = defineProps({
  labels: {
    type: Array,
    default: () => [],
  },
  borrowSeries: {
    type: Array,
    default: () => [],
  },
  reservationSeries: {
    type: Array,
    default: () => [],
  },
});

// Detect dark mode
const isDark = computed(() => {
  if (typeof window !== 'undefined') {
    return document.documentElement.classList.contains('dark');
  }
  return false;
});

const chartData = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      label: 'Borrows',
      data: props.borrowSeries,
      backgroundColor: '#3b82f6',
      borderRadius: 8,
      barPercentage: 0.7,
      categoryPercentage: 0.8,
    },
    {
      label: 'Reservations',
      data: props.reservationSeries,
      backgroundColor: '#10b981',
      borderRadius: 8,
      barPercentage: 0.7,
      categoryPercentage: 0.8,
    },
  ],
}));

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top',
      align: 'center',
      labels: {
        usePointStyle: true,
        pointStyle: 'circle',
        padding: 15,
        font: {
          size: 12,
          weight: '600',
        },
        color: isDark.value ? '#94a3b8' : '#64748b',
      },
    },
    tooltip: {
      backgroundColor: isDark.value ? '#1e293b' : '#ffffff',
      titleColor: isDark.value ? '#f1f5f9' : '#0f172a',
      bodyColor: isDark.value ? '#94a3b8' : '#64748b',
      borderColor: isDark.value ? '#334155' : '#e2e8f0',
      borderWidth: 1,
      padding: 10,
      cornerRadius: 8,
      displayColors: true,
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      grid: {
        color: isDark.value ? '#334155' : '#e2e8f0',
        drawBorder: false,
        lineWidth: 1,
      },
      ticks: {
        precision: 0,
        stepSize: 1,
        font: {
          size: 11,
        },
        color: isDark.value ? '#94a3b8' : '#64748b',
      },
      title: {
        display: false,
      },
    },
    x: {
      grid: {
        display: false,
      },
      ticks: {
        font: {
          size: 11,
          weight: '500',
        },
        color: isDark.value ? '#94a3b8' : '#64748b',
      },
    },
  },
  layout: {
    padding: {
      top: 10,
      right: 10,
      bottom: 10,
      left: 10,
    },
  },
  datasets: {
    bar: {
      barPercentage: 0.7,
      categoryPercentage: 0.8,
    },
  },
}));
</script>

<template>
  <div class="chart-container">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.chart-container {
  width: 100%;
  height: 320px;
  position: relative;
}

@media (min-width: 640px) {
  .chart-container {
    height: 340px;
  }
}

@media (min-width: 1024px) {
  .chart-container {
    height: 360px;
  }
}

/* Smooth transitions for theme changes */
:deep(canvas) {
  transition: all 0.3s ease;
}

/* Custom tooltip styling enhancements */
:deep(.chartjs-tooltip) {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(4px);
  border-radius: 0.75rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.dark :deep(.chartjs-tooltip) {
  background: rgba(30, 41, 59, 0.95);
  backdrop-filter: blur(4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}
</style>