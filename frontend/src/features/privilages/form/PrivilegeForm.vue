<script setup>
import { Form, Input } from '@/components/new_form_elements';

const props = defineProps({
  privilege: Object,
  onSubmit: Function,
});
</script>

<template>
  <Form
    class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mt-6 p-4 sm:p-6"
    :inner="false"
    id="privilegeForm"
    v-slot="{ }"
  >
    <!-- Privilege Name -->
    <Input
      name="privilegeName"
      validation="required"
      label="Privilege Name"
      :value="privilege?.privilegeName || ''"
      :attributes="{
        placeholder: 'Enter Privilege',
      }"
    />

    <!-- Privilege Description -->
    <Input
      validation="required|alpha"
      class="sm:col-span-2"
      name="privilegeDescription"
      :value="privilege?.privilegeDescription || ''"
      label="Privilege Description"
      :attributes="{
        placeholder: 'Enter Privilege description',
      }"
    />

    <!-- Privilege Category -->
    <Input
      :value="privilege?.privilegeCategory || ''"
      name="privilegeCategory"
      label="Privilege Category"
      validation="required|alpha"
      :attributes="{
        placeholder: 'Enter Privilege category',
      }"
    />
  </Form>
</template>
