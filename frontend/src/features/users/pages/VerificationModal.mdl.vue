<script setup>
import { ModalParent } from "@customizer/modal-x";
import { closeModal } from "@customizer/modal-x";
import BaseIcon from "@/components/base/BaseIcon.vue";
import { mdiClose } from "@mdi/js";
import { ref } from "vue";

const modalName = "VerificationModal";
const verificationCode = ref("");

function submit() {
  if (verificationCode.value.trim()) {
    closeModal(verificationCode.value);
  }
}

function cancel() {
  closeModal(false);
}
</script>

<template>
  <ModalParent
    v-slot="{ data }"
    :name="modalName"
    class="flex justify-center items-center inset-0 py-4 bg-black/50 p-4"
  >
    <div class="relative bg-white rounded-xl w-[450px] shadow-lg p-6">
      <!-- Close Button -->
      <button
        @click="cancel"
        class="absolute top-4 right-4 text-gray-600 hover:text-gray-900"
      >
        <BaseIcon :path="mdiClose" class="w-5 h-5" />
      </button>

      <!-- Title -->
      <p class="text-lg font-bold items-center text-gray-800 mb-4 py-2 border-b">
        {{ data?.title || "Verify User" }}
      </p>

      <!-- Message -->
      <p class="text-gray-600 text-sm leading-relaxed mb-4">
        {{ data?.message || "Enter verification code sent to the user's phone" }}
      </p>

      <!-- Verification Code Input -->
      <div class="mb-5">
        <label class="block text-sm font-medium text-gray-700 mb-1">
          {{ data?.inputLabel || "Verification Code" }}
        </label>
        <input
          type="text"
          v-model="verificationCode"
          :placeholder="data?.inputPlaceholder || 'Enter verification code'"
          class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          @keyup.enter="submit"
        />
      </div>

      <!-- Buttons -->
      <div class="flex justify-end gap-4 mt-2 pb-2">
        <button
          @click="cancel"
          class="bg-[#FC5A5A] text-white px-6 py-2 text-sm font-medium hover:bg-red-600 rounded-md"
        >
          Cancel
        </button>
        <button
          @click="submit"
          :disabled="!verificationCode.trim()"
          :class="{'bg-blue-400 cursor-not-allowed': !verificationCode.trim(), 'bg-[#2E3365] hover:bg-[#1E224D]': verificationCode.trim()}"
          class="text-white px-6 py-2 text-sm font-medium rounded-md transition-colors"
        >
          Verify
        </button>
      </div>
    </div>
  </ModalParent>
</template>