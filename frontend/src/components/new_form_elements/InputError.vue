<script setup>
	const props = defineProps(['error'])
</script>
<template>
	<p v-if='error' :title='error' class="capitalize px-1 text-xs text-red-700">
		{{error}}
	</p>
</template>