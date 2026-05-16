<script setup>
import { computed } from 'vue';
import { Doughnut } from 'vue-chartjs';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);

const props = defineProps({
  available: {
    type: Number,
    default: 0,
  },
  unavailable: {
    type: Number,
    default: 0,
  },
  physical: {
    type: Number,
    default: 0,
  },
  digital: {
    type: Number,
    default: 0,
  },
});

const chartData = computed(() => ({
  labels: ['Available', 'Unavailable', 'Physical', 'Digital'],
  datasets: [
    {
      data: [props.available, props.unavailable, props.physical, props.digital],
      backgroundColor: ['#22C55E', '#F59E0B', '#3B82F6', '#8B5CF6'],
      borderWidth: 1,
      borderColor: '#FFFFFF',
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
  <div class="h-[320px]">
    <Doughnut :data="chartData" :options="chartOptions" />
  </div>
</template>
