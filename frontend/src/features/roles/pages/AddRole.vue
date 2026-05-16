<script setup>
import PrivilegesDataProvider from '../../privilages/components/PrivilegesDataProvider.vue';
import { useApiRequest } from '@/composables/useApiRequest';
import { craeteRole } from "../Api/RoleApi";
import { toasted } from '@/utils/utils.js';
import { useRoles } from '../store/roleStore';
import RoleForm from '../form/RoleForm.vue';
import { useRouter } from 'vue-router';
import NewFormParent from '../components/NewFormParent.vue';
import Button from '@/components/Button.vue';
import { useForm } from '@/components/new_form_builder/useForm';

const { submit } = useForm('roleForm');
const roleStore = useRoles();
const req = useApiRequest();

function create({ values }) {
    req.send(
        () => craeteRole(values),
        (res) => {
            if (res.success) {
                roleStore.add(res.data);
            }
            toasted(res.success, 'Role Created', res.error);
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
        <div className="m-6 ml-1 flex gap-2 item-center ">

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
    <NewFormParent class="!p-0" size="xl" title="Add Role">
        <PrivilegesDataProvider :pre-page="500" v-slot="{ privileges, pending }">
            <RoleForm v-if="!pending" :privileges="privileges" :roles="roleStore" />
            <p v-else>Loading...</p>
        </PrivilegesDataProvider>
        <Button size="sm" type="primary" class="flex justify-center items-center mt-3 gap-3 p-2 bg-primary"
            :pending="req.pending.value" @click.prevent="submit(create)">
            <!-- <i class="pb-[3px]" v-html="icons.plus" /> -->
            Add Role
        </Button>
    </NewFormParent>
</template>
