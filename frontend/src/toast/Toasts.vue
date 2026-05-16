<script setup lang="ts">
import { watch } from 'vue'
import { useToast } from "./store/toast";
import Toast from "./Toast.vue";

const {toasts} = useToast()

</script>
<template>
  <Suspense>
    <div v-if="toasts.length" class="z-[502] fixed bottom-4 left-4 flex flex-col gap-4">
      <Toast v-for="({id, toast}, idx) in toasts" :key="id" :id="id" :toast="toast" />
    </div>
  </Suspense>
</template>