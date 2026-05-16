<script setup>
defineProps({
  label: String,
  error: String,
  validation: String,
  required: Boolean,
  hint: String,
  hideSuccessIcon: {
    type: Boolean,
    default: false
  }
});
</script>

<template>
  <div class="input-field-container">
    <!-- Label -->
    <label v-if="label" class="input-label">
      {{ label }}
      <span v-if="required || validation?.includes('required')" class="required-asterisk">*</span>
    </label>

    <!-- Input Container -->
    <div class="input-container">
      <div :class="{ 'has-error': error }">
        <slot />
      </div>
      
      <!-- Success Icon (hidden for selects) -->
      <div v-if="!error && validation && !hideSuccessIcon" class="validation-icon success-icon">
        <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
        </svg>
      </div>
    </div>

    <!-- Error Message -->
    <transition name="error-slide">
      <div v-if="error" class="error-message">
        <svg class="error-message-icon" fill="currentColor" viewBox="0 0 20 20">
          <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
        </svg>
        {{ error }}
      </div>
    </transition>

    <!-- Hint Text -->
    <div v-if="hint && !error" class="hint-text">
      {{ hint }}
    </div>
  </div>
</template>

<style scoped>
.input-field-container {
  @apply space-y-2;
}

.input-label {
  @apply block text-sm font-semibold text-gray-700 mb-2;
}

.dark .input-label {
  @apply text-slate-200;
}

.required-asterisk {
  @apply text-red-500 ml-1;
}

.input-container {
  @apply relative;
}

/* Input wrapper styles */
:deep(.input-wrapper) {
  @apply relative flex items-center w-full overflow-hidden border-2 border-gray-200 bg-white rounded-xl transition-all duration-300 ease-in-out;
  @apply hover:border-gray-300 hover:shadow-md;
  @apply focus-within:border-blue-500 focus-within:ring-4 focus-within:ring-blue-500/10 focus-within:shadow-lg focus-within:shadow-blue-500/10;
}

.dark :deep(.input-wrapper) {
  @apply border-slate-700 bg-slate-900/90 hover:border-slate-600;
}

/* Error state wrapper - HIGHEST PRIORITY */
:deep(.input-wrapper:has(input:invalid)),
:deep(.input-wrapper:has(input[aria-invalid="true"])),
:deep(.input-wrapper:has(select:invalid)),
:deep(.input-wrapper:has(select[aria-invalid="true"])),
:deep(.input-wrapper.has-error) {
  @apply border-red-400 bg-red-50/30 focus-within:ring-red-500/10 focus-within:border-red-500 focus-within:shadow-red-500/10 !important;
}

/* Success state wrapper - LOWER PRIORITY, only when no error */
/* :deep(.input-wrapper:not(.has-error):has(input:valid:not(:placeholder-shown))),
:deep(.input-wrapper:not(.has-error):has(select:valid:not([value=""]))) {
  @apply border-green-400 bg-green-50/20 focus-within:ring-green-500/10 focus-within:border-green-500 focus-within:shadow-green-500/10;
} */

.validation-icon {
  @apply absolute right-3 top-1/2 transform -translate-y-1/2 pointer-events-none z-10;
}

.success-icon {
  @apply text-green-500 drop-shadow-sm;
}

.dark .success-icon {
  @apply text-emerald-400;
}

.error-message {
  @apply flex items-center space-x-2 text-sm text-red-700 bg-red-50 px-4 py-3 rounded-xl border border-red-200 shadow-sm;
}

.dark .error-message {
  @apply border-red-900/70 bg-red-950/40 text-red-200;
}

.error-message-icon {
  @apply w-4 h-4 flex-shrink-0;
}

.hint-text {
  @apply text-xs text-gray-500 mt-1 px-1;
}

.dark .hint-text {
  @apply text-slate-400;
}

/* Error slide animation */
.error-slide-enter-active,
.error-slide-leave-active {
  @apply transition-all duration-300 ease-in-out;
}

.error-slide-enter-from {
  @apply opacity-0 transform -translate-y-2 scale-95;
}

.error-slide-leave-to {
  @apply opacity-0 transform -translate-y-2 scale-95;
}

/* Focus within styling for better UX */
.input-field-container:focus-within .input-label {
  @apply text-blue-600 transition-colors duration-200;
}

.dark .input-field-container:focus-within .input-label {
  @apply text-blue-400;
}

/* Slot positioning */
:deep(.input-wrapper > *:first-child:not(input):not(select):not(textarea)) {
  @apply absolute left-3 z-10 text-gray-500 transition-colors duration-200;
}

:deep(.input-wrapper > *:last-child:not(input):not(select):not(textarea)) {
  @apply absolute right-3 z-10 text-gray-500 transition-colors duration-200;
}

.dark :deep(.input-wrapper > *:first-child:not(input):not(select):not(textarea)),
.dark :deep(.input-wrapper > *:last-child:not(input):not(select):not(textarea)) {
  @apply text-slate-400;
}

/* Focus state for slots */
:deep(.input-wrapper:focus-within > *:first-child:not(input):not(select):not(textarea)) {
  @apply text-blue-500;
}

:deep(.input-wrapper:focus-within > *:last-child:not(input):not(select):not(textarea)) {
  @apply text-blue-500;
}

/* Responsive adjustments */
@media (max-width: 640px) {
  .input-label {
    @apply text-xs;
  }
  
  .error-message {
    @apply text-xs px-3 py-2;
  }
}
</style>

<style>
/* Global styles for form inputs - similar to the old custom-input approach */
.custom-input,
.skiped-input {
  border: none;
  outline: none;
  width: 100%;
  background-color: transparent;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #111827;
  transition: all 0.2s ease-in-out;
}

.dark .custom-input,
.dark .skiped-input {
  color: #111827;
}

/* Select specific styles */
select.custom-input,
select.skiped-input {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-image: none;
  cursor: pointer;
  padding-right: 2.5rem; /* Space for arrow */
}

/* Remove default select styling */
select.custom-input::-ms-expand,
select.skiped-input::-ms-expand {
  display: none;
}

select.custom-input::-moz-focus-inner,
select.skiped-input::-moz-focus-inner {
  border: 0;
}

/* Adjust padding when slots are present */
.input-wrapper:has(> *:first-child:not(input):not(select)) .custom-input,
.input-wrapper:has(> *:first-child:not(input):not(select)) .skiped-input {
  padding-left: 3rem;
}

.input-wrapper:has(> *:last-child:not(input):not(select):not(.select-arrow)) .custom-input,
.input-wrapper:has(> *:last-child:not(input):not(select):not(.select-arrow)) .skiped-input {
  padding-right: 4rem; /* Extra space for both arrow and slot */
}

textarea.custom-input,
textarea.skiped-input {
  padding: 0.75rem 1rem;
  resize: none;
  height: 12rem;
  line-height: 1.5;
}

.custom-input:focus,
.skiped-input:focus {
  box-shadow: none;
  outline: none;
}

.custom-input::placeholder,
.skiped-input::placeholder {
  color: #9CA3AF;
  opacity: 1;
  font-weight: normal;
}

.dark .custom-input::placeholder,
.dark .skiped-input::placeholder {
  color: #64748b;
}

/* Disabled state */
.custom-input:disabled,
.skiped-input:disabled {
  background-color: #F9FAFB;
  color: #6B7280;
  cursor: not-allowed;
}

.dark .custom-input:disabled,
.dark .skiped-input:disabled {
  background-color: #0f172a;
  color: #64748b;
}
</style>






