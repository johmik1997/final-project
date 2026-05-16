<script setup>
import { nextTick, ref } from "vue";
import { OnClickOutside } from "@vueuse/components";
import NewInputLayout from "./NewInputLayout.vue";
import InputParent from "../new_form_builder/InputParent.vue";

const props = defineProps({
  label: {
    type: String,
  },
  options: {
    type: Array,
    default: [],
  },
  value: {
    type: Array,
  },
});

const selected = ref(props.value || []);
const selectedPrivileges = ref({});

if (props.value.length) {
  props.value.forEach((val) => {
    selectedPrivileges.value[val.privilege] =
      props.options?.find((op) => op.privilege == val.privilege)?.methods || [];
  });
}

function add(option, emit) {
  if (!selected.value.find((sel) => sel?.privilege == option?.privilege)) {
    selected.value.push({ privilege: option?.privilege, actions: [] });
    selectedPrivileges.value[option.privilege] = option?.methods;
    nextTick(() => {
      emit(selected.value);
    });
  }
}

function remove(option, emit) {
  selected.value = selected.value.filter(
    (el) => el?.privilege != option?.privilege
  );
  delete selectedPrivileges.value[option.privilege];
  emit(selected.value);
}

function toggleMethod(privilege, method, emit) {
  const idx = selected.value.findIndex((pri) => pri.privilege == privilege);

  if (idx == -1) return;

  const found = selected.value[idx].actions.findIndex((act) => act == method);

  if (found == -1) {
    selected.value[idx].actions.push(method);
  } else {
    selected.value[idx].actions.splice(found, 1);
  }

  emit(selected.value);
}

const open = ref(false);

console.log(props.options, props.value);
</script>

<template>
  <InputParent v-model="selected" v-slot="{ setRef, error, attrs, emit }">
    <NewInputLayout
      :class="attrs?.class"
      class="h-auto overflow-visible"
      :label="label"
      :error="error"
    >
      <div
        @keydown.enter="open = !open"
        tabindex="0"
        @click="open = !open"
        class="relative w-full flex"
        :ref="setRef"
      >
        <p v-if="!selected.length" class="h-full p-2">
          {{
            $attrs.placeholder ? $attrs.placeholder : "select multiple options"
          }}
        </p>
        <div v-else class="p-2 w-full h-full flex-wrap gap-2 flex items-center">
          <div
            class="h-14 flex-shrink-0 overflow-hidden text-xs flex items-center rounded-md bg-primary/30"
            :key="selecte"
            v-for="selecte in selected"
          >
            <div class="p-3 flex flex-col gap-1">
              <p class="text-base">{{ selecte?.privilege }}</p>
              <div class="flex gap-2">
                <div
                  @click="toggleMethod(selecte?.privilege, action, emit)"
                  :class="[
                    selecte?.actions.includes(action)
                      ? 'bg-primary text-white'
                      : 'border border-gray-400',
                  ]"
                  class="rounded-md px-2 text-xs rounded-m uppercase"
                  :key="action"
                  v-for="action in selectedPrivileges[selecte?.privilege]"
                >
                  {{ action }}
                </div>
              </div>
            </div>
            <button
              @click.prevent="
                () => {
                  remove(selecte, emit);
                }
              "
              class="bg-gray-700 text-white h-full w-6"
            >
              <h-icon name="fa-times" scale=".7" />
            </button>
          </div>
        </div>
        <slot name="right" />
        <OnClickOutside
          :class="[open ? 'block' : 'hidden']"
          @trigger="open = false"
        >
          <div
            class="absolute left-0 top-[110%] border rounded-md cursor-pointer w-full z-20 bg-white p-2"
          >
            <div
              @keydown.enter.prevent="() => add(option, emit)"
              class="focus:border focus:border-primary"
              tabindex="0"
              @click.prevent.stop="
                () => {
                  add(option, emit);
                }
              "
              :value="option"
              v-for="option in options"
            >
              {{ option?.privilege }}
            </div>
          </div>
        </OnClickOutside>
      </div>
    </NewInputLayout>
  </InputParent>
</template>
