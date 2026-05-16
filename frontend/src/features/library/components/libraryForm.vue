<script setup>
import Input from '@/components/new_form_elements/Input.vue';
import Form from '@/components/new_form_builder/Form.vue';
import Select from '@/components/new_form_elements/Select.vue'

const { library, formId } = defineProps({
  library: {
    type: Object,
    default: () => ({}),
  },
  formId: {
    type: String,
    default: 'libraryForm',
  },
});
</script>

<template>
  <Form class="grid grid-cols-1 gap-5 md:grid-cols-2 text-black" :id="formId" :inner="false">
    <Input
      name="name"
      validation="required"
      label="Library Name"
      :value="library?.name || ''"
      :attributes="{ placeholder: 'Enter Library Name' }"
    />

    <!-- <Input
      name="campus"
      validation="required"
      label="Campus Name"
      :value="library?.campus || ''"
      :attributes="{ placeholder: 'Enter Campus Name' }"
    /> -->
  
    
    <Select
    v-model="campus"
  name="campus"
  label="Campus"
  validation="required"
  :options="[
    'Main Campus',
    'Agriculture Campus',
    'Wondo Genet Campus',
    'Technology Campus',
    'Hawassa Referral Campus',
    'Awada Campus',
    'Yirgalem Campus'
  ]"
  :attributes="{
    placeholder: 'Select Campus'
  }"
/>

    <Input
      name="location"
      validation="required"
      label="Location"
      :value="library?.location || ''"
      :attributes="{ placeholder: 'Enter Physical Location' }"
    />

    <Input
      name="phone"
      validation="required|phone"
      label="Contact Phone"
      :value="library?.phone || ''"
      :attributes="{ placeholder: 'Enter Phone Number', type: 'tel' }"
    />
  </Form>
</template>
