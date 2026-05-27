<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useApiRequest } from '@/composables/useApiRequest';
import { getMaterialById, streamDigitalMaterial, downloadDigitalMaterial } from '../api/materialApi';
import { toasted } from '@/utils/utils';
import { useAuth } from '@/stores/auth';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiArrowLeft, mdiDownload, mdiFileDocument, mdiChevronLeft, mdiChevronRight } from '@mdi/js';

const route = useRoute();
const router = useRouter();
const detailReq = useApiRequest();
const authStore = useAuth();

const materialId = computed(() => route.params.materialId);
const material = computed(() => {
  const p = detailReq.response.value;
  if (!p) return null;
  if (Array.isArray(p)) return p[0] || null;
  if (Array.isArray(p?.content)) return p.content[0] || null;
  if (Array.isArray(p?.data)) return p.data[0] || null;
  if (Array.isArray(p?.results)) return p.results[0] || null;
  return p;
});

const allowDownload = computed(() => {
  const v = material.value?.allow_downloadable;
  if (v === undefined || v === null) return true;
  return v === true || v === 'true' || v === 1;
});

const isPdf = computed(() => String(material.value?.format || '').toLowerCase() === 'pdf');

// PDF state
const pdfLoading = ref(false);
const fileError = ref(false);
const totalPages = ref(0);
const currentPage = ref(1);
const pageCanvases = ref([]); // array of canvas elements set by template refs
let pdfDocRef = null; // raw pdfjs doc — not reactive to avoid proxy issues

function getAccessToken() {
  if (authStore.auth?.accessToken) return authStore.auth.accessToken;
  try {
    const d = JSON.parse(localStorage.getItem('userDetail') || '{}');
    return d?.access || d?.accessToken || d?.token || '';
  } catch { return ''; }
}

async function renderPage(pageNum) {
  if (!pdfDocRef) return;
  const canvas = pageCanvases.value[pageNum - 1];
  if (!canvas) return;
  try {
    const page = await pdfDocRef.getPage(pageNum);
    const scale = Math.min(window.devicePixelRatio || 1, 2) * 1.5;
    const viewport = page.getViewport({ scale });
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    canvas.style.width = '100%';
    canvas.style.height = 'auto';
    await page.render({ canvasContext: canvas.getContext('2d'), viewport }).promise;
  } catch (e) {
    console.error('renderPage error', pageNum, e);
  }
}

async function renderAllPages() {
  for (let i = 1; i <= totalPages.value; i++) {
    await renderPage(i);
  }
}

// Called once canvases are in the DOM (watch totalPages > 0 + nextTick)
async function onPagesReady() {
  // Give Vue one more tick to flush all canvas refs
  await new Promise(r => setTimeout(r, 50));
  await renderAllPages();
}

