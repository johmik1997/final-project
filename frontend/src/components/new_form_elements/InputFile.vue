<script setup>
import InputParent from "../new_form_builder/InputParent.vue";
import InputLayout from "./NewInputLayout.vue";
import { watch, ref } from "vue";

const props = defineProps({
  modelValue: {
    required: false,
  },
  attributes: {
    type: Object,
  },
});
const emit = defineEmits(["update:modelValue"]);
const file = ref(props.modelValue || "");

watch(file, () => {
  emit("update:modelValue", file.value);
});
</script>
<template>
  <InputParent
    v-model="file"
    :attributes="{ ...attributes, type: 'file' }"
    v-slot="{ setRef, error, value, changeValue }"
  >
    <InputLayout :error="error" :label="$attrs?.label">
      <div class="flex gap-4 items-center">
        <label
          class="flex-1 cursor-pointer flex items-center h-full bg-secondary px-2 rounded"
        >
          <div class="size-8 grid place-items-center">
            <!--<img src="@/assets/img/ArrowAction.svg" />-->
            <!-- <BaseIcon :size="20" :path="mdiAttachment" /> -->
          </div>
          <p :class="[!value?.name ? 'text-white font-bold' : '']">
            {{ value?.name || attributes?.placeholder }}
          </p>
          <input class="hidden" :ref="setRef" />
        </label>
      </div>
    </InputLayout>
  </InputParent>
</template>

<style></style>
