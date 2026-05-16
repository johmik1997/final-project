<template>  
  <div class="w-1/2">  
    <h2 class="text-lg font-semibold mb-2">Check Table</h2>  
    <table class="min-w-full table-auto text-xs">  
      <thead>  
        <tr class="text-[#A3AED0]">  
          <th class="px-4 py-2 text-left">NAME</th>  
          <th class="px-4 py-2 text-left">PROGRESS</th>  
          <th class="px-4 py-2 text-left">QUANTITY</th>  
          <th class="px-4 py-2 text-left">DATE</th>  
        </tr>  
      </thead>  
      <tbody>  
        <tr v-for="(item, index) in tableData" :key="index" class="hover:bg-gray-100">  
          <td class="px-4 py-2">  
            <input type="checkbox" v-model="item.checked" class="mr-1" />  
            {{ item.name }}  
          </td>  
          <td class="px-4 py-2">{{ item.progress }}</td>  
          <td class="px-4 py-2">{{ item.quantity }}</td>  
          <td class="px-4 py-2">{{ item.date }}</td>  
        </tr>  
      </tbody>  
    </table>  
  </div>  
</template>  

<script setup>  
import { ref } from 'vue';  

const tableData = ref([  
  { name: 'Horizon UI PRO', progress: '17.5%', quantity: '2.458', date: '24.Jan.2021', checked: false },  
  { name: 'Horizon UI Free', progress: '10.8%', quantity: '1.485', date: '12.Jun.2021', checked: true },  
  { name: 'Weekly Update', progress: '21.3%', quantity: '1.024', date: '5.Jan.2021', checked: true },  
  { name: 'Venus 3D Asset', progress: '31.5%', quantity: '858', date: '7.Mar.2021', checked: false },  
  { name: 'Marketplace', progress: '12.2%', quantity: '258', date: '17.Dec.2021', checked: false }  
]);  
</script>  

<style scoped>  
table {  
  border-collapse: collapse;  
}  
td, th {  
  border: none;  
}  
</style>  
