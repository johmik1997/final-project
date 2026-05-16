<script setup>
import { ModalParent, closeModal } from '@customizer/modal-x';
import { useApiRequest } from '@/composables/useApiRequest';
import { updateUserById } from '../Api/UserApi';
import { toasted } from '@/utils/utils.js';
import { useUsers } from '../store/userStore';
import NewFormParent from '../../roles/components/NewFormParent.vue';
import Button from '@/components/Button.vue';
import { useForm } from '@/components/new_form_builder/useForm';
import UserForm from '../form/userForm.vue';
import { emitEntityMutation } from '@/utils/entitySync';
import { getAllLibrary } from '@/features/library/api/libraryApi';

const modalName = 'EditUser';
const usersStore = useUsers();
const { submit } = useForm('userform');
const updateReq = useApiRequest();
const libraryReq = useApiRequest();

libraryReq.send(() => getAllLibrary({ page: 1, size: 200 }));

function getUserId(user) {
  return user?.userUuid || user?.id;
}

function update({ values }, userId, currentUser = {}) {
  if (!userId) {
    toasted(false, '', 'User id is missing.');
    return;
  }

  if (values.role !== 'MEMBER') {
    values.user_type = null;
    values.department = null;
  }

  updateReq.send(
    () => updateUserById(userId, values),
    (res) => {
      toasted(res.success, 'Successfully Updated', res.error);
      if (res.success) {
        const updatedUser = res.data || { ...(currentUser || {}), ...values };
        usersStore.update(userId, updatedUser);
        emitEntityMutation('users', { action: 'updated', id: userId });
        closeModal();
      }
    }
  );
}
</script>

<template>
  <ModalParent v-slot="{ data }" :name="modalName" class="bg-black/50 min-h-full p-4 sm:p-6 md:p-10 grid place-items-center">
    <NewFormParent title="Update User" size="md">
      <UserForm :user="data?.user || {}" :libraries="libraryReq.response.value?.libraries || libraryReq.response.value || []" />

      <div class="p-4 sm:p-6 pt-0">
        <Button
          type="secondary"
          class="w-full"
          :pending="updateReq.pending.value"
          @click.prevent="submit((payload) => update(payload, getUserId(data?.user), data?.user || {}))"
        >
          Update User
        </Button>
      </div>
    </NewFormParent>
  </ModalParent>
</template>
