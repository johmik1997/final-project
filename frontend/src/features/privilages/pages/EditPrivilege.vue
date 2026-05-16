<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router';
import { useApiRequest } from '@/composables/useApiRequest';
import { getPrivilegeById, updatePrivilege } from '../Api/PrivilegeApi';
import NewFormParent from '../../roles/components/NewFormParent.vue';
import PrivilegeForm from '../form/PrivilegeForm.vue';
import { usePrivilege } from '../store/privilegeStore';
import { ref } from 'vue';
import { toasted } from '@/utils/utils.js';
import Button from '@/components/Button.vue';
import { useForm } from '@/components/new_form_builder/useForm';

const { submit } = useForm('privilegeForm');
const privilegeStore = usePrivilege()
const route = useRoute()
const privilegeUuid = route.params.privilegeUuid;
const req = useApiRequest()
const updateReq = useApiRequest()

const privilege = ref(
    privilegeStore.privilege.find((el) => el.privilegeUuid == privilegeUuid) || {}
);

if (!Object.keys(privilege.value).length) {
    req.send(
        () => getPrivilegeById(privilegeUuid),
        (res) => {
            if (res.success) {
                privilege.value = res.data;
            }
        }
    );
}

function update({ values }) {
    updateReq.send(
        () => updatePrivilege(privilegeUuid, values),
        (res) => {
            if (res.success) {
                privilegeStore.update(privilegeUuid, { ...privilege, ...values });
            }
            toasted(res.success, 'Successfully Updated', res.error);
        }
    );
}

const router = useRouter();

const goBack = () => {
    router.go(-1);
};

</script>
<template>
    <NewFormParent size="xl" title="Update Privileges">
        <PrivilegeForm :privilege="privilege" />
        <Button size="xl" type="primary" class="flex justify-center items-center mt-3 gap-3 p-2 bg-primary"
            :pending="req.pending.value" @click.prevent="submit(update)">
            Update Privilege
        </Button>
        <!-- <template #bottom>
            <div class="flex justify-center p-2 px-4">
                <Button class="flex items-center gap-3" :pending="updateReq.pending.value" type="primary"
                    @click.prevent="submit(update)">
                   
                    Update Privilege
                </Button>
            </div>
        </template> -->
    </NewFormParent>
</template>