<script setup>
import Input from '@/components/new_form_elements/Input.vue';
import Privilages from '../../privilages/pages/Privileges.vue';
import Textarea from '@/components/new_form_elements/Textarea.vue';
import Form from '@/components/new_form_builder/Form.vue';
import SelectPrivilegeInput from '../components/SelectPrivilegeInput.vue';

const props = defineProps({
  roles: {
    type: Object,
  },
  privileges: {
    type: Array,
    required: true,
  },
  selectPrivilege: {
    type: Array,
  },
});

console.log(props.selectPrivilege);
</script>

<template>
  <Form
    class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 p-4 sm:p-6"
    :inner="false"
    id="roleForm"
  >
    <!-- Role Name -->
    <Input
      name="roleName"
      validation="required|alpha"
      label="Role Name"
      :value="roles?.roleName || ''"
      :attributes="{
        placeholder: 'Enter Role Name',
      }"
    />

    <!-- Role Description -->
    <Textarea
      validation="required"
      name="roleDescription"
      :value="roles?.roleDescription || ''"
      label="Role Description"
      :attributes="{
        placeholder: 'Enter Role Description',
      }"
    />

    <!-- Select Privileges (Full width) -->
    <div class="sm:col-span-2 lg:col-span-3">
      <SelectPrivilegeInput
        label="Select Privileges"
        validation="required"
        name="privileges"
        :options="privileges"
        :selectedPrivilege="selectPrivilege || []"
      />
    </div>
  </Form>
</template>
