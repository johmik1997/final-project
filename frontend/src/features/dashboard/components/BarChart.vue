<script setup>
import { ref, computed } from "vue";
import { Chart as ChartJS, BarElement, BarController, CategoryScale, LinearScale, Tooltip, Legend } from "chart.js";
import { Bar } from "vue-chartjs"; // Correct package: vue-chartjs, NOT vue-chart-3

// ✅ Register required Chart.js components
ChartJS.register(BarElement, BarController, CategoryScale, LinearScale, Tooltip, Legend);

const selectedYear = ref(2024);
const years = [2024, 2023, 2022];

const chartData = computed(() => ({
    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug"],
    datasets: [
        {
            label: `Transactions (${selectedYear.value})`,
            data: [10, 30, 50, 40, 60, 80, 90, 100],
            backgroundColor: "#004E89",
        },
        {
            label: `Previous Year (${selectedYear.value - 1})`,
            data: [15, 25, 45, 35, 55, 75, 85, 95],
            backgroundColor: "#D1D5DB",
        },
    ],
}));

const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
};
</script>

<template>
    <div class="bg-white p-4 rounded-lg shadow-md">
        <div class="flex justify-between items-center mb-4">
            <div>
                <p class="text-gray-500 text-sm">Total Transactions</p>
                <p class="text-2xl font-semibold">ETB 92,900.09</p>
            </div>
            <select v-model="selectedYear" class="border rounded-md px-3 py-1 text-sm text-gray-600">
                <option v-for="year in years" :key="year">{{ year }}</option>
            </select>
        </div>
        <div class="h-[300px]">
            <Bar :data="chartData" :options="chartOptions" />
        </div>
    </div>
</template>
