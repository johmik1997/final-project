<script setup>
import { usePagination } from '@/composables/usePaginationTemp';
import { watch } from 'vue';
import { getAllPrograms } from '../api/ProgramApi';
import { usePrograms } from '../store/programsStore';

const props = defineProps({
  prePage: {
    type: Number,
    default: 25
  }
})
const programsStore = usePrograms();

const pagination = usePagination({
  perPage: props.prePage,
  store: programsStore,
  cb: getAllPrograms,
});

if (programsStore.programs.length == 0) {
  pagination.send();
}

watch(pagination.data, console.log, { immediate: true })
</script>
<template>
  <slot :pending="pagination.pending.value" :error="pagination.error.value" :programs="programsStore.programs" />
</template>
