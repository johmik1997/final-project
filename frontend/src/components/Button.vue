<script setup>
import icons from '@/utils/icons';

const props = defineProps({
  pending: {
    type: Boolean,
    default: false,
  },
  size: {
    type: String,
    default: "sm",
  },
  type: {
    type: String,
  },
  noTransition: {
    type: Boolean,
    default: false
  }
});
</script>
<template>
  <button
    v-ripple
    :class="[
      $style?.[size], 
      $style?.[type],
      noTransition ? 'transition-none' : ''
    ]"
    class=" py-1 flex items-center justify-center rounded capitalize"
  >
    <slot v-if="!pending"></slot>
    <i class="m-auto" v-else v-html="icons.spinner" />
  </button>
</template>
<style module>
.xs {
  width: auto;
  height: auto;
}

.sm {
  min-width: 6rem;
  min-height: 2rem;
}

.md {
  min-width: 6.8rem;
  min-height: 2rem;
}

.lg {
  min-width: 6.8rem;
  min-height: 2rem;
}

.secondary {
  @apply bg-secondary text-white;
}

.primary {
  @apply bg-primary text-white;
}
</style>

