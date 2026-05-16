<script setup>
import { closeModal } from '@customizer/modal-x';

const props = defineProps({
  size: {
    type: String,
    default: 'md',
  },
  title: {
    required: true,
    type: String,
  },
  goBack: {
    type: Boolean,
    default: false,
  },
  onGoBack: {
    type: Function,
  },
  error: {
    type: String,
  },
});
</script>
<template>
  <div
    :class="[$style[size]]"
    class="overflow-hidden flex flex-col justify-between rounded-3xl border border-gray-200 bg-white/95 shadow-2xl backdrop-blur-xl dark:border-slate-700 dark:bg-slate-900/95"
  >
    <div class="flex items-center justify-between border-b border-gray-200 px-5 py-4 dark:border-slate-700">
      <div class="flex min-w-0 items-center gap-3">
        <button
          v-if="goBack"
          @click="onGoBack"
          class="grid h-10 w-10 place-items-center rounded-xl border border-gray-200 text-slate-700 transition-colors hover:bg-gray-50 dark:border-slate-700 dark:text-slate-200 dark:hover:bg-slate-800"
        >
          <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
          </svg>
        </button>

        <slot name="header-icon" />

        <div class="min-w-0">
          <slot name="title">
            <p class="truncate text-lg font-bold text-slate-900 dark:text-white">{{ title }}</p>
          </slot>
        </div>
      </div>

      <div class="flex items-center gap-3">
        <slot name="right-actions">
          <button
            @click="closeModal()"
            class="grid h-10 w-10 place-items-center rounded-xl border border-gray-200 text-slate-600 transition-colors hover:bg-gray-50 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
            aria-label="Close"
            title="Close"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </slot>
      </div>
    </div>

    <div class="form-scrollbar flex flex-1 flex-col gap-4 overflow-auto border-b border-gray-200 bg-gradient-to-br from-white via-amber-50/30 to-orange-50/20 p-4 dark:border-slate-700 dark:from-slate-900 dark:via-slate-900 dark:to-slate-950">
      <slot />
    </div>

    <slot name="bottom" />
  </div>
</template>

<style module>
.md {
  width: 100%;
  max-width: 44rem;
  max-height: 92vh;
}

.lg {
  width: 100%;
  max-width: 60rem;
  max-height: 92vh;
}

.xl {
  width: 100%;
  max-width: 72rem;
  max-height: 94vh;
}

.xs {
  width: 100%;
  max-width: 28rem;
  max-height: 88vh;
}
</style>

<style>
.form-layout {
  display: grid;
}

.form-scrollbar::-webkit-scrollbar {
  display: block;
  width: 6px;
}

.form-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(245, 158, 11, 0.35);
  border-radius: 999px;
}
</style>
