<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { Html5Qrcode, Html5QrcodeSupportedFormats } from 'html5-qrcode';

const props = defineProps({
  active: { type: Boolean, default: false },
  /** Minimum ms between duplicate scan emissions */
  scanCooldownMs: { type: Number, default: 2500 },
  /** Same code must be read this many times before emitting */
  minStableReads: { type: Number, default: 4 },
  /** Minimum time the same code must stay visible (ms) */
  stabilityMs: { type: Number, default: 900 },
  /** Stop the camera after a confirmed scan */
  autoStop: { type: Boolean, default: true },
  allowImageUpload: { type: Boolean, default: false },
  captureMode: { type: String, default: 'environment' },
});

const emit = defineEmits(['scan', 'error']);

const scannerId = `barcode-scanner-${Math.random().toString(36).slice(2, 9)}`;
const isStarting = ref(false);
const scannerError = ref('');
const scanStatus = ref('idle'); // idle | tracking | ready
let scanner = null;
let lastScannedCode = '';
let lastScannedAt = 0;
let stableCandidate = '';
let stableCount = 0;
let stableFirstSeenAt = 0;

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

function resetStabilityTracking() {
  stableCandidate = '';
  stableCount = 0;
  stableFirstSeenAt = 0;
  scanStatus.value = 'idle';
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

function processDecodedText(raw) {
  const code = normalizeScannedCode(raw);
  if (!code) return;

  const now = Date.now();
  if (code !== stableCandidate) {
    stableCandidate = code;
    stableCount = 1;
    stableFirstSeenAt = now;
    scanStatus.value = 'tracking';
    return;
  }

  stableCount += 1;
  const heldMs = now - stableFirstSeenAt;
  if (stableCount < props.minStableReads || heldMs < props.stabilityMs) {
    scanStatus.value = 'tracking';
    return;
  }

  if (!shouldEmitScan(code)) {
    resetStabilityTracking();
    return;
  }

  scanStatus.value = 'ready';
  emit('scan', code);
  resetStabilityTracking();
  if (props.autoStop) {
    stopScanner();
  }
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
        fps: 10,
        qrbox: scanBox,
        aspectRatio: 1.777,
        disableFlip: false,
        experimentalFeatures: {
          useBarCodeDetectorIfSupported: true,
        },
      },
      (decodedText) => {
        processDecodedText(decodedText);
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
      lastScannedCode = '';
      lastScannedAt = 0;
      resetStabilityTracking();
      startScanner();
    } else {
      resetStabilityTracking();
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
    <p v-else-if="scanStatus === 'tracking'" class="scanner-hint scanner-hint-tracking">
      Hold the barcode steady in the frame…
    </p>
    <p v-else-if="scanStatus === 'ready'" class="scanner-hint scanner-hint-ready">Barcode confirmed</p>
    <p v-else class="scanner-hint">Align the barcode inside the frame and hold steady for a moment</p>
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

.scanner-hint {
  margin: 0.5rem 0 0;
  font-size: 0.8rem;
  color: #92400e;
  text-align: center;
}

.scanner-hint-tracking {
  color: #b45309;
  font-weight: 600;
}

.scanner-hint-ready {
  color: #047857;
  font-weight: 600;
}

.scanner-error {
  margin: 0.5rem 0 0;
  font-size: 0.8rem;
  color: #b91c1c;
  text-align: center;
}
</style>
