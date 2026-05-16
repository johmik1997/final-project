<script setup>
import { computed, onBeforeUnmount, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useApiRequest } from '@/composables/useApiRequest';
import { getMaterialById } from '../api/materialApi';
import { toasted } from '@/utils/utils';
import { useAuth } from '@/stores/auth';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiArrowLeft, mdiOpenInNew, mdiDownload, mdiFileDocument } from '@mdi/js';

const route = useRoute();
const router = useRouter();
const detailReq = useApiRequest();
const authStore = useAuth();

const materialId = computed(() => route.params.materialId);
const fileError = ref(false);
const inlinePdfUrl = ref('');
const inlinePdfLoading = ref(false);

function extractRow(payload) {
  if (!payload) return null;
  if (Array.isArray(payload)) return payload[0] || null;
  if (Array.isArray(payload?.content)) return payload.content[0] || null;
  if (Array.isArray(payload?.data)) return payload.data[0] || null;
  if (Array.isArray(payload?.results)) return payload.results[0] || null;
  return payload;
}

function resolveBackendOrigin() {
  const raw = import.meta.env.VITE_API_URL || import.meta.env.v_API_URL || '';
  if (!raw) return window.location.origin;
  try {
    const url = new URL(raw);
    return url.origin;
  } catch {
    return window.location.origin;
  }
}