async function loadPdf() {
  fileError.value = false;
  pdfDocRef = null;
  totalPages.value = 0;
  currentPage.value = 1;
  pageCanvases.value = [];
  if (!isPdf.value || !materialId.value) return;

  pdfLoading.value = true;
  try {
    const token = getAccessToken();
    const res = await fetch(streamDigitalMaterial(materialId.value), {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const arrayBuffer = await res.arrayBuffer();

    const pdfjsLib = await import('pdfjs-dist');
    pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
      'pdfjs-dist/build/pdf.worker.mjs',
      import.meta.url
    ).href;

    pdfDocRef = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    totalPages.value = pdfDocRef.numPages;
    // renderAllPages is triggered by the watch on totalPages below
  } catch (e) {
    console.error('loadPdf error', e);
    fileError.value = true;
  } finally {
    pdfLoading.value = false;
  }
}

// Trigger rendering after canvases are rendered into DOM
watch(totalPages, async (n) => {
  if (n > 0) await onPagesReady();
});

function setCanvasRef(el, index) {
  if (el) pageCanvases.value[index] = el;
}

function loadMaterial() {
  if (!materialId.value) return;
  detailReq.send(
    () => getMaterialById(materialId.value, 'digital'),
    (res) => { if (!res?.success) toasted(false, 'Failed to load digital material'); },
    true
  );
}

async function downloadFile() {
  if (!allowDownload.value) { toasted(false, 'Download is not permitted for this material.'); return; }
  const token = getAccessToken();
  try {
    const res = await fetch(downloadDigitalMaterial(materialId.value), {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!res.ok) throw new Error(`${res.status}`);
    const blob = await res.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = material.value?.title || 'download';
    a.click();
    URL.revokeObjectURL(a.href);
    toasted(true, 'Download started');
  } catch { toasted(false, 'Download failed.'); }
}

function goBack() {
  router.push({ path: `/material/${materialId.value}`, query: { type: 'digital' } });
}

function scrollToPage(num) {
  currentPage.value = num;
  const canvas = pageCanvases.value[num - 1];
  if (canvas) canvas.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function blockContextMenu(e) { if (!allowDownload.value) e.preventDefault(); }
function blockKeys(e) {
  if (!allowDownload.value && (e.ctrlKey || e.metaKey) && ['s', 'p', 'u'].includes(e.key.toLowerCase()))
    e.preventDefault();
}

watch(() => route.params.materialId, () => { if (route.params.materialId) loadMaterial(); }, { immediate: true });
watch(isPdf, (val) => { if (val) loadPdf(); });

onMounted(() => {
  document.addEventListener('contextmenu', blockContextMenu);
  document.addEventListener('keydown', blockKeys);
});
onBeforeUnmount(() => {
  document.removeEventListener('contextmenu', blockContextMenu);
  document.removeEventListener('keydown', blockKeys);
});
</script>

<template>
  <div class="p-4 sm:p-7" :class="{ 'select-none': !allowDownload }">
    <!-- Header -->
    <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
      <button class="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-2" @click="goBack">
        <BaseIcon :path="mdiArrowLeft" size="18" />
        Back to Material Detail
      </button>
      <div class="flex items-center gap-2">
        <span v-if="!allowDownload" class="text-xs text-amber-700 bg-amber-50 border border-amber-200 px-2 py-1 rounded-lg">
          🔒 View only — download & copy restricted
        </span>
        <button
          v-if="allowDownload"
          class="px-3 py-2 rounded-lg bg-primary text-white hover:bg-primary/90 text-sm flex items-center gap-1.5 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="!material"
          @click="downloadFile"
        >
          <BaseIcon :path="mdiDownload" size="16" />
          Download
        </button>
      </div>
    </div>

    <!-- Loading metadata -->
    <div v-if="detailReq.pending.value" class="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-800 flex items-center gap-2">
      <div class="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent"></div>
      Loading digital material...
    </div>

    <div v-else-if="!material" class="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800">
      Digital material was not found.
      <button @click="loadMaterial" class="ml-2 underline">Retry</button>
    </div>

    <!-- Non-PDF -->
    <div v-else-if="!isPdf" class="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800 flex items-center gap-2">
      <BaseIcon :path="mdiFileDocument" size="20" />
      This file format ({{ material?.format || 'unknown' }}) cannot be previewed in the browser.
      <button v-if="allowDownload" class="ml-2 underline" @click="downloadFile">Download to view</button>
    </div>

    <!-- PDF Viewer -->
    <div v-else class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
      <!-- Title bar + pagination -->
      <div class="px-5 py-3 border-b border-gray-100 flex items-center justify-between flex-wrap gap-2">
        <div>
          <h1 class="text-base font-semibold text-gray-900">{{ material?.title }}</h1>
          <p class="text-xs text-gray-500">{{ material?.author }}</p>
        </div>
        <div v-if="totalPages > 1" class="flex items-center gap-1 text-sm text-gray-600">
          <button class="p-1 rounded hover:bg-gray-100 disabled:opacity-40" :disabled="currentPage <= 1" @click="scrollToPage(currentPage - 1)">
            <BaseIcon :path="mdiChevronLeft" size="20" />
          </button>
          <span class="px-1">{{ currentPage }} / {{ totalPages }}</span>
          <button class="p-1 rounded hover:bg-gray-100 disabled:opacity-40" :disabled="currentPage >= totalPages" @click="scrollToPage(currentPage + 1)">
            <BaseIcon :path="mdiChevronRight" size="20" />
          </button>
        </div>
      </div>

      <!-- PDF loading spinner -->
      <div v-if="pdfLoading" class="p-8 flex flex-col items-center gap-3 text-blue-700 bg-blue-50">
        <div class="animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent"></div>
        <span class="text-sm">Preparing secure preview...</span>
      </div>

      <!-- Error -->
      <div v-else-if="fileError" class="p-4 text-center text-red-600">
        Failed to load file.
        <button @click="loadPdf" class="ml-2 underline">Retry</button>
      </div>

      <!-- Canvas pages -->
      <div
        v-else-if="totalPages > 0"
        class="overflow-y-auto bg-gray-200"
        style="max-height: 80vh;"
      >
        <div class="flex flex-col items-center gap-3 py-4 px-2">
          <template v-for="n in totalPages" :key="n">
            <div class="w-full max-w-3xl relative">
              <canvas
                :ref="el => setCanvasRef(el, n - 1)"
                class="w-full shadow-lg rounded bg-white"
                :class="{ 'pointer-events-none': !allowDownload }"
              />
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>
