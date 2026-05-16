<template>
  <div class="edit-material-container">
    <!-- Go Back Button -->
    <button @click.prevent="goBack" class="back-button group">
      <div class="flex gap-2 p-4 items-center">
        <span class="mt-1 transition-transform group-hover:-translate-x-1">
          <svg width="7" height="13" viewBox="0 0 7 13" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path opacity="0.6" fill-rule="evenodd" clip-rule="evenodd"
              d="M5.82539 1.0134C6.03505 1.20471 6.05933 1.54072 5.87962 1.76391L2.15854 6.38525L5.87962 11.0066C6.05933 11.2298 6.03505 11.5658 5.82539 11.7571C5.61572 11.9484 5.30007 11.9226 5.12036 11.6994L1.12037 6.73164C0.959876 6.53232 0.959876 6.23819 1.12037 6.03887L5.12036 1.07113C5.30008 0.847943 5.61572 0.822096 5.82539 1.0134Z"
              class="fill-gray-600 dark:fill-gray-400 stroke-gray-600 dark:stroke-gray-400"
              stroke-linecap="round" />
          </svg>
        </span>
        <h3 class="font-medium text-gray-700 dark:text-gray-300">Go Back</h3>
      </div>
    </button>

    <!-- Main Modal -->
    <div class="modal-wrapper">
      <div class="modal-container">
        <!-- Modal Header -->
        <div class="modal-header">
          <div>
            <h2 class="modal-title">Update Material Info</h2>
            <p class="modal-subtitle">Edit the material details and save your changes</p>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="materialReq.pending.value" class="modal-loading">
          <div class="loading-spinner"></div>
          <p class="loading-text">Loading material details...</p>
        </div>

        <!-- Form Content -->
        <div v-else-if="materialReq.response.value" class="modal-body">
          <MaterialForm
            :initialData="material"
            :libraries="libraryReq.response.value?.libraries || libraryReq.response.value || []"
          />
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer">
          <button 
            type="button"
            class="update-button"
            :disabled="updateReq.pending.value" 
            @click.prevent="submit(update)"
          >
            <span v-if="updateReq.pending.value" class="button-spinner"></span>
            <span v-else>Update Material</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router';
import { useApiRequest } from '@/composables/useApiRequest';
import { getMaterialById, updateMaterialById } from '../api/materialApi'; 
import { toasted } from '@/utils/utils.js';
import { useMaterials } from '../store/materialStore';
import { ref, watch } from 'vue';
import { useForm } from '@/components/new_form_builder/useForm';
import MaterialForm from '../form/materialForm.vue';
import { emitEntityMutation } from '@/utils/entitySync';
import { getAllLibrary } from '@/features/library/api/libraryApi';

const route = useRoute();
const router = useRouter();
const materialStore = useMaterials();
const materialUuid = route.params.materialUuid;
const materialType = ref(String(route.query?.type || 'physical').toLowerCase());

const material = ref({});

function normalizeMaterialResponse(payload) {
  return payload?.data?.response || payload?.data || payload || {};
}

function toDateInputValue(value) {
  if (!value) return '';
  if (typeof value === 'string') return value.slice(0, 10);

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  return date.toISOString().slice(0, 10);
}

const { submit } = useForm('materialform');
const materialReq = useApiRequest();
const updateReq = useApiRequest();
const libraryReq = useApiRequest();

// Fetch material by ID
materialReq.send(() => getMaterialById(materialUuid, materialType.value));
libraryReq.send(() => getAllLibrary({ page: 1, size: 200 }));

// Watch the API response and set local material
watch(
  () => materialReq.response.value,
  (val) => {
    if (val) {
      material.value = normalizeMaterialResponse(val);
      if (material.value?.material_type) {
        materialType.value = String(material.value.material_type).toLowerCase().includes('digital')
          ? 'digital'
          : 'physical';
      }
    }
  }
);

