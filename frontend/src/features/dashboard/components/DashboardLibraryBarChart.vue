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

function normalizeText(value) {
  return String(value || '').trim().toLowerCase();
}

function matchesLibrary(row, library) {
  const targetId = String(library?.id || '');
  const targetName = normalizeText(library?.name || library?.library_name);

  const idCandidates = [
    row?.library_id,
    row?.library,
    row?.libraryId,
    row?.material_library_id,
    row?.material?.library_id,
    row?.material?.library,
  ]
    .filter((value) => value !== null && value !== undefined && value !== '')
    .map((value) => String(value));

  if (targetId && idCandidates.includes(targetId)) {
    return true;
  }

  const nameCandidates = [
    row?.library_name,
    row?.libraryName,
    row?.material_library_name,
    row?.material?.library_name,
    row?.material?.libraryName,
  ]
    .map((value) => normalizeText(value))
    .filter(Boolean);

  return Boolean(targetName) && nameCandidates.includes(targetName);
}

function normalizeStatus(value) {
  return String(value || '').trim().toUpperCase();
}

const chartData = computed(() => {
  const labels = props.libraries.map((lib) => lib?.name || lib?.library_name || 'Branch');
  const memberCounts = props.libraries.map((lib) => {
    const explicitMembers = props.members.filter((user) => matchesLibrary(user, lib));
    if (explicitMembers.length) {
      return explicitMembers.length;
    }

    // Fallback for older records where members were not assigned a branch directly.
    return new Set(
      props.borrows
        .filter((row) => matchesLibrary(row, lib))
        .map((row) => row?.member)
        .filter(Boolean)
        .map((value) => String(value))
    ).size;
  });
  const activeBorrows = props.libraries.map((lib) =>
    props.borrows.filter(
      (row) =>
        !row?.is_returned &&
        ['BORROWED', 'OVERDUE'].includes(normalizeStatus(row?.status)) &&
        matchesLibrary(row, lib)
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
