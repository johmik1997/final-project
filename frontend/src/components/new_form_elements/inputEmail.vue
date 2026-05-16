<script setup>
import { ref, computed } from "vue";
import Input from "./Input.vue";
import icons from "@/utils/icons"; // Make sure this contains an email icon

const props = defineProps({
  modelValue: String, // Bind to v-model
  attributes: {
    type: Object,
  },
});

// Reactive email value
const email = ref(props.modelValue);

// Email validation function
const isValidEmail = computed(() => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email.value);
});

// Emit the updated value
const emit = defineEmits(["update:modelValue"]);
</script>

<template>
  <div class="relative">
    <Input
      :modelValue="email"
      @update:modelValue="(value) => { email = value; emit('update:modelValue', value); }"
      :attributes="{ ...attributes, type: 'email', placeholder: 'Enter your email' }"
    >
      <template #right>
        <div class="h-full w-12 grid place-items-center border-r bg-red-400">
          <!-- <i v-html="icons.email" class="text-gray-500" /> -->
        </div>
      </template>
    </Input>
    <p v-if="email && !isValidEmail" class="text-red-500 text-sm mt-1">
      Please enter a valid email address.
    </p>
  </div>
</template>
