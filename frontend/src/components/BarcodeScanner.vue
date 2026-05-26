<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { Html5Qrcode } from 'html5-qrcode';

const props = defineProps({
  active: { type: Boolean, default: false },
});

const emit = defineEmits(['scan', 'error']);

const scannerId = `barcode-scanner-${Math.random().toString(36).slice(2, 9)}`;
const isStarting = ref(false);
const scannerError = ref('');
let scanner = null;

async function stopScanner() {
  if (!scanner) return;
  try {
    const state = await scanner.getState();
    if (state === 2) {
      await scanner.stop();
    }
    await scanner.clear();
  } catch {
    // ignore cleanup errors
  }
  scanner = null;
}

async function startScanner() {
  scannerError.value = '';
  await stopScanner();
  if (!props.active) return;

  isStarting.value = true;
  try {
    scanner = new Html5Qrcode(scannerId);
    await scanner.start(
      { facingMode: 'environment' },
      { fps: 10, qrbox: { width: 260, height: 120 }, aspectRatio: 1.6 },
      (decodedText) => {
        const code = String(decodedText || '').trim();
        if (!code) return;
        emit('scan', code);
        stopScanner();
      },
      () => {}
    );
  } catch (error) {
    scannerError.value = error?.message || 'Unable to access camera for barcode scanning.';
    emit('error', scannerError.value);
  } finally {
    isStarting.value = false;
  }
}

watch(
  () => props.active,
  (active) => {
    if (active) {
      startScanner();
    } else {
      stopScanner();
    }
  }
);

onMounted(() => {
  if (props.active) {
    startScanner();
  }
});

onBeforeUnmount(() => {
  stopScanner();
});
</script>

<template>
  <div v-if="active" class="barcode-scanner">
    <div :id="scannerId" class="scanner-viewport" />
    <p v-if="isStarting" class="scanner-hint">Starting camera...</p>
    <p v-else-if="scannerError" class="scanner-error">{{ scannerError }}</p>
    <p v-else class="scanner-hint">Point the camera at a material barcode</p>
  </div>
</template>

<style scoped>
.barcode-scanner {
  border-radius: 0.85rem;
  border: 1px dashed #f59e0b;
  background: #fffbeb;
  padding: 0.75rem;
  overflow: hidden;
}

.scanner-viewport {
  width: 100%;
  min-height: 200px;
  border-radius: 0.65rem;
  overflow: hidden;
  background: #0f172a;
}

.scanner-hint {
  margin: 0.5rem 0 0;
  font-size: 0.8rem;
  color: #92400e;
  text-align: center;
}

.scanner-error {
  margin: 0.5rem 0 0;
  font-size: 0.8rem;
  color: #b91c1c;
  text-align: center;
}
</style>
