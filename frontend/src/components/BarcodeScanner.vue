<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { Html5Qrcode, Html5QrcodeSupportedFormats } from 'html5-qrcode';

const props = defineProps({
  active: { type: Boolean, default: false },
  /** Minimum ms between duplicate scan emissions */
  scanCooldownMs: { type: Number, default: 1500 },
  allowImageUpload: { type: Boolean, default: true },
  captureMode: { type: String, default: 'environment' },
});

const emit = defineEmits(['scan', 'error']);

const scannerId = `barcode-scanner-${Math.random().toString(36).slice(2, 9)}`;
const isStarting = ref(false);
const isScanningFile = ref(false);
const scannerError = ref('');
let scanner = null;
let lastScannedCode = '';
let lastScannedAt = 0;

const BARCODE_FORMATS = [
  Html5QrcodeSupportedFormats.CODE_128,
  Html5QrcodeSupportedFormats.CODE_39,
  Html5QrcodeSupportedFormats.CODE_93,
  Html5QrcodeSupportedFormats.EAN_13,
  Html5QrcodeSupportedFormats.EAN_8,
  Html5QrcodeSupportedFormats.UPC_A,
  Html5QrcodeSupportedFormats.UPC_E,
  Html5QrcodeSupportedFormats.ITF,
  Html5QrcodeSupportedFormats.QR_CODE,
];

function normalizeScannedCode(raw) {
  const text = String(raw || '').trim();
  if (!text) return '';

  const digitsOnly = text.replace(/\D/g, '');
  // ISBN-13 / ISBN-10 style barcodes
  if (digitsOnly.length === 10 || digitsOnly.length === 13) {
    return digitsOnly;
  }
  return text;
}

function shouldEmitScan(code) {
  const now = Date.now();
  if (code === lastScannedCode && now - lastScannedAt < props.scanCooldownMs) {
    return false;
  }
  lastScannedCode = code;
  lastScannedAt = now;
  return true;
}

function getScanBoxSize() {
  const width = Math.min(Math.max(window.innerWidth * 0.85, 280), 420);
  const height = Math.min(Math.max(width * 0.45, 100), 180);
  return { width: Math.round(width), height: Math.round(height) };
}

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

function getScannerInstance() {
  if (!scanner) {
    scanner = new Html5Qrcode(scannerId, { formatsToSupport: BARCODE_FORMATS });
  }
  return scanner;
}

async function startScanner() {
  scannerError.value = '';
  await stopScanner();
  if (!props.active) return;

  isStarting.value = true;
  try {
    const scanBox = getScanBoxSize();
    const reader = getScannerInstance();
    await reader.start(
      { facingMode: props.captureMode },
      {
        fps: 15,
        qrbox: scanBox,
        aspectRatio: 1.777,
        disableFlip: false,
        experimentalFeatures: {
          useBarCodeDetectorIfSupported: true,
        },
      },
      (decodedText) => {
        const code = normalizeScannedCode(decodedText);
        if (!code || !shouldEmitScan(code)) return;
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

async function handleImageSelection(event) {
  const file = event?.target?.files?.[0];
  if (!file) return;

  scannerError.value = '';
  isScanningFile.value = true;

  try {
    await stopScanner();
    const reader = getScannerInstance();
    const decodedText = await reader.scanFile(file, true);
    const code = normalizeScannedCode(decodedText);
    if (!code || !shouldEmitScan(code)) return;
    emit('scan', code);
    await stopScanner();
  } catch (error) {
    scannerError.value = error?.message || 'Unable to read a barcode from that image.';
    emit('error', scannerError.value);
    if (props.active) {
      await startScanner();
    }
  } finally {
    isScanningFile.value = false;
    if (event?.target) {
      event.target.value = '';
    }
  }
}

watch(
  () => props.active,
  (active) => {
    if (active) {
      lastScannedCode = '';
      lastScannedAt = 0;
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
    <div v-if="allowImageUpload" class="scanner-actions">
      <label class="scanner-upload">
        <input
          type="file"
          accept="image/*"
          :capture="captureMode"
          @change="handleImageSelection"
        />
        Use photo instead
      </label>
    </div>
    <p v-if="isStarting" class="scanner-hint">Starting camera...</p>
    <p v-else-if="isScanningFile" class="scanner-hint">Reading barcode from image...</p>
    <p v-else-if="scannerError" class="scanner-error">{{ scannerError }}</p>
    <p v-else class="scanner-hint">Align the barcode inside the frame and hold steady</p>
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
  min-height: 220px;
  border-radius: 0.65rem;
  overflow: hidden;
  background: #0f172a;
}

.scanner-viewport :deep(video) {
  object-fit: cover;
}

.scanner-actions {
  display: flex;
  justify-content: center;
  margin-top: 0.75rem;
}

.scanner-upload {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  border: 1px solid rgba(245, 158, 11, 0.35);
  background: white;
  color: #92400e;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.5rem 0.9rem;
}

.scanner-upload input {
  display: none;
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
