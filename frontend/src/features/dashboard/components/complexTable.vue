<template>  
    <div class="w-1/2 bg-white pl-5">  
      <h2 class="text-lg font-semibold mb-2">Complex Table</h2>  
      <table class="min-w-full table-auto text-xs">  
        <thead>  
          <tr class="text-[#A3AED0]">  
            <th class="px-4 py-2 text-left">NAME</th>  
            <th class="px-4 py-2 text-left">STATUS</th>  
            <th class="px-4 py-2 text-left">DATE</th>  
            <th class="px-4 py-2 text-left">PROGRESS</th>  
          </tr>  
        </thead>  
        <tbody>  
          <tr v-for="(item, index) in items" :key="index" class="hover:bg-gray-100">  
            <td class="px-4 py-2">  
              <span>{{ item.name }}</span>  
            </td>  
            <td class="px-4 py-2 flex items-center">  
              <i v-html="icons[item.statusIcon]" class="mr-2 w-6 h-6 inline"></i>  
              <span :class="statusClasses[item.status]">{{ item.status }}</span>  
            </td>  
            <td class="px-4 py-2">{{ item.date }}</td>  
            <td class="px-4 py-2">  
              <div class="w-full bg-gray-200 rounded h-2">  
                <div  
                  class="bg-indigo-600 h-2 rounded"  
                  :style="{ width: item.progress }"  
                ></div>  
              </div>  
            </td>  
          </tr>  
        </tbody>  
      </table>  
    </div>  
  </template>  
  
  <script setup>  
  import { ref } from 'vue';  
  import icons from '@/utils/icons'; // Adjust the path based on your directory structure  
  
  const items = ref([  
    {  
      name: 'Horizon UI PRO',  
      status: 'Approved',  
      statusIcon: 'Approved',  
      date: '18 Apr 2021',  
      progress: '75%',  
    },  
    {  
      name: 'Horizon UI Free',  
      status: 'Disable',  
      statusIcon: 'Disable',  
      date: '18 Apr 2021',  
      progress: '40%',  
    },  
    {  
      name: 'Marketplace',  
      status: 'Error',  
      statusIcon: 'Error',  
      date: '20 May 2021',  
      progress: '50%',  
    },  
    {  
      name: 'Weekly Updates',  
      status: 'Approved',  
      statusIcon: 'Approved',  
      date: '12 Jul 2021',  
      progress: '80%',  
    },  
  ]);  
  
  const statusClasses = {  
    Approved: 'text-green-600',  
    Disable: 'text-red-600',  
    Error: 'text-yellow-600',  
  };  
  </script>  
  
  <style scoped>  
  table {  
    border-collapse: collapse;  
  }  
  td, th {  
    border: none;  
  }  
  </style>