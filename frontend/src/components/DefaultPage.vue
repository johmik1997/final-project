<script setup>
import icons from "@/utils/icons";
import { ref, watch } from "vue"

const props = defineProps({
  modelValue: {
    type: String,
  },
  title: {
    Type: String,
  },
	placeholder: String,
  showHeader: {
    type: Boolean,
    default: true
  }
});

const emit = defineEmits(['update:modelValue'])
const search = ref("");

watch(search, () => {
  emit('update:modelValue', search.value)
})
const inputData = ref("");
watch(inputData, () => {
  emit("update:modelValue", inputData.value);
});
</script>
<template>
  <div class="flex flex-col h-full bg-white">
    <div class="flex justify-between gap-2 items-center h-10 p-2 border-b">
   
      <slot v-if="showHeader" name="header">
				<div tabindex="0" class="w-[20rem] focus-within:border-primary overflow-hidden shadow-primary h-full flex justify-end items-center border rounded-md">
					<span class="size-10 border-r grid place-items-center" v-html='icons.search' />
					<input v-model="search" :placeholder="placeholder || 'Search...'" class="!shadow-none flex-1 px-3 h-full" />
				</div>
      </slot>
      <slot name="more" />
    </div>
    <slot :search="search" />
  </div>
</template>
