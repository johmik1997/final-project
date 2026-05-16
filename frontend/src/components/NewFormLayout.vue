<script setup>
import { Form } from "./new_form_builder";
const props = defineProps({
  id: {
    type: String,
    required: true,
  },
  inner: {
    type: Boolean,
    default: true,
  },
  childrenName: {
    type: String,
  },
});
</script>
<template>
  <Form
    :childrenName="childrenName"
    :id="id"
    :inner="inner"
    v-slot="form"
    class="grid grid-cols-1 grid-flow-row gap-6"
  >
    <slot v-bind="form" />
  </Form>
</template>
