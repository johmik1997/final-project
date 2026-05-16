<script setup>
import { shallowRef, computed } from "vue";

const props = defineProps({
  pages: {
    type: Array,
    required: true,
  },
  transitionName: {
    type: String,
    default: 'page'
  },
  baseAnimation: {
    type: Boolean,
    default: true
  }
});

const pages = shallowRef(props.pages.filter((el) => !el.base));
const active = shallowRef(props.pages.find((el) => el.active)?.component);
const basePage = shallowRef(
  props.pages.find((el) => el.base) || props.pages.at(0)
);

const routes = shallowRef([basePage.value?.component]);

function goTo(name) {
  const res = pages.value.find((el) => el.name == name)?.component;
  if (res && res != active.value) {
    active.value = res;
  } else {
    active.value = basePage.value?.component;
  }
  routes.value.unshift(active.value);
}

function goBack() {
  if (routes.value.length == 1) return;
  if (routes.value?.length == 2) {
    routes.value.shift();
    active.value = "";
  } else {
    active.value = routes.value.at(1);
    routes.value.shift();
  }
}

const activeProps = computed(() => {
  return pages.value.find((el) => el.component == active.value)?.props;
});
</script>
<template>
  <div class="h-full w-full relative overflow-hidden">
    <component
      :class="[active && baseAnimation && '__base_hide']"
      class="__base_show"
      v-bind="basePage?.props || {}"
      :goBack="goBack"
      :goTo="goTo"
      :is="basePage?.component"
    />
    <Transition :name="transitionName">
      <component
        v-if="active"
        :is="active"
        v-bind="activeProps || {}"
        class="absolute inset-0"
        :goBack="goBack"
        :goTo="goTo"
      />
    </Transition>
  </div>
</template>

<style scoped>
.page-enter-active,
.page-leave-active {
  transition: transform 0.2s ease;
  z-index: 10;
}

.page-enter-from,
.page-leave-to {
  transform: translate(100%, 0);
}
.page{
  position: absolute;
  inset: 0;
}

.__base_show {
  transform: translate(0rem, 0);
  transition: transform 0.2s linear;
}

.__base_hide {
  transform: translate(-6rem, 0) !important;
}
</style>
