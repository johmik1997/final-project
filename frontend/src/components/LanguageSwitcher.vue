<script setup>
import { computed } from "vue";
import { useI18n } from "@/i18n";

const props = defineProps({
  compact: {
    type: Boolean,
    default: false,
  },
});

const { locale, locales, setLocale } = useI18n();

const selectedLocale = computed({
  get: () => locale.value,
  set: (value) => setLocale(value),
});
</script>

<template>
  <label
    class="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-white/95 px-3 py-2 text-sm font-medium text-slate-700 shadow-sm backdrop-blur"
    :class="compact ? 'pr-2' : 'pr-3'"
  >
    <span class="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">
      {{ compact ? "Lang" : "Language" }}
    </span>
    <select
      v-model="selectedLocale"
      class="rounded-xl border border-slate-200 bg-white px-3 py-1.5 text-sm text-slate-700 outline-none transition focus:border-primary focus:ring-4 focus:ring-primary/10"
    >
      <option v-for="option in locales" :key="option.code" :value="option.code">
        {{ option.label }}
      </option>
    </select>
  </label>
</template>
