<script setup>
import Input from '@/components/new_form_elements/Input.vue'
import Select from '@/components/new_form_elements/Select.vue'
import Form from '@/components/new_form_builder/Form.vue'
import { computed, ref, watch } from 'vue'

const props = defineProps({
  user: {
    type: Object,
    required: true
  },
  libraries: {
    type: Array,
    default: () => []
  }
})

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

const role = ref('')
const showLibraryField = computed(() => Boolean(role.value) && !['MEMBER', 'SUPER ADMIN'].includes(role.value))
const roleOptions = [
  'MEMBER',
  'STACK STAFF',
  'TECHNICAL STAFF',
  'FRONT DESK STAFF',
  'ADMIN',
  'SUPER ADMIN'
]

watch(
  () => props.user,
  (val) => {
    role.value = val?.role || val?.roleName || ''
  },
  { immediate: true }
)
</script>

<template>
  <Form
    class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 p-4 sm:p-6"
    id="userform"
    :inner="false"
  >

    <Input
      name="id_number"
      validation="required|numeric"
      label="ID Number"
      :value="user?.id_number || ''"
      :attributes="{ placeholder: 'Enter ID Number' }"
    />

    <Input
      name="email"
      validation="required|email"
      label="Email"
      :value="user?.email || ''"
      :attributes="{ placeholder: 'Enter Email' }"
    />

    <Input
      name="first_name"
      validation="required|alpha"
      label="First Name"
      :value="user?.first_name || user?.firstName || ''"
      :attributes="{ placeholder: 'Enter First Name' }"
    />

    <Input
      name="last_name"
      validation="required|alpha"
      label="Last Name"
      :value="user?.last_name || user?.lastName || ''"
      :attributes="{ placeholder: 'Enter Last Name' }"
    />

    <Input
      name="phone"
      validation="required"
      label="Mobile Phone"
      :value="user?.phone || user?.mobilePhone || ''"
      :attributes="{ placeholder: 'Enter Mobile Phone' }"
    />

    <Select
      v-if="showLibraryField"
      :obj="true"
      name="library"
      label="Library"
      validation="required"
      :value="user?.library_id || user?.library || ''"
      :options="libraries.map((library) => ({ label: library?.name, value: library?.id }))"
      :attributes="{ placeholder: 'Select Library', required: true }"
    />

    <Select
      v-model="role"
      name="role"
      label="Role"
      validation="required"
      :options="roleOptions"
      :attributes="{ placeholder: 'Select Role' }"
    />

    <Select
      v-if="role === 'MEMBER'"
      name="user_type"
      label="User Type"
      validation="required"
      :value="user?.user_type || ''"
      :options="['TEACHER','STUDENT']"
    />

    <Select
      v-if="role === 'MEMBER'"
      name="department"
      label="Department"
      validation="required"
      :value="user?.department || ''"
      :options="departments"
      :attributes="{ placeholder: 'Select Department' }"
    />

  </Form>
</template>
