<script setup>
import { usePagination } from '@/composables/usePagination';
import { watch } from 'vue';
import { usePrivilege } from '../store/privilegeStore';
import { getAllPrivilege } from '../Api/PrivilegeApi';


const props = defineProps({
  prePage: {
    type: Number,
    default: 25
  }
})
const privilegesStore = usePrivilege();

const pagination = usePagination({
  auto: false,
  perPage: props.prePage,
  store: privilegesStore,
  cb: getAllPrivilege,
});

if (privilegesStore.privilege.length == 0) {
  pagination.send();
}

watch(pagination.data, console.log, { immediate: true })
</script>
<template>
  {{ console.log(privilegesStore.privilege) }}
  <slot :pending="pagination.pending.value" :error="pagination.error.value" :privileges="privilegesStore.privilege" />
</template>
