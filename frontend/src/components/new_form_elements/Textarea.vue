<script setup>
import InputParent from "../new_form_builder/InputParent.vue";
import InputLayout from "@/components/new_form_elements/NewInputLayout.vue";
</script>

<template>
  <InputParent v-slot="{ setRef, error, validation }">
    <InputLayout
      :class="$attrs?.class"
      :label="$attrs.label"
      :error="error"
      :validation="validation"
    >
      <div class="input-wrapper">
        <textarea
          :ref="setRef"
          class="custom-input"
        />
        <slot name="right" />
      </div>
    </InputLayout>
  </InputParent>
</template>

