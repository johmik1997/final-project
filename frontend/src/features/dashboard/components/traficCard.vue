<template>  
   <div class="w-1/4 mx-6">  
    <div class="justify-between flex">
      <h2 class="text-gray-500">Daily Traffic</h2>  
      <span class="text-green-500 ml-2">+2.45%</span> 
    </div>
      <div class="flex items-baseline">  
        <h1 class="text-3xl font-bold text-gray-900">2.579</h1>  
        <p class="text-gray-400">Visitors</p>
         
      </div>  
       
      <div class="flex items-end pt-8 space-x-6"> <!-- Space between bars -->  
        <div v-for="(data, index) in revenueData" :key="index" class="flex flex-col items-center">  
          <div class="flex flex-col justify-end bg-red">  
            <div  
  class="rounded-t-lg pt-8 transition-all duration-300"
  :style="{ 
    height: `${Math.min(data[0] * 20, 100)}px`, 
    backgroundColor: `hsl(250, 100%, ${100 - Math.min(data[0] * 4, 60)}%)` 
  }"
></div>
 
           
             
          </div>  
          <span class="text-gray-500">{{ (index * 4).toString().padStart(2, '0') }}</span>
        </div>  
      </div>  
    </div>  
  </template>  
  
  <script setup>  
  import { ref } from 'vue';  
  
  // Sample revenue data with three values for each bar  
  const revenueData = ref([  
    [5],  
    [3],  
    [6],  
    [4],  
    [5.5],  
    [7],  
    [1] 
  ]);  
  </script>  
  
  <style scoped>  
  .flex-col {  
    min-width: 10px; /* Decrease bar width */  
  }  
  </style>