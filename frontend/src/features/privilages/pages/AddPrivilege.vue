<script setup>
import PrivilegeForm from '../form/PrivilegeForm.vue';
import { useApiRequest } from '@/composables/useApiRequest';
import { usePrivilege } from '../store/privilegeStore';
import { toasted } from '@/utils/utils.js';
import { createPrivilege } from '../Api/PrivilegeApi';
import NewFormParent from '../../roles/components/NewFormParent.vue';
import { useRouter } from 'vue-router';
import { useForm } from '@/components/new_form_builder/useForm';
import Button from '@/components/Button.vue';

const req = useApiRequest();
const privilegeStore = usePrivilege();

const { submit } = useForm('privilegeForm');
function create({ values, reset }) {
    req.send(
        () => createPrivilege(values),
        (res) => {
            if (res.success) {
                privilegeStore.add(res.data);
                reset();
            }
            toasted(res.success, 'Privilege Created Successfully', res.error);

        });
}
const router = useRouter();

const goBack = () => {
    router.go(-1);
};

</script>
<template>
    <button @click.prevent="goBack">
        <div className="p-6 flex gap-2 item-center ">

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
    <!-- <div class="p-4 flex items-center space-x-2">
        <button @click.prevent="goBack" class="text-gray-700 font-medium opacity-60">← Back</button>
    </div> -->
    <NewFormParent size="xl" title="Add Privileges">
        <PrivilegeForm />
        <Button size="xl" type="primary" class="flex justify-center items-center mt-3 gap-3 p-2 bg-primary"
            :pending="req.pending.value" @click.prevent="submit(create)">
            <!-- <i class="pb-[3px]" v-html="icons.plus" /> -->
            Add Privilege
        </Button>

        <!-- <template #bottom>
            <div class="flex justify-end p-2 px-4">
                <Button class="flex items-center gap-3" :pending="req.pending.value" type="primary"
                    @click.prevent="submit(create)">
                    <i class="pb-[3px]" v-html="icons.plus" />
                    Add Privilege
                </Button>
            </div>
        </template> -->
    </NewFormParent>
</template>
