<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useToast } from "./store/toast.js";
import icons from '@/utils/icons.js';
//import { mdiClose } from '@mdi/js'
const { removeToast } = useToast()
const props = defineProps({
  toast: {
    type: Object
  },
  id: String
})

const t = ref()

let timeout: any

function removeT() {
  clearTimeout(timeout)
  if(t.value) {
    t.value.classList.remove('enter')
    t.value.classList.add('leave')
    t.value.onanimationend = (() => {
      props?.id && removeToast(props?.id)
    })
  } else {
    props?.id && removeToast(props?.id)
  }
}

onMounted(() => {
  timeout = setTimeout(() => props.id && removeT(), 6000)
})

onMounted(() => {
  if(t.value) {
    t.value.style.setProperty("--height", t.value.offsetHeight + 'px')
    t.value.classList.add('enter')
  }
})

function stay() {
  clearTimeout(timeout)
}

function out() {
  timeout = setTimeout(() => props.id && removeT(), 6000)
}
</script>

<template>
  <div @mouseout="out" @mouseover="stay" ref="t" @click="removeT" :class="[$style[toast?.type || 'error']]"
    class="relative rounded-md max-w-[50%] flex items-center p-4 gap-3 text-base shadow-md min-w-72 justify-between">
    <p class="text-sm">{{ toast?.message }}</p>
    <button class="min-w-4 min-h-4 flex-shrink-0 bg-dark/20 shadow-md rounded-full text-base-clr2 right-0 top-0 w-8 h-8 flex items-center justify-center self-start">
      <span v-html="icons.close" />
    </button>
  </div>
</template>

<style module>
/* .toast-item {
  --color: 
} */
.error {
  @apply bg-yellow-200  border-l-4 border-red-500;
}

.success {
  @apply bg-secondary text-white;
}
</style>

<style>

.leave {
  animation: leave .2s linear;
  animation: "leave" .2s linear;
}

.enter {
  animation: enter .2s linear;
  animation: "enter" .2s linear normal;
}

@keyframes enter {
  0% {
    opacity: 0;
    height: 0;
    transform: translateX(-15rem);
    overflow: hidden;
  }

  100% {
    opacity: 1;
    height: var(--height);
    transform: translateX(0rem);
  }
}

@keyframes leave {
  0% {
    opacity: 1;
    height: var(--height);
    transform: translateX(0rem);
  }

  100% {
    opacity: 0;
    height: 0;
    transform: translateX(-13rem);
    overflow: hidden;
  }
}
</style>