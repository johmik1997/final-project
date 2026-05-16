<script setup>
const props = defineProps({
  rowData: {
    type: Array,
    required: true,
  },
  firstCol: {
    type: Boolean,
    default: false,
  },
  rowKeys: {
    type: Array,
    required: true,
  },
  headKeys: {
    type: Array,
    default: [],
  },
  cells: Object,
});
const emit = defineEmits(["row"]);
</script>
<template>
  <template :key="index" v-for="(row, index) in rowData">
    <slot name="top" :row="row" />
    <tr
      @click="emit('row', row)"
      class="odd:bg-base-clr hover:bg-base-clr text-sm cursor-pointer border-b-[0.2px]"
    >
      <td v-if="firstCol" class="p-3">
        <slot name="select" :row="row" />
      </td>
      <td class="p-2 opacity-80">{{ index + 1 }}</td>
      <td class="p-2 max-w-40 opacity-80" :key="key" v-for="key in rowKeys">
        <span class="text-sm" v-if="!Object.keys(cells || {}) || !cells?.[key]">
          {{
            key.split(".").reduce((all, el) => {
              return all?.[el];
            }, row)
          }}
        </span>
        <component
          v-else-if="Object.keys(cells || {}) && cells[key].com"
          :row="row"
          :is="cells[key].com"
          v-bind="
            Array.isArray(cells[key].props)
              ? cells[key].props.reduce((props, prop) => {
                  props[prop.name] = row[prop.value];
                  return props;
                }, {})
              : {}
          "
        />
        <span v-else-if="typeof cells[key] == 'function'">
          {{ cells[key](row?.[key], row) }}
        </span>
      </td>
      <td
        class="p-3"
        v-if="headKeys.find((head) => head.toLowerCase() == 'actions')"
      >
        <slot name="actions" :row="row" />
      </td>
    </tr>
    <slot name="bottom" :row="row" />
  </template>
</template>
