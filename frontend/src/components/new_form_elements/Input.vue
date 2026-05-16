<script setup>
import { useAttrs } from "vue";
import InputParent from "../new_form_builder/InputParent.vue";
import InputLayout from "./NewInputLayout.vue";

const attrs = useAttrs();
</script>
<template>
  <InputParent v-slot="{ setRef, validation, error, value, changeValue }">
    <InputLayout :validation="validation" :error="error" :label="$attrs?.label">
      <div class="input-wrapper">
        <slot name="left" />
        <input :ref="setRef" :type="attrs.type || 'text'" />
        <slot name="right" />
      </div>
    </InputLayout>
  </InputParent>
</template>
