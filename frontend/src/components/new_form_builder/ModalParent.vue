<script setup></script>
<template>
  <div class="p-2 sm:p-4 grid place-items-center min-h-full bg-primary/20 overflow-y-auto">
    <div class="w-full max-w-full flex justify-center items-center min-h-full py-2 sm:py-4">
      <slot />
    </div>
  </div>
</template>

<style scoped>
/* Ensure proper mobile scrolling */
@media (max-width: 640px) {
  div {
    -webkit-overflow-scrolling: touch;
  }
}
</style>
