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

const role = ref('')
const libraryRequired = computed(() => role.value !== 'MEMBER' && role.value !== 'SUPER ADMIN')

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
      :obj="true"
      name="library"
      label="Library"
      :validation="libraryRequired ? 'required' : ''"
      :value="user?.library_id || user?.library || ''"
      :options="libraries.map((library) => ({ label: library?.name, value: library?.id }))"
      :attributes="{ placeholder: libraryRequired ? 'Select Library' : 'Select Library (optional)', required: libraryRequired }"
    />

    <Select
      v-model="role"
      name="role"
      label="Role"
      validation="required"
      :options="[
        'MEMBER',
        'STACK STAFF',
        'TECHNICAL STAFF',
        'FRONT DESK STAFF',
        'ADMIN',
        'SUPER ADMIN'
      ]"
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

    <Input
      v-if="role === 'MEMBER'"
      name="department"
      label="Department"
      validation="required"
      :value="user?.department || ''"
      :attributes="{ placeholder: 'Enter Department' }"
    />

  </Form>
</template>
