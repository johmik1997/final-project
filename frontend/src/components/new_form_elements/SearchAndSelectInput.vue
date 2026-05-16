<script setup>
import InputLayout from "@/components/new_form_elements/NewInputLayout.vue";
import { useApiRequest } from "@/composables/useApiRequest";
import { InputParent } from "@/new_form_builder";
import { computed, nextTick, onMounted, ref, watch } from "vue";
import { OnClickOutside } from "@vueuse/components";

const props = defineProps({
  modelValue: {
    required: false,
  },
  store: {
    type: Object,
  },
  value: {
    type: String,
  },
  onInput: {
    type: Function,
    required: true,
  },
  attributes: {
    type: Object,
  },
  toBeSelected: {
    type: String,
    default: "agencyName",
  },
  matchId: {
    type: String,
    default: "agencyUuid",
  },
});
const emit = defineEmits(["update:modelValue"]);

const agencyReq = useApiRequest();

const search = ref("");
const typedText = ref("");
const selected = ref(props.value || "");
const agencies = ref([]);

let controller;
let timeout;
function getAgency(ev) {
  if (timeout) {
    clearTimeout(timeout);
  }
  timeout = setTimeout(() => {
    if (controller) {
      controller.abort();
    }
    controller = new AbortController();

    agencyReq.send(
      () =>
        props.onInput(
          {
            search: ev.target.value,
          },
          {
            signal: controller.signal,
          }
        ),
      (res) => {
        if (res.success && Array.isArray(res.data)) {
          agencies.value = res.data;
          if (props.store && Array.isArray(res.data)) {
            props.store.set(res.data);
          }
        }

        openDropdown.value = true;
      },
      true
    );
  }, 200);
}

function select(agency) {
  selected.value = agency?.[props.matchId] || typedText.value.value;
  typedText.value.value = agency?.[props.toBeSelected] || typedText.value.value
  emit("update:modelValue", selected.value);
  openDropdown.value = false;
}

const openDropdown = ref(false);
onMounted(() => {
  typedText.value.value = props.value || "";
});
</script>
<template>
  <InputParent
    :attributes="attributes"
    v-model="selected"
    v-slot="{ setRef, value, error }"
  >
    <InputLayout v-bind="$attrs" :error="error">
      <div class="relative focus:border-0 w-full flex" :ref="setRef">
        <OnClickOutside class="flex-1" @trigger="openDropdown = false">
          <div class="flex h-full">
            <input
              @input="getAgency"
              ref="typedText"
              class="flex-1 placeholder:text-text-clr placeholder:opacity-60"
              :placeholder="attributes?.placeholder"
              name="search"
            />
            <div
              @click="openDropdown = !openDropdown"
              class="cursor-pointer h-full ml-auto w-8 flex items-center justify-center"
            >
              <h-icon name="fa-angle-down" />
            </div>
          </div>
          <div
            v-if="openDropdown || agencyReq.pending.value"
            class="absolute top-full mt-[1px] z-20 max-h-[15rem] overflow-auto rounded border-black bg-white border w-full left-0"
          >
            <p
              tabindex="0"
              v-if="openDropdown && !agencyReq.pending.value"
              @click="select(agency)"
              :key="agency?.[matchId]"
              v-for="agency in agencies"
              class="p-2 bg-white cursor-pointer"
            >
              {{ agency?.[toBeSelected] }}
            </p>
            <div
              v-if="agencyReq.pending.value"
              class="p-2 focus:bg-gray-400 bg-white grid place-items-center"
            >
              <h-icon name="fa-spinner" class="animate-spin" />
            </div>
            <div
              @click="
                () => {
                  selected = search;
                  emit('update:modelValue', selected);
                }
              "
              v-if="!agencyReq.response.value?.length && !agencyReq.pending.value"
              class="p-2 bg-white grid place-items-center"
            >
              <p
                @click.stop.prevent="
                  () => {
                    select()
                    emit('update:modelValue', search);
                  }
                "
                class="text-sm text-center italic"
              >
                no data found (click to select) {{ typedText.value }}
              </p>
            </div>
          </div>
        </OnClickOutside>
      </div>
    </InputLayout>
  </InputParent>
</template>
