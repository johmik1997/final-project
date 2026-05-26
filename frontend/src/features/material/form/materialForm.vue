<script setup>
import Form from '@/components/new_form_builder/Form.vue';
import Input from '@/components/new_form_elements/Input.vue';
import Select from '@/components/new_form_elements/Select.vue';

const props = defineProps({
  initialData: {
    type: Object,
    default: () => ({}),
  },
  libraries: {
    type: Array,
    default: () => [],
  },
});
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
function toDateInputValue(value) {
  if (!value) return '';
  if (typeof value === 'string') return value.slice(0, 10);

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  return date.toISOString().slice(0, 10);
}
</script>

<template>
  <Form id="materialform" :inner="false" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 p-4 sm:p-6">
    <Input name="title" label="Title" validation="required" :value="initialData?.title || ''" />
    <Input name="author" label="Author" validation="required" :value="initialData?.author || ''" />
    <Input name="isbn" label="ISBN" :value="initialData?.isbn || ''" />

    <Select
      name="category"
      label="Category"
      validation="required"
      :value="initialData?.category || ''"
      :options="['BOOK', 'MAGAZINE', 'RESEARCH PAPER', 'JOURNALS', 'THESIS']"
      :attributes="{ placeholder: 'Select Category' }"
    />

    <Select
      name="genre"
      label="Genre"
      validation="required"
      :value="initialData?.genre || ''"
       :options="['SCIENCE', 'FICTION', 'HISTORY', 'BIOGRAPHY','TECHNOLOGY','EDUCATIONAL', 'OTHER']"
      :attributes="{ placeholder: 'Select Genre' }"
    />

    <Input name="language" label="Language" :value="initialData?.language || ''" />
    <Input name="published_date" type="date" label="Published Date" :value="toDateInputValue(initialData?.published_date)" />
    <Select
      name="department"
      label="Department"
      validation="required"
      :value="initialData?.department || ''"
      :options="departments"
      :attributes="{ placeholder: 'Select Department' }"
    />
    <Input name="location" label="Library Location" :value="initialData?.location || ''" />

    <Select
      :obj="true"
      name="library"
      label="Owning Library"
      validation="required"
      :value="initialData?.library || initialData?.library_id || ''"
      :options="libraries.map((library) => ({ label: library?.name, value: library?.id }))"
      :attributes="{ placeholder: 'Select Library' }"
    />

    <Input name="total_copies" type="number" label="Total Copies" validation="required|numeric" :value="initialData?.total_copies ?? ''" />
    <Input name="price" type="number" label="Price" :value="initialData?.price ?? ''" :attributes="{ step: '0.01' }" />
    <Input name="image" type="file" label="Material Image (Optional)" :attributes="{ accept: '.jpg,.jpeg,.png,.webp,.gif' }" />

    <Select
      name="condition"
      label="Condition"
      validation="required"
      :value="initialData?.condition || ''"
     :options="['NEW', 'GOOD', 'FAIR', 'DAMAGED']"
      :attributes="{ placeholder: 'Select Condition' }"
    />

    <Select
      name="can_borrow"
      label="Can be Borrowed?"
      validation="required"
      :value="initialData?.can_borrow === true ? 'Yes' : initialData?.can_borrow === false ? 'No' : ''"
      :options="['Yes', 'No']"
      :attributes="{ placeholder: 'Select Status' }"
    />
  </Form>
</template>
