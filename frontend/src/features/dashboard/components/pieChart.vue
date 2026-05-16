<template>  
    <div class="p-6 bg-white rounded-lg shadow-md w-1/4">  
      <h2 class="text-2xl font-semibold mb-4">Your Pie Chart</h2>  
      <div class="flex justify-between">  
        <p class="text-gray-500">Monthly</p>  
      </div>  
      <PieChart :chart-data="chartData" :chart-options="chartOptions" />  
      <div class="mt-4">  
        <div class="flex justify-between">  
          <div>  
            <span class="text-purple-500">●</span> Your files 63%  
          </div>  
          <div>  
            <span class="text-blue-300">●</span> System 25%  
          </div>  
        </div>  
      </div>  
    </div>  
  </template>  
  
  <script setup>  
  import { ref } from 'vue';  
  import { Pie } from 'vue-chartjs';  
  import {  
    Chart as ChartJS,  
    Title,  
    Tooltip,  
    Legend,  
    ArcElement,  
  } from 'chart.js';  
  
  ChartJS.register(Title, Tooltip, Legend, ArcElement);  
  
  const chartData = ref({  
    labels: ['Your files', 'System', 'Others'],  
    datasets: [  
      {  
        data: [63, 25, 12], // Adjust these values as needed  
        backgroundColor: ['#6D28D9', '#3B82F6', '#D1D5DB'], // Colors for each segment  
      },  
    ],  
  });  
  
  const chartOptions = ref({  
    responsive: true,  
    plugins: {  
      legend: {  
        position: 'top',  
      },  
    },  
  });  
  </script>  
  
  <style scoped>  
  </style>