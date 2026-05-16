<template>  
    <div class="">  
      <div class="flex justify-between items-center mb-4">  
        <h2 class="text-xl font-semibold">Weekly Revenue</h2>  
        <button class="bg-gray-200 rounded-full p-2">  
          <span class="text-gray-600">📈</span>  
        </button>  
      </div>  
      <div class="flex items-end space-x-10"> <!-- Space between bars -->  
        <div v-for="(data, index) in revenueData" :key="index" class="flex flex-col items-center">  
          <div class="flex flex-col justify-end bg-red">  
            <div  
              class="bg-[#EFF4FB] rounded-t-lg"  
              :style="{ height: `${Math.min(data[0] * 4, 70)}px` }" 
            ></div>  
            <div  
              class="bg-[#6AD2FF]"  
              :style="{ height: `${Math.min(data[1] * 4, 70)}px` }"
            ></div>  
            <div  
              class=" bg-[#4318FF] rounded-b-lg"  
              :style="{ height: `${Math.min(data[2] * 4, 70)}px` }"  
            ></div>  
          </div>  
          <span class="text-gray-500">{{ index + 17 }}</span> <!-- Display the day (17 to 25) -->  
        </div>  
      </div>  
    </div>  
  </template>  
  
  <script setup>  
  import { ref } from 'vue';  
  
  // Sample revenue data with three values for each bar  
  const revenueData = ref([  
    [5, 3, 8],  
    [3, 5, 8],  
    [2, 4, 6],  
    [8, 7, 15],  
    [6, 4, 10],  
    [8, 10, 18],  
    [5, 5, 10],  
    [5, 7, 12],  
    [13, 6, 7]  
  ]);  
  </script>  
  
  <style scoped>  
  .flex-col {  
    min-width: 10px; /* Decrease bar width */  
  }  
  </style>