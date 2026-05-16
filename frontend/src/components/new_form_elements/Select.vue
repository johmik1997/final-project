<script setup>
import icons from "@/utils/icons";
import InputParent from "../new_form_builder/InputParent.vue";
import InputLayout from "./NewInputLayout.vue";

const props = defineProps({
  obj: {
    type: Boolean,
    default: false,
  },
  options: {
    type: Array,
    required: true,
  },
});
</script>
<template>
  <InputParent v-slot="{ setRef, error, validation, value, attributes, changeValue }">
    <InputLayout
      :validation="validation"
      :error="error"
      :label="$attrs.label"
      :hideSuccessIcon="true"
    >
      <div class="input-wrapper">
        <slot name="left" />
        <select :ref="setRef">
          <option
            value=""
            disabled
          >
            {{ attributes?.placeholder || 'Select an option' }}
          </option>
          
          <template v-if="!obj">
            <option
              :value="option"
              :key="option"
              v-for="option in options"
            >
              {{ option }}
            </option>
          </template>
          
          <template v-else>
            <option
              :value="option.value"
              :key="option.value"
              v-for="option in options"
            >
              {{ option.label }}
            </option>
          </template>
        </select>
        
        <!-- Custom Dropdown Arrow -->
        <div class="select-arrow">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
          </svg>
        </div>
        
        <slot name="right" />
      </div>
    </InputLayout>
  </InputParent>
</template>

<style scoped>
.select-arrow {
  @apply absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none text-gray-500 transition-all duration-200 z-20;
}

:deep(.input-wrapper:focus-within .select-arrow) {
  @apply text-blue-500 rotate-180;
}
</style>




