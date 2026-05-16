<script setup>
const props = defineProps({
  data: {
    type: Array,
  },
});
</script>
<template>
  <div
    v-for="entries in props.data"
    :key="entries.title"
    class="flex flex-col gap-1 bg-white p-2 rounded-lg"
  >
    <div class="flex justify-between">
      <img :src="entries.Image" />
      <img class="w-20" :src="entries.today" />
    </div>
    <p class="opacity-70">{{ entries.title }}</p>
    <p class="font-bold leading-8 text-2xl">{{ entries.amount }}</p>

    <div class="font flex gap-1">
      <img src="@/assets/trending.svg" />
      <p class="text-primary">{{ entries.percent }}</p>
      Up from yesterday
    </div>
  </div>
</template>
