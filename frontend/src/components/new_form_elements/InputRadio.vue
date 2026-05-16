<script setup>
import InputParent from "../../new_form_builder/InputParent.vue";
import { ref, watch } from "vue";

const props = defineProps({
  name: {
    type: String,
    required: true,
  },
  options: {
    type: Array,
    required: true,
  },
});
</script>

<template>
  <InputParent
    :name="name"
    v-slot="{ error, setRef, value, changeValue }"
  >
    <p>{{ error }}</p>
    <div :ref="setRef">
      <input
        :checked="value == option"
        @change="(ev) => changeValue(option)"
        :key="option"
        v-for="option in options"
        :name="name"
        type="radio"
        :value="option"
      />
    </div>
  </InputParent>
</template>
