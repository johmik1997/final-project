<script setup>
import Table from '@/components/Table.vue';
import { useRoles } from '../store/roleStore';
import { getAllRole, removeRoleById } from '../Api/RoleApi';
import { toasted } from '@/utils/utils';
import { useApiRequest } from '@/composables/useApiRequest';
import TableRowSkeleton from '@/components/TableRowSkeleton.vue';
import { openModal } from '@customizer/modal-x';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiDeleteAlert, mdiPencil } from '@mdi/js';
import { usePaginationcopy } from '@/composables/usePaginationcopy';

const rolesStore = useRoles();

const pagination = usePaginationcopy({
  store: rolesStore,
  cb: getAllRole,
});

const removeReq = useApiRequest();

function remove(id) {
  openModal(
    'Confirmation',
    {
      title: 'Remove Role',
      message: 'Are you sure you want to delete this role?',
    },
    (res) => {
      if (res) {
        removeReq.send(
          () => removeRoleById(id),
          (res) => {
            if (res.success) {
              rolesStore.remove(id);
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
    <!-- Add Role Button -->
    <div class="flex flex-col sm:flex-row justify-end items-start sm:items-center gap-4 mb-6">
      <slot name="select">
        <router-link to="/add_role">
          <button class="bg-primary text-white px-4 py-2 rounded-md flex items-center gap-2 w-full sm:w-auto justify-center">
            <!-- Icon -->
            <svg width="14" height="14" viewBox="0 0 12 14" fill="white" xmlns="http://www.w3.org/2000/svg">
              <path
                d="M1 4.04995C0.723858 4.04995 0.5 4.27381 0.5 4.54995C0.5 4.82609 0.723858 5.04995 1 5.04995V4.04995ZM2.2 5.04995C2.47614 5.04995 2.7 4.82609 2.7 4.54995C2.7 4.27381 2.47614 4.04995 2.2 4.04995V5.04995ZM1 6.44995C0.723858 6.44995 0.5 6.67381 0.5 6.94995C0.5 7.22609 0.723858 7.44995 1 7.44995V6.44995ZM2.2 7.44995C2.47614 7.44995 2.7 7.22609 2.7 6.94995C2.7 6.67381 2.47614 6.44995 2.2 6.44995V7.44995ZM1 8.84995C0.723858 8.84995 0.5 9.07381 0.5 9.34995C0.5 9.62609 0.723858 9.84995 1 9.84995V8.84995ZM2.2 9.84995C2.47614 9.84995 2.7 9.62609 2.7 9.34995C2.7 9.07381 2.47614 8.84995 2.2 8.84995V9.84995ZM6.9 5.14995V4.64995H5.9V5.14995H6.9ZM5.9 8.74995V9.24995H6.9V8.74995H5.9ZM8.2 7.44995H8.7V6.44995H8.2V7.44995ZM4.6 6.44995H4.1V7.44995H4.6V6.44995ZM1 5.04995H2.2V4.04995H1V5.04995ZM1 7.44995H2.2V6.44995H1V7.44995ZM1 9.84995H2.2V8.84995H1V9.84995ZM2.8 13.45H10V12.45H2.8V13.45ZM10 13.45C10.9389 13.45 11.7 12.6889 11.7 11.75H10.7C10.7 12.1366 10.3866 12.45 10 12.45V13.45ZM11.7 11.75V2.14995H10.7V11.75H11.7ZM11.7 2.14995C11.7 1.21107 10.9389 0.449951 10 0.449951V1.44995C10.3866 1.44995 10.7 1.76335 10.7 2.14995H11.7ZM10 0.449951H2.8V1.44995H10V0.449951ZM2.8 0.449951C1.86112 0.449951 1.1 1.21107 1.1 2.14995H2.1C2.1 1.76335 2.4134 1.44995 2.8 1.44995V0.449951ZM1.1 2.14995V11.75H2.1V2.14995H1.1ZM1.1 11.75C1.1 12.6889 1.86112 13.45 2.8 13.45V12.45C2.4134 12.45 2.1 12.1366 2.1 11.75H1.1ZM5.9 5.14995V8.74995H6.9V5.14995H5.9ZM8.2 6.44995H4.6V7.44995H8.2V6.44995Z"
                fill="white" />
            </svg>
            <span>Add Role</span>
          </button>
        </router-link>
      </slot>
    </div>

    <!-- Roles Table -->
    <div class="overflow-x-auto">
      <Table
        :pending="pagination.pending.value"
        :headers="{
          head: ['Role Name', 'Role Description', 'Actions'],
          row: ['roleName', 'roleDescription']
        }"
        :Fallback="TableRowSkeleton"
        :rows="rolesStore.roles"
      >
        <template #actions="{ row }">
          <div class="flex flex-col sm:flex-row gap-2">
            <button
              class="bg-gray-600 text-white px-3 py-1 rounded flex justify-center items-center gap-1"
              @click="$router.push('/edit_role/' + row?.roleUuid)"
            >
              <BaseIcon :path="mdiPencil" />
              <span class=" sm:inline">Edit</span>
            </button>
            <button
              class="bg-[#FF4C4C] text-white px-3 py-1 rounded flex justify-center items-center gap-1"
              @click="remove(row?.roleUuid)"
            >
              <BaseIcon :path="mdiDeleteAlert" />
              <span class=" sm:inline">Delete</span>
            </button>
          </div>
        </template>
      </Table>
    </div>
  </div>
</template>
