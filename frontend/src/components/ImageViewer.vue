<script setup>
import { defineProps } from 'vue';
import { closeModal } from "@customizer/modal-x";

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  imageUrl: {
    type: String,
    required: true
  }
});
</script>

<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
    <div class="bg-white rounded-lg max-w-4xl w-full">
      <div class="p-4 border-b flex justify-between items-center">
        <h3 class="text-lg font-semibold">{{ title }}</h3>
        <button @click="closeModal()" class="text-gray-500 hover:text-gray-700">
          <span class="sr-only">Close</span>
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
      <div class="p-4">
        <img :src="imageUrl" alt="Receipt" class="w-full h-auto" />
      </div>
    </div>
  </div>
</template>