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
  libraries: { type: Array, default: () => [] },
  members: { type: Array, default: () => [] },
  borrows: { type: Array, default: () => [] },
});

const chartData = computed(() => {
  const labels = props.libraries.map((lib) => lib?.name || lib?.library_name || 'Branch');
  const memberCounts = props.libraries.map((lib) =>
    props.members.filter(
      (user) => String(user?.library_id || user?.library) === String(lib?.id)
    ).length
  );
  const activeBorrows = props.libraries.map((lib) =>
    props.borrows.filter(
      (row) =>
        !row?.is_returned &&
        String(row?.library_id || row?.material_library_id || '') === String(lib?.id)
    ).length
  );

  return {
    labels,
    datasets: [
      {
        label: 'Members',
        data: memberCounts,
        backgroundColor: '#3b82f6',
        borderRadius: 6,
      },
      {
        label: 'Active borrows',
        data: activeBorrows,
        backgroundColor: '#f59e0b',
        borderRadius: 6,
      },
    ],
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'top' },
  },
  scales: {
    y: { beginAtZero: true, ticks: { precision: 0 } },
    x: { grid: { display: false } },
  },
};
</script>

<template>
  <div class="library-chart">
    <Bar :data="chartData" :options="chartOptions" />
  </div>
</template>

<style scoped>
.library-chart {
  width: 100%;
  height: 320px;
}
</style>
