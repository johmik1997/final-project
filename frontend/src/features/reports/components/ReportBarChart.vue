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
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  datasets: { type: Array, default: () => [] },
  label: { type: String, default: 'Count' },
  color: { type: String, default: '#f59e0b' },
});

const normalizedDatasets = computed(() => {
  if (props.datasets?.length) {
    return props.datasets.map((dataset) => ({
      borderRadius: 8,
      maxBarThickness: 48,
      ...dataset,
    }));
  }

  return [
    {
      label: props.label,
      data: props.values,
      backgroundColor: props.color,
      borderRadius: 8,
      maxBarThickness: 48,
    },
  ];
});

const chartData = computed(() => ({
  labels: props.labels,
  datasets: normalizedDatasets.value,
}));

const chartOptions = computed(() => ({
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: normalizedDatasets.value.length > 1 },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: { precision: 0 },
    },
    x: {
      grid: { display: false },
    },
  },
}));
</script>

<template>
  <div class="report-chart">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.report-chart {
  width: 100%;
  height: 280px;
}
</style>
