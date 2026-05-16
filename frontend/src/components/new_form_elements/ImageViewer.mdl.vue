<script setup>
import { ModalParent } from "@customizer/modal-x";
import { closeModal } from "@customizer/modal-x";
import BaseIcon from "@/components/base/BaseIcon.vue";
import { mdiClose } from "@mdi/js";

const props = defineProps({
  data: {
    type: Object,
    required: true
  }
});

const handleApprove = () => {
  // Add your approve logic here
  console.log('Image approved');
  closeModal();
};

const handleReject = () => {
  // Add your reject logic here
  console.log('Image rejected');
  closeModal();
};
</script>

<template>
  <ModalParent
    v-slot="{ data }"
    name="ImageViewer"
    class="fixed inset-0 flex items-center justify-center bg-black/50 p-4"
  >
    <div class="relative bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
      <!-- Header -->
      <div class="flex justify-between items-center p-4 border-b">
        <h3 class="text-xl font-semibold">{{ data.title }}</h3>
        <button
          @click="closeModal()"
          class="rounded-full bg-gray-100 text-gray-800 w-8 h-8 flex items-center justify-center"
        >
          <BaseIcon :path="mdiClose" />
        </button>
      </div>

      <!-- Image Container -->
      <div class="p-4 overflow-auto max-h-[calc(90vh-160px)]">
        <img 
          :src="data.imageUrl" 
          :alt="data.title"
          class="w-full h-auto"
        />
      </div>

      <!-- Action Buttons -->
      <div class="flex justify-end gap-3 p-4 border-t">
        <button
          @click="handleReject"
          class="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
        >
          Reject
        </button>
        <button
          @click="handleApprove"
          class="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600"
        >
          Approve
        </button>
      </div>
    </div>
  </ModalParent>
</template>
