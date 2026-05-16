<template>  
  <div class="w-1/4">  
    <div class="flex justify-between items-center mb-4">  
      <select v-model="selectedMonth" class=" items-center text-center text-[#4318FF] bg-[#F4F7FE] rounded-full ml-6 py-2">  
        <option v-for="month in months" :key="month.value" :value="month.value">  
          {{ month.name }}  
        </option>  
      </select>  
      <select v-model="selectedYear" class=" rounded-full mr-14 py-1">  
        <option v-for="year in years" :key="year">{{ year }}</option>  
      </select>  
    </div>  
    <div class="grid grid-cols-7 text-center font-bold text-gray-600">  
      <div>Mo</div>  
      <div>Tu</div>  
      <div>We</div>  
      <div>Th</div>  
      <div>Fr</div>  
      <div>Sa</div>  
      <div>Su</div>  
    </div>  
    <div class="grid grid-cols-7 mt-2">  
      <div v-for="blank in blankDays" :key="blank" class="p-2"></div>  
      <div  
        v-for="date in daysInMonth"  
        :key="date"  
        @click="selectDate(date)"  
        :class="[  
          'flex justify-center items-center h-8 w-8 cursor-pointer transition-transform duration-200 rounded-full',  
          { 'bg-[#4318FF] text-white': isStartDate(date) || isEndDate(date) },  
          { 'bg-[#F4F7FE] text-[#4318FF]': isInRange(date) },  
          { 'bg-gray-200': isToday(date) }  // Light gray for today's date  
        ]"  
      >  
        {{ date }}  
      </div>  
    </div>  
  </div>  
</template>  

<script setup>  
import { ref, computed } from 'vue';  

const months = [  
  { name: 'January', value: 1 },  
  { name: 'February', value: 2 },  
  { name: 'March', value: 3 },  
  { name: 'April', value: 4 },  
  { name: 'May', value: 5 },  
  { name: 'June', value: 6 },  
  { name: 'July', value: 7 },  
  { name: 'August', value: 8 },  
  { name: 'September', value: 9 },  
  { name: 'October', value: 10 },  
  { name: 'November', value: 11 },  
  { name: 'December', value: 12 },  
];  

const currentYear = new Date().getFullYear();  
const years = Array.from({ length: 5 }, (v, i) => currentYear + i);  

const selectedMonth = ref(4); // Default to April  
const selectedYear = ref(currentYear);  
const startDate = ref(null);  
const endDate = ref(null);  

const daysInMonth = computed(() => {  
  const date = new Date(selectedYear.value, selectedMonth.value, 0);  
  return Array.from({ length: date.getDate() }, (v, i) => i + 1);  
});  

const blankDays = computed(() => {  
  const firstDayOfMonth = new Date(selectedYear.value, selectedMonth.value - 1, 1);  
  return firstDayOfMonth.getDay() === 0 ? 6 : firstDayOfMonth.getDay() - 1;  
});  

// Function to select a date  
const selectDate = (date) => {  
  if (!startDate.value) {  
    startDate.value = date;  
  } else if (!endDate.value) {  
    endDate.value = date > startDate.value ? date : startDate.value;  
    startDate.value = date < startDate.value ? date : startDate.value;  
  } else {  
    startDate.value = date;  
    endDate.value = null;  
  }  
};  

// Check if the date is the start date  
const isStartDate = (date) => {  
  return date === startDate.value;  
};  

// Check if the date is the end date  
const isEndDate = (date) => {  
  return date === endDate.value;  
};  

// Check if the date is in the selected range  
const isInRange = (date) => {  
  return (  
    startDate.value &&  
    endDate.value &&  
    date > startDate.value && date < endDate.value  
  );  
};  

// Check if the date is today  
const isToday = (date) => {  
  const today = new Date();  
  return date === today.getDate() &&   
         selectedMonth.value === today.getMonth() + 1 &&   
         selectedYear.value === today.getFullYear();  
};  
</script>  

<style scoped>  
/* You can add additional styles here */  
</style>