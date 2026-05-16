<script setup>
import InputError from '@/components/new_form_elements/InputError.vue';
import InputParent from '@/components/new_form_builder/InputParent.vue';
import { computed, ref, watch } from 'vue';

const props = defineProps({
  label: String,
  value: String,
  options: {
    type: Array,
    required: true,
  },
  selectedPrivilege: {
    type: Array,
  },
  validation: String,
});

const selected = ref([]);

const group = computed(() => {
  return props?.options.reduce((acc, el) => {
    const category = el.privilegeCategory || 'Uncategorized';
    if (!acc[category]) {
      acc[category] = [];
    }
    acc[category].push(el);
    return acc;
  }, {});
});

watch(
  () => props.selectedPrivilege,
  (newPrivileges) => {
    if (!Array.isArray(newPrivileges)) {
      selected.value = [];
      return;
    }
    selected.value = newPrivileges
      .filter((el) => el.privilegeUuid)
      .map((el) => el.privilegeUuid);
  },
  { immediate: true }
);

function toggle(id) {
  const idx = selected.value.indexOf(id);
  if (idx === -1) {
    selected.value.push(id);
  } else {
    selected.value.splice(idx, 1);
  }
}

const isChecked = computed(() => {
  return (id) => selected.value.includes(id);
});

const isAllChecked = computed(() => {
  return (category) =>
    group.value[category].every((el) => selected.value.includes(el.privilegeUuid));
});

function selectAll(checked, category) {
  const ids = group.value[category].map((el) => el.privilegeUuid);
  if (checked) {
    selected.value = [...new Set([...selected.value, ...ids])];
  } else {
    selected.value = selected.value.filter((id) => !ids.includes(id));
  }
}
</script>

<template>
  <InputParent :validation="validation" v-model="selected" v-slot="{ setRef, error }">
    <div :ref="setRef" class="flex flex-col gap-3">
      <!-- Label and error -->
      <div class="flex items-center justify-between gap-2 border-b pb-2">
        <span
          v-if="label"
          class="text-sm font-medium truncate"
          :data-required="`${validation}`.includes('required') ? 'true' : 'false'"
        >
          {{ label }}
        </span>
        <InputError :error="error" />
      </div>

      <!-- Privilege Groups -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div
          v-for="category in Object.keys(group)"
          :key="category"
          class="border rounded-md p-3"
        >
          <!-- Category Header with Select All -->
          <div class="flex items-center gap-2 border-b pb-2 mb-2">
            <input
              type="checkbox"
              class="size-4 accent-primary"
              :checked="isAllChecked(category)"
              @change="(e) => selectAll(e.target.checked, category)"
            />
            <p class="font-semibold text-sm truncate">{{ category }}</p>
          </div>

          <!-- Privileges in Category -->
          <div
            v-for="privilege in group[category]"
            :key="privilege.privilegeUuid"
            class="flex items-center gap-2 py-1"
          >
            <input
              type="checkbox"
              class="size-4 accent-primary"
              :checked="isChecked(privilege.privilegeUuid)"
              @change="() => toggle(privilege.privilegeUuid)"
            />
            <p class="text-xs truncate">{{ privilege.privilegeName }}</p>
          </div>
        </div>
      </div>
    </div>
  </InputParent>
</template>
