<template>  
    <div class="w-1/2"> <!-- Set the width to half -->  
      <div class="flex  justify-between"> <!-- Flex to align text and chart -->  
        <div class=" w-1/2"> <!-- Content container -->  
          <div class="flex items-center text-sm text-[#A3AED0] bg-[#F4F7FE] mb-4">  
        <i v-html="icons.calander" class="pl-2" />  
        <h2 class="text-md pl-2 font-normal">This month</h2>  
      </div>   
          <div class="flex items-baseline justify-between">  
            <h1 class="font-['DM_Sans'] font-bold text-[#2B3674] text-[23.97px] leading-[29.61px] tracking-[-0.02em]">
  $37.5K
</h1></div> 
<div class="text-[#05CD99] flex gap-4"> 
    <p class="font-['DM_Sans'] font-medium text-[9.87px] leading-[16.92px] tracking-[-0.02em] text-[#A3AED0]">
  Total Spent
</p>
 
<span class="font-['DM_Sans'] font-bold text-[8.46px] leading-[14.1px] tracking-[-0.02em] text-center">
  ▲ +2.45%
</span>
 
          </div>  
         
          <p class="text-[#05CD99]">✅ On track</p>  
        </div>  
        <div class="chart-container w-1/2 flex flex-col items-end"> <!-- Chart container --> 
  <button class="border rounded px-2 py-1 text-gray-600 mb-2">📅</button>   
  <canvas ref="lineChart" class="h-32"></canvas> <!-- Reduced height of the chart -->  
</div>
      </div>  
    </div>  
  </template>  
  
  <script setup>  
  import { ref, onMounted } from 'vue';  
  import { Chart, registerables } from 'chart.js';  
import icons from '@/utils/icons';
  
  // Register all necessary components  
  Chart.register(...registerables);  
  
  const lineChart = ref(null);  
  
  const renderChart = () => {  
    const ctx = lineChart.value.getContext('2d');  
    new Chart(ctx, {  
      type: 'line',  
      data: {  
        labels: ['SEP', 'OCT', 'NOV', 'DEC', 'JAN', 'FEB'],  
        datasets: [  
          {  
            label: 'Total Spent',  
            data: [5000, 15000, 10000, 15000, 10000, 5000],  
            fill: false,  
            borderColor: 'rgba(106, 210, 255, 1)',  
            tension: 0.4,  
            borderWidth: 2,  
            pointRadius: 0, // No dots on the line  
          },  
          {  
            label: 'Projected',  
            data: [25000, 30000, 25000, 30000, 25000, 30000],  
            fill: false,  
            borderColor: 'rgba(67, 24, 255, 1)',  
            tension: 0.4,  
            borderWidth: 2,  
            pointRadius: 0, // No dots on the line  
          },  
        ],  
      },  
      options: {  
        responsive: true,  
        plugins: {  
          legend: {  
            display: false,  
          },  
        },  
        scales: {  
          x: {  
            grid: {  
              display: false, // Hide x-axis line  
            },  
            ticks: {  
              display: true, // Display x-axis labels  
            },  
          },  
          y: {  
            display: false, // Hide y-axis  
            ticks: {  
              display: false, // Hide y-axis numbers  
            },  
            grid: {  
              display: false, // Hide horizontal lines  
            },  
          },  
        },  
      },  
    });  
  };  
  
  // Use onMounted to render the chart when the component is mounted  
  onMounted(renderChart);  
  </script>  
  
  <style scoped>  
  .chart-container {  
    width: 100%; /* Ensure the chart container takes full width */  
  }  
  </style>