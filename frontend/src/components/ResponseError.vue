<script setup lang="ts">
import { inject, watch } from 'vue';

	const props = defineProps(['error'])

	const formError = inject('formError', '')
</script>
<template>
	<p v-if='error || formError' class="text-left whitespace-normal border-l-4 w-full bg-yellow-300 text-error-text border-error-border bg-error-bg px-2 py-1 text-sm">
		{{error || formError}}
	</p>
</template>