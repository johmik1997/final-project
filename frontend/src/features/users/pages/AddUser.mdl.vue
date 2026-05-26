<script setup>
import Button from '@/components/Button.vue';
import Input from '@/components/new_form_elements/Input.vue';
import InputPassword from '@/components/new_form_elements/InputPassword.vue';
import Select from '@/components/new_form_elements/Select.vue';
import Form from '@/components/new_form_builder/Form.vue';
import NewFormParent from '../../roles/components/NewFormParent.vue';
import { closeModal } from '@customizer/modal-x';
import { useApiRequest } from '@/composables/useApiRequest';
import { CreateUser } from '../Api/UserApi';
import { useUsers } from '../store/userStore';
import { toasted } from '@/utils/utils';
import { useForm } from '@/components/new_form_builder/useForm';
import { computed, ref } from 'vue';
import { emitEntityMutation } from '@/utils/entitySync';
import { getAllLibrary } from '@/features/library/api/libraryApi';

const { submit } = useForm('addform');

const user = useUsers();
const req = useApiRequest();
const libraryReq = useApiRequest();
const role = ref('');
libraryReq.send(() => getAllLibrary({ page: 1, size: 200 }));

const libraryOptions = computed(() => libraryReq.response.value?.libraries || libraryReq.response.value?.results || libraryReq.response.value || []);
const showLibraryField = computed(() => Boolean(role.value) && !['MEMBER', 'SUPER ADMIN'].includes(role.value));
const roleOptions = ['MEMBER', 'STACK STAFF', 'TECHNICAL STAFF', 'FRONT DESK STAFF', 'ADMIN', 'SUPER ADMIN'];
const departments = [
  'Biology',
  'Chemistry',
  'Physics',
  'Mathematics',
  'Statistics',
  'Civil Engineering',
  'Mechanical Engineering',
  'Electrical & Computer Engineering',
  'Software Engineering',
  'Information Technology',
  'Computer Science',
  'Architecture',
  'Agronomy',
  'Animal Science',
  'Plant Science',
  'Nursing',
  'Public Health',
  'Medicine',
  'Pharmacy',
  'Economics',
  'Sociology',
  'Political Science',
  'History',
  'Geography',
  'Law',
  'Business Administration',
  'Accounting & Finance',
  'Management',
  'Education',
  'Journalism & Communication',
  'Other'
];
// Submit handler
function create({ values }) {
  if (values.role === 'MEMBER') {
    delete values.library;
  }
  if (values.role !== 'MEMBER') {
    delete values.user_type;
    delete values.department;
  }

  req.send(
    () => CreateUser(values),
    (res) => {
      if (res.success) {
        user.add(res.data);
        emitEntityMutation('users', { action: 'created', id: res.data?.id });
        toasted(true, 'User Created');
        closeModal();
      } else {
        toasted(false, '', res.error);
      }
    }
  );
}
</script>

<template>
  <div class="bg-black/50 min-h-full text-black p-4 sm:p-6 md:p-10 grid place-items-center">
    <NewFormParent title="Add User" size="2xl">
      <Form :inner="false" id="addform"
        class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 p-4 sm:p-6">
        
        <Input name="id_number" validation="required|numeric" label="ID Number" :attributes="{ placeholder: 'Enter ID Number'}" />

        <Input name="email" validation="required|email" label="Email" :attributes="{ placeholder: 'Enter User Email' }" />
        
        <InputPassword name="password" label="Password" validation="required|pass"
          :attributes="{ placeholder: 'Password' }" />
        
        <Input name="first_name" validation="required|alpha" label="First Name"
          :attributes="{ placeholder: 'Enter First Name' }" />
        
        <Input name="last_name" validation="required|alpha" label="Last Name"
          :attributes="{ placeholder: 'Enter Last Name' }" />
        
        <!-- <Input name="grandFatherName" validation="required|alpha" label="Grandfather Name"
          :attributes="{ placeholder: 'Enter Grandfather Name' }" />-->

        <Input name="phone" label="Mobile Phone" validation="required|phone" 
          :attributes="{ placeholder: 'Enter Mobile Phone' }" />

        <Select
          v-if="showLibraryField"
          :obj="true"
          name="library"
          label="Library"
          validation="required"
          :options="libraryOptions.map((library) => ({
            label: library?.name,
            value: library?.id,
          }))"
          :attributes="{ placeholder: 'Select Library', required: true }"
        />
       
             <Select v-model="role" name="role" label="Role" validation="required"
          :options="roleOptions"
          :attributes="{ placeholder: 'Select Role', required: true }" />
            <Select v-if="role=='MEMBER'" name="user_type" label="User Type" validation="required"
          :options="['TEACHER', 'STUDENT']"
          :attributes="{ placeholder: 'Select User Type', required: true }" />
        <!-- <Select :obj="true" name="roleUuid" label="Role" validation="required"
          :options="(rolereq.response.value?.roles?.content || []).map(role => ({
            label: role.roleName,
            value: role.roleUuid,
          }))"
          :attributes="{ placeholder: 'Select Role',
            required
           }" /> -->
           <Select v-if="role === 'MEMBER'" name="department" label="Department" validation="required"
          :options="departments"
          :attributes="{ placeholder: 'Select Department' }" />
      </Form>

      <template #bottom>
        <div class="p-4">
          <Button type="secondary" :pending="req.pending.value" @click.prevent="submit(create)" class="w-full">
            Add User
          </Button>
        </div>
      </template>
    </NewFormParent>
  </div>
</template>