function update({ values }) {
  const payload = {
    ...values,
    published_date: toDateInputValue(values.published_date),
    total_copies: Number(values.total_copies),
    price: Number(values.price)
  };

  updateReq.send(
    () => updateMaterialById(materialUuid, payload, materialType.value),
    (res) => {
      toasted(res.success, 'Material Successfully Updated', res.error);

      if (res.success) {
        // Update store with new data
        const updatedRow = res.data || { ...material.value, ...payload };
        materialStore.update(materialUuid, updatedRow);
        emitEntityMutation('materials', { action: 'updated', id: materialUuid, type: materialType.value });
        router.push({ name: 'Material' }); // Redirect back to material list
      }
    }
  );
}

const goBack = () => router.go(-1);
</script>

<style scoped>
.edit-material-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  transition: background 0.3s ease;
  padding: 1rem;
}

.dark .edit-material-container {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

@media (min-width: 640px) {
  .edit-material-container {
    padding: 1.5rem;
  }
}

/* Back Button */
.back-button {
  background: transparent;
  border: none;
  cursor: pointer;
  margin-bottom: 1rem;
  transition: all 0.2s ease;
}

.back-button:hover {
  color: #f59e0b;
}

/* Modal Wrapper */
.modal-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
}

.modal-container {
  width: 100%;
  max-width: 72rem;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(4px);
  border-radius: 1.5rem;
  border: 1px solid rgba(203, 213, 225, 0.5);
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  transition: all 0.2s ease;
}

.dark .modal-container {
  background: rgba(30, 41, 59, 0.95);
  border: 1px solid rgba(51, 65, 85, 0.5);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

/* Modal Header */
.modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid rgba(203, 213, 225, 0.5);
}

.dark .modal-header {
  border-bottom: 1px solid rgba(51, 65, 85, 0.5);
}

@media (min-width: 640px) {
  .modal-header {
    padding: 1.5rem 2rem;
  }
}

.modal-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
}

.dark .modal-title {
  color: #f1f5f9;
}

@media (min-width: 640px) {
  .modal-title {
    font-size: 1.5rem;
  }
}

.modal-subtitle {
  font-size: 0.75rem;
  color: #64748b;
  margin-top: 0.25rem;
}

.dark .modal-subtitle {
  color: #94a3b8;
}

/* Loading State */
.modal-loading {
  padding: 3rem 2rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.loading-spinner {
  width: 2.5rem;
  height: 2.5rem;
  border: 3px solid rgba(245, 158, 11, 0.2);
  border-top-color: #f59e0b;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-text {
  font-size: 0.875rem;
  color: #64748b;
}

.dark .loading-text {
  color: #94a3b8;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Modal Body */
.modal-body {
  padding: 1.5rem;
  max-height: 60vh;
  overflow-y: auto;
}

@media (min-width: 640px) {
  .modal-body {
    padding: 2rem;
  }
}

/* Custom scrollbar */
.modal-body::-webkit-scrollbar {
  width: 6px;
}

.modal-body::-webkit-scrollbar-track {
  background: rgba(203, 213, 225, 0.3);
  border-radius: 3px;
}

.dark .modal-body::-webkit-scrollbar-track {
  background: rgba(51, 65, 85, 0.3);
}

.modal-body::-webkit-scrollbar-thumb {
  background: rgba(245, 158, 11, 0.5);
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: #f59e0b;
}

/* Modal Footer */
.modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(203, 213, 225, 0.5);
  background: rgba(0, 0, 0, 0.02);
}

.dark .modal-footer {
  border-top: 1px solid rgba(51, 65, 85, 0.5);
  background: rgba(15, 23, 42, 0.3);
}

@media (min-width: 640px) {
  .modal-footer {
    padding: 1rem 2rem;
  }
}

/* Update Button */
.update-button {
  width: 100%;
  padding: 0.75rem 1.5rem;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  font-weight: 600;
  transition: all 0.2s ease;
  cursor: pointer;
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  color: white;
  border: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

@media (min-width: 640px) {
  .update-button {
    padding: 0.875rem 2rem;
    font-size: 1rem;
  }
}

.update-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px -5px rgba(245, 158, 11, 0.4);
}

.update-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.button-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
</style>