function toAbsoluteUrl(filePath) {
  if (!filePath) return '';
  const value = String(filePath).trim();
  if (!value) return '';
  if (/^https?:\/\//i.test(value)) return value;
  if (value.startsWith('//')) {
    return `${window.location.protocol}${value}`;
  }
  
  const origin = resolveBackendOrigin();
  const normalizedPath = value.startsWith('/') ? value : `/${value}`;
  return `${origin}${normalizedPath}`;
}

const material = computed(() => {
  return extractRow(detailReq.response.value);
});

// Try multiple possible file field names
const fileUrl = computed(() => {
  const materialData = material.value;
  if (!materialData) return '';
  
  const fileField = materialData?.file_url || 
                   materialData?.file || 
                   materialData?.download_url || 
                   materialData?.filePath ||
                   materialData?.url;
  return toAbsoluteUrl(fileField);
});

const isPdf = computed(() => {
  if (!fileUrl.value) return false;
  
  const format = String(material.value?.format || '').toLowerCase();
  if (format === 'pdf') return true;
  
  const url = fileUrl.value.toLowerCase().split('?')[0];
  return url.endsWith('.pdf');
});

const iframeSrc = computed(() => {
  if (!isPdf.value) return '';
  return inlinePdfUrl.value || '';
});

function revokeInlinePdfUrl() {
  if (!inlinePdfUrl.value) return;
  URL.revokeObjectURL(inlinePdfUrl.value);
  inlinePdfUrl.value = '';
}

function getAccessToken() {
  if (authStore.auth?.accessToken) return authStore.auth.accessToken;

  try {
    const detail = JSON.parse(localStorage.getItem('userDetail') || '{}');
    return detail?.access || detail?.accessToken || detail?.token || '';
  } catch {
    return '';
  }
}

async function loadInlinePdfBlob() {
  revokeInlinePdfUrl();
  fileError.value = false;

  if (!isPdf.value || !fileUrl.value) return;

  inlinePdfLoading.value = true;
  try {
    const token = getAccessToken();
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    const response = await fetch(fileUrl.value, { headers });

    if (!response.ok) {
      throw new Error(`Failed to load file (${response.status})`);
    }

    const blob = await response.blob();
    inlinePdfUrl.value = URL.createObjectURL(blob);
  } catch (err) {
    fileError.value = true;
    console.error('Inline PDF preview failed:', err);
  } finally {
    inlinePdfLoading.value = false;
  }
}

function loadMaterial() {
  if (!materialId.value) {
    return;
  }

  detailReq.send(
    () => getMaterialById(materialId.value, 'digital'),
    (res) => {
      if (!res?.success) {
        toasted(false, 'Failed to load digital material');
      } else {
        if (!fileUrl.value) {
          toasted(false, 'This digital material has no file attached');
        }
      }
    },
    true
  );
}

function goBack() {
  router.push({
    path: `/material/${String(materialId.value || '')}`,
    query: { type: 'digital' },
  });
}

function openInNewTab() {
  if (!fileUrl.value) {
    toasted(false, 'No file available to open');
    return;
  }
  window.open(fileUrl.value, '_blank', 'noopener');
}

function downloadFile() {
  if (!fileUrl.value) {
    toasted(false, 'No file available to download');
    return;
  }
  
  const link = document.createElement('a');
  link.href = fileUrl.value;
  link.download = material.value?.title || 'digital-material';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  
  toasted(true, 'Download started');
}

function retryLoad() {
  fileError.value = false;
  loadMaterial();
}

// Watch for route changes
watch(() => route.params.materialId, () => {
  if (route.params.materialId) {
    loadMaterial();
  }
}, { immediate: true });

watch([fileUrl, isPdf], () => {
  loadInlinePdfBlob();
}, { immediate: true });

onBeforeUnmount(() => {
  revokeInlinePdfUrl();
});
</script>

<template>
  <div class="p-4 sm:p-7">
    <div class="mb-4 flex flex-wrap items-center justify-between gap-3">
      <button class="text-sm text-gray-600 hover:text-gray-900 flex items-center gap-2" @click="goBack">
        <BaseIcon :path="mdiArrowLeft" size="18" />
        Back to Material Detail
      </button>

      <div class="flex items-center gap-2">
        <button
          class="px-3 py-2 rounded-lg border border-gray-200 text-gray-700 hover:bg-gray-100 text-sm flex items-center gap-1.5 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="!fileUrl"
          @click="openInNewTab"
        >
          <BaseIcon :path="mdiOpenInNew" size="16" />
          Open
        </button>
        <button
          class="px-3 py-2 rounded-lg bg-primary text-white hover:bg-primary/90 text-sm flex items-center gap-1.5 disabled:opacity-50 disabled:cursor-not-allowed"
          :disabled="!fileUrl"
          @click="downloadFile"
        >
          <BaseIcon :path="mdiDownload" size="16" />
          Download
        </button>
      </div>
    </div>

    <div v-if="detailReq.pending.value" class="bg-blue-50 border border-blue-200 rounded-xl p-4 text-sm text-blue-800 flex items-center gap-2">
      <div class="animate-spin rounded-full h-4 w-4 border-2 border-blue-600 border-t-transparent"></div>
      Loading digital material...
    </div>

    <div v-else-if="!material" class="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800">
      Digital material was not found.
      <button @click="retryLoad" class="ml-2 text-amber-900 underline">Retry</button>
    </div>

    <div v-else-if="!fileUrl" class="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800">
      <div class="flex items-center gap-2">
        <BaseIcon :path="mdiFileDocument" size="20" />
        <span>This digital material has no file attached or the file is missing.</span>
      </div>
      <p class="mt-2 text-xs">Material ID: {{ materialId }}</p>
      <p class="text-xs">Title: {{ material?.title }}</p>
    </div>

    <div v-else-if="!isPdf" class="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-800">
      This file is not a PDF. Use "Open" or "Download" to view it.
      <p class="mt-1 text-xs">File URL: {{ fileUrl }}</p>
    </div>

    <div v-else class="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
      <div class="px-5 py-4 border-b border-gray-100">
        <h1 class="text-lg font-semibold text-gray-900">{{ material?.title || 'Digital Material' }}</h1>
        <p class="text-sm text-gray-500 mt-1">{{ material?.author || 'Unknown Author' }}</p>
        <p v-if="material?.category" class="text-xs text-gray-400 mt-1">Category: {{ material.category }}</p>
      </div>
      <div v-if="inlinePdfLoading" class="p-6 text-sm text-blue-700 bg-blue-50 border-t border-blue-100">
        Preparing PDF preview...
      </div>
      <iframe
        v-else-if="iframeSrc"
        :src="iframeSrc"
        class="w-full h-[70vh] sm:h-[75vh]"
        title="PDF Reader"
        @error="fileError = true"
      />
      <div v-else class="p-4 text-center text-amber-700">
        Inline preview is blocked for this file.
        <button @click="openInNewTab" class="text-primary underline">Open in new tab</button>.
      </div>
      <div v-if="fileError" class="p-4 text-center text-red-600 border-t border-red-100">
        Failed to load PDF.
        <button @click="openInNewTab" class="text-primary underline">Open in new tab</button> instead.
      </div>
    </div>
  </div>
</template>
