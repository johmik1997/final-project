<script setup lang="ts">
import { useForm } from "./useForm";
import type { Ref } from 'vue';

const emit = defineEmits(['submit']);

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

if (!props.id) {
  throw new Error("[id] is required for a new form");
}

type Submit = (cb: Function) => void;

interface UseForm {
  formEl: Ref<HTMLElement | undefined>,
  submit: Submit,
  valid: Ref<boolean>,
  reset: () => void,
  id: string
}

const { formEl, submit, valid } = useForm(
  props.id,
  props.inner,
  props.childrenName
) as UseForm;

function onSubmit(e: Event) {
  e.preventDefault();
  if (typeof submit === 'function') {
    submit(({ values }) => {
      emit('submit', values);
    });
  }
}
</script>
<template>
  <form autocomplete="off" :id="id" ref="formEl" action="" @submit.prevent="onSubmit">
    <slot :valid="valid" :submit="submit"></slot>
  </form>
</template>
