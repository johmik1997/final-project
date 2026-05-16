<script setup>
import { ModalParent, closeModal } from "@customizer/modal-x";

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  close: {
    type: Boolean,
    default: true,
  },
});
</script>
<template>
  <ModalParent :name="name" v-slot="modal" class="inset-0 flex h-full">
    <!-- <div class="w-drawer-width"></div> -->
    <div
      @click.self="closeModal()"
      class="grid place-items-center flex-1 p-4 bg-[#44444429] h-full overflow-y-auto"
    >
      <slot v-bind="modal" />
    </div>
  </ModalParent>
</template>
