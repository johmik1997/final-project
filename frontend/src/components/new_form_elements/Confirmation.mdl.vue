<script setup>
import { ModalParent } from "@customizer/modal-x";
import { closeModal } from "@customizer/modal-x";
import BaseIcon from "@/components/base/BaseIcon.vue";
import { mdiClose } from "@mdi/js";

const modalName = "Confirmation";

function yes() {
  closeModal(true);
}

function no() {
  closeModal(false);
}
</script>

<template>
  <ModalParent
    v-slot="{ data }"
    :name="modalName"
    class="flex justify-center items-center inset-0 py-4  bg-black/50 p-4"
  >
    <div class="relative bg-white rounded-xl w-[400px] shadow-lg p-6 ">
      <!-- Close Button -->
      <button
        @click="closeModal()"
        class="absolute top-4 right-4 text-gray-600 hover:text-gray-900"
      >
        <BaseIcon :path="mdiClose" class="w-5 h-5" />
      </button>

      <!-- Title -->
      <p class="text-lg font-bold items-center text-gray-800 mb-4 py-2 border-b">
        {{ data?.title || "Confirm Authorization" }}
      </p>

      <!-- Message -->
      <p class="text-gray-600 text-sm leading-relaxed">
        {{ data?.message || "Are you sure you want to authorize disbursement amount of ETB 74,000 to Lion Insurance?" }}
      </p>

      <!-- Buttons -->
      <div class="flex justify-end gap-4 mt-6 pb-2">
        <button
          @click="no"
          class="bg-[#FC5A5A] text-white px-6 py-2  text-sm font-medium hover:bg-red-600"
        >
          Cancel
        </button>
        <button
          @click="yes"
          class="bg-[#2E3365] text-white px-6 py-2  text-sm font-medium hover:bg-[#1E224D]"
        >
          Confirm
        </button>
      </div>
    </div>
  </ModalParent>
</template>
