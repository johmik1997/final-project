<script setup>
import { inject, watch } from "vue";

const props = defineProps({
  headers: {
    type: Array,
    required: true,
  },
  showFooter: {
    type: Boolean,
    default: true,
  },
  firstCol: {
    type: Boolean,
    default: false,
  },
});

const next = inject("next", () => {});
const previous = inject("previous", () => {});

const page = inject("page", 1);
const totalPages = inject("totalPages", 1);
</script>
<template>
  <table class="min-w-full rounded-lg text-sm">
    <thead class="capitalize">
      <tr>
        <th
          v-if="firstCol"
          class="th p-2 text-left uppercase tracking-wider"
        ></th>

        <th class="th p-2 text-left uppercase tracking-wider !font-bold">#</th>
        <!-- Add row number column -->
        <th
          :title="header"
          v-for="header in headers"
          :key="header"
          class="truncate p-2 text-left !font-bold"
        >
          {{ header }}
        </th>
      </tr>
    </thead>
    <tbody>
      <slot />
    </tbody>
  </table>
</template>
<style scoped>
th {
  font-weight: 500;
}
</style>
