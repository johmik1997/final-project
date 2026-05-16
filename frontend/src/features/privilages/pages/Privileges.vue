<script setup>
import Table from '@/components/Table.vue';
import PrivilegesDataProvider from '../components/PrivilegesDataProvider.vue';
import { usePagination } from '@/composables/usePagination';
import { usePrivilege } from '../store/privilegeStore';
import { useApiRequest } from '@/composables/useApiRequest';
import { toasted } from '@/utils/utils';
import { getAllPrivilege, removePrivilege } from '../Api/PrivilegeApi';
import { openModal } from '@customizer/modal-x';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiDeleteAlert, mdiPencil } from '@mdi/js';
import { RouterLink } from 'vue-router';

const privilegeStore = usePrivilege();
const pagination = usePagination({
  state: privilegeStore,
  cb: getAllPrivilege,
});

const removeReq = useApiRequest();

function remove(id) {
  openModal(
    'Confirmation',
    {
      title: 'Remove Privilege',
      message: 'Are you sure you want to delete this role?',
    },
    (res) => {
      if (res) {
        removeReq.send(
          () => removePrivilege(id),
          (res) => {
            if (res.success) {
              privilegeStore.remove(id);
            }
            toasted(res.success, 'Removed Successfully', res.error);
          }
        );
      }
    }
  );
}
</script>

<template>
  <div class="p-4 sm:p-7">
    <!-- Header Actions -->
    <div class="flex flex-col sm:flex-row sm:justify-end sm:space-x-4 space-y-4 sm:space-y-0 mb-4">
      <slot name="select">
        <RouterLink to="/add_privilege">
          <button class="bg-primary w-auto text-white px-4 py-2 rounded-md flex items-end gap-2  sm:w-auto justify-end">
            <svg width="14" height="14" viewBox="0 0 12 14" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M1 4.05C0.72 4.05 0.5 4.27 0.5 4.55C0.5 4.83 0.72 5.05 1 5.05V4.05ZM2.2 5.05C2.48 5.05 2.7 4.83 2.7 4.55C2.7 4.27 2.48 4.05 2.2 4.05V5.05ZM1 6.45C0.72 6.45 0.5 6.67 0.5 6.95C0.5 7.23 0.72 7.45 1 7.45V6.45ZM2.2 7.45C2.48 7.45 2.7 7.23 2.7 6.95C2.7 6.67 2.48 6.45 2.2 6.45V7.45ZM1 8.85C0.72 8.85 0.5 9.07 0.5 9.35C0.5 9.63 0.72 9.85 1 9.85V8.85ZM2.2 9.85C2.48 9.85 2.7 9.63 2.7 9.35C2.7 9.07 2.48 8.85 2.2 8.85V9.85ZM6.9 5.15V4.65H5.9V5.15H6.9ZM5.9 8.75V9.25H6.9V8.75H5.9ZM8.2 7.45H8.7V6.45H8.2V7.45ZM4.6 6.45H4.1V7.45H4.6V6.45ZM1 5.05H2.2V4.05H1V5.05ZM1 7.45H2.2V6.45H1V7.45ZM1 9.85H2.2V8.85H1V9.85ZM2.8 13.45H10V12.45H2.8V13.45ZM10 13.45C10.94 13.45 11.7 12.69 11.7 11.75H10.7C10.7 12.14 10.39 12.45 10 12.45V13.45ZM11.7 11.75V2.15H10.7V11.75H11.7ZM11.7 2.15C11.7 1.21 10.94 0.45 10 0.45V1.45C10.39 1.45 10.7 1.76 10.7 2.15H11.7ZM10 0.45H2.8V1.45H10V0.45ZM2.8 0.45C1.86 0.45 1.1 1.21 1.1 2.15H2.1C2.1 1.76 2.41 1.45 2.8 1.45V0.45ZM1.1 2.15V11.75H2.1V2.15H1.1ZM1.1 11.75C1.1 12.69 1.86 13.45 2.8 13.45V12.45C2.41 12.45 2.1 12.14 2.1 11.75H1.1ZM5.9 5.15V8.75H6.9V5.15H5.9ZM8.2 6.45H4.6V7.45H8.2V6.45Z"
                fill="white"
              />
            </svg>
            <span>Add Privilege</span>
          </button>
        </RouterLink>
      </slot>
    </div>

    <!-- Privileges Table -->
    <PrivilegesDataProvider v-slot="{ privileges, pending }">
      <div class="overflow-x-auto">
        <Table
          :headers="{
            head: ['Privilege Name', 'Privilege Description', 'Privilege Category', 'Actions'],
            row: ['privilegeName', 'privilegeDescription', 'privilegeCategory']
          }"
          :pending="pending"
          :rows="privileges || []"
        >
          <template #actions="{ row }">
            <div class="flex flex-col sm:flex-row gap-2">
              <button
                class="bg-gray-600 text-white justify-center px-3 py-1 rounded flex items-center gap-1"
                @click="$router.push('/edit_privilege/' + row?.privilegeUuid)"
              >
                <BaseIcon :path="mdiPencil" />
                <span class="items-center sm:inline ">Edit</span>
              </button>
              <button
                class="bg-[#FF4C4C] text-white px-3 py-1 rounded flex justify-center items-center gap-1"
                @click="remove(row?.privilegeUuid)"
              >
                <BaseIcon :path="mdiDeleteAlert" />
                <span class=" sm:inline">Delete</span>
              </button>
            </div>
          </template>
        </Table>
      </div>
    </PrivilegesDataProvider>
  </div>
</template>
