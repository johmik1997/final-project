<script setup>
const props = defineProps({
  title: {
    type: String,
  },
});
</script>
<template>
  <div class="flex justify-between items-center">
    <p class="font-bold">{{ props.title }}</p>
    <slot name="header" />
  </div>
</template>
