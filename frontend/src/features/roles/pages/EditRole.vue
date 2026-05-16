<script setup>
import { useRoute, useRouter } from 'vue-router';
import { useApiRequest } from '@/composables/useApiRequest';
import { getRoleById, updateRolebyId } from '../Api/RoleApi';
import { useRoles } from '../store/roleStore';
import { ref } from 'vue';
import NewFormParent from '../components/NewFormParent.vue';
import PrivilegesDataProvider from '../../privilages/components/PrivilegesDataProvider.vue';
import Button from '@/components/Button.vue';
import RoleForm from '../form/RoleForm.vue';
import { useForm } from '@/components/new_form_builder/useForm';
import { toasted } from '@/utils/utils';

const roleStore = useRoles();
const route = useRoute()
const roleUuid = route.params.roleUuid
const role = ref(roleStore.roles.find((el) => el.roleUuid == roleUuid) || {});
const req = useApiRequest()
const updateReq = useApiRequest()
const { submit } = useForm('roleForm')

if (!Object.keys(role.value).length) {
    req.send(
        () => getRoleById(roleUuid),
        (res) => {
            if (res.success) {
                role.value = res.data;
            }
        }
    );
    console.log(role);
}
function update({ values }) {
    console.log(values);
    updateReq.send(
        () => updateRolebyId(roleUuid, values),
        (res) => {
            if (res.success) {
                roleStore.update(roleUuid, { ...role, ...values });
            }
            toasted(res.success, 'Successfully Updated', res.error);
        }
    );
}
const router = useRouter();
const goBack = () => {
    router.go(-1);
}

</script>
<template>
    <button @click.prevent="goBack">
        <div class="p-6 flex gap-2 item-center ">

            <span class="item-center mt-1">
                <svg width="7" height="13" viewBox="0 0 7 13" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path opacity="0.6" fill-rule="evenodd" clip-rule="evenodd"
                        d="M5.82539 1.0134C6.03505 1.20471 6.05933 1.54072 5.87962 1.76391L2.15854 6.38525L5.87962 11.0066C6.05933 11.2298 6.03505 11.5658 5.82539 11.7571C5.61572 11.9484 5.30007 11.9226 5.12036 11.6994L1.12037 6.73164C0.959876 6.53232 0.959876 6.23819 1.12037 6.03887L5.12036 1.07113C5.30008 0.847943 5.61572 0.822096 5.82539 1.0134Z"
                        fill="#263558" stroke="#263558" stroke-linecap="round" />
                </svg>
            </span>
            <h3>Go Back</h3>


        </div>
    </button>
    <NewFormParent size="xl" title="Update Roles">
        <PrivilegesDataProvider :pre-page="500" v-slot="{ privileges, pending }">
            <RoleForm v-if="!pending" :selectPrivilege="role?.privileges" :privileges="privileges" :roles="role" />
        </PrivilegesDataProvider>
        <Button size="sm" type="primary" class="flex justify-center items-center mt-3 gap-3 p-2 bg-primary"
            :pending="updateReq.pending.value" @click.prevent="submit(update)">
            Update Role
        </Button>

    </NewFormParent>
</template>