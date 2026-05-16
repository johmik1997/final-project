<script setup>
import { ref } from "vue";
import Input from "./Input.vue";
import icons from "@/utils/icons";

const props = defineProps({
  attributes: {
    type: Object,
  },
});

const text = ref(props.attributes?.type == "text" ? true : false);

function toggleType() {
  text.value = !text.value;
}
</script>

<template>
  <Input
    :attributes="{
      ...attributes,
      type: text ? 'text' : 'password',
    }"
  >
    <template #right>
      <div class="h-full w-12 grid place-items-center border-r">
        <i @click="toggleType" v-html="text ? icons.eyeClose : icons.eye" />
      </div>
    </template>
  </Input>
</template>
