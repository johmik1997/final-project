<script setup>
import { computed } from 'vue';
import { Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const props = defineProps({
  labels: { type: Array, default: () => [] },
  values: { type: Array, default: () => [] },
  colors: {
    type: Array,
    default: () => ['#3b82f6', '#f59e0b', '#10b981', '#ef4444', '#8b5cf6'],
  },
});

const chartData = computed(() => ({
  labels: props.labels,
  datasets: [
    {
      data: props.values,
      backgroundColor: props.colors.slice(0, props.values.length),
      borderWidth: 2,
      borderColor: '#ffffff',
    },
  ],
}));

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
    },
  },
};
</script>

<template>
  <div class="report-chart">
    <Doughnut :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.report-chart {
  width: 100%;
  height: 280px;
}
</style>
