<script setup lang="ts">
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'
import { Doughnut } from 'vue-chartjs'

ChartJS.register(ArcElement, Tooltip, Legend)

const chartdata = {
    datasets: [{
        label: 'My First Dataset',
        data: [63, 21, 16],
        backgroundColor: [
            '#4318FF',
            '#6AD2FF',
            '#EFF4FB'
        ],
        hoverOffset: 4
    }]
};

const options = {
    cutout: 0 // Removes the white circle in the center
};
</script>

<template>
     <div class="w-1/4 ">  
        <div class="flex justify-between">
      <h2 class="text-xl font-normal mb-7">Your Pie Chart</h2>  
        <p class="text-gray-500">Monthly</p>  
      </div>  
    <div class="h-[150px] items-center mx-12">
        <Doughnut :data="chartdata" :options="options" />
    </div>
    <div class="mt-4">  
        <div class="flex justify-between">  
          <div>  
            <span class="text-[#4318FF]">●</span> Your files 63%  
          </div>  
          <div>  
            <span class="text-[#6AD2FF]">●</span> System 25%  
          </div>  
        </div>  
      </div>  
    </div>  
</template>
