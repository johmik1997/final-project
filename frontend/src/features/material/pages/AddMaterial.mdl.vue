<script setup>
import { computed, ref, toRaw } from 'vue';
import Button from '@/components/Button.vue';
import Input from '@/components/new_form_elements/Input.vue';
import Select from '@/components/new_form_elements/Select.vue';
import Form from '@/components/new_form_builder/Form.vue';
import { closeModal } from '@customizer/modal-x';
import { useApiRequest } from '@/composables/useApiRequest';
import { CreateMaterial } from '../api/materialApi';
import { toasted } from '@/utils/utils';
import { useForm } from '@/components/new_form_builder/useForm';
import { useMaterials } from '../store/materialStore';
import { emitEntityMutation } from '@/utils/entitySync';
import { getAllLibrary } from '@/features/library/api/libraryApi';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiClose } from '@mdi/js';

const { submit } = useForm('addMaterialForm');
const req = useApiRequest();
const libraryReq = useApiRequest();
const materialStore = useMaterials();
const currentStep = ref(1);
const totalSteps = computed(() => 3);

const currentType = computed(() => materialStore.createType || 'physical');
const isDigital = computed(() => currentType.value === 'digital');
const modalTitle = computed(() => isDigital.value ? 'Add New Digital Material' : 'Add New Physical Material');
const actionLabel = computed(() => isDigital.value ? 'Add Digital Material' : 'Add Physical Material');
const libraryOptions = computed(() => libraryReq.response.value?.libraries || libraryReq.response.value || []);

const steps = computed(() => {
  const baseSteps = [
    { number: 1, title: 'Basic Information', icon: '📚' },
    { number: 2, title: 'Classification', icon: '🏷️' },
    { number: 3, title: isDigital.value ? 'File Upload' : 'Inventory Details', icon: isDigital.value ? '📎' : '📦' },
  ];

  return baseSteps;
});

libraryReq.send(() => getAllLibrary({ page: 1, size: 200 }));

function toDateInputValue(value) {
  if (!value) return '';
  if (typeof value === 'string') return value.slice(0, 10);
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  return date.toISOString().slice(0, 10);
}

function unwrapRaw(value) {
  if (!value || typeof value !== 'object') return value;
  try {
    return toRaw(value);
  } catch {
    return value;
  }
}

function isFileLike(value) {
  return Boolean(
    value &&
    typeof value === 'object' &&
    typeof value.name === 'string' &&
    typeof value.size === 'number' &&
    typeof value.type === 'string' &&
    typeof value.arrayBuffer === 'function'
  );
}

function normalizeUploadFile(value) {
  const raw = unwrapRaw(value);
  if (!raw) return null;
  if (raw instanceof File || isFileLike(raw)) return raw;
  if (typeof FileList !== 'undefined' && raw instanceof FileList) {
    return raw.length ? unwrapRaw(raw[0]) : null;
  }
  if (Array.isArray(raw)) {
    return normalizeUploadFile(raw[0]);
  }
  if (typeof raw === 'object' && raw[0]) {
    return normalizeUploadFile(raw[0]);
  }
  return null;
}

function nextStep() {
  if (currentStep.value < totalSteps.value) {
    currentStep.value++;
  }
}

function prevStep() {
  if (currentStep.value > 1) {
    currentStep.value--;
  }
}

function handleCreate({ values }) {
  if (isDigital.value) {
    const fileInput = document.querySelector('input[name="file"]');
    const uploadFile = fileInput?.files?.[0] || null;
    
    if (!uploadFile) {
      toasted(false, 'Please choose a digital file before submitting.');
      return;
    }

    const payload = new FormData();
    payload.append('title', values.title || '');
    payload.append('author', values.author || '');
    payload.append('category', values.category || '');
    payload.append('genre', values.genre || '');
    payload.append('published_date', toDateInputValue(values.published_date));
    payload.append('department', values.department || '');
    payload.append('language', values.language || '');
    payload.append('isbn', values.isbn || '');
    if (values.library) {
      payload.append('library', values.library);
    }
    payload.append('file', uploadFile, uploadFile.name);
    
    req.send(
      () => CreateMaterial(payload, currentType.value),
      (res) => {
        if (res.success) {
          if (res.data) {
            materialStore.add(res.data);
          }
          emitEntityMutation('materials', { action: 'created', type: currentType.value });
          toasted(true, 'Material Added Successfully');
          closeModal();
        } else {
          toasted(false, '', res.error);
        }
      }
    );
  } else {
    const payload = {
      ...values,
      published_date: toDateInputValue(values.published_date),
      price: Number(values.price || 0),
      can_borrow: String(values.can_borrow || '').toUpperCase() === 'YES',
      total_copies: Number(values.total_copies || 0),
      library: values.library || null,
    };
    
    req.send(
      () => CreateMaterial(payload, currentType.value),
      (res) => {
        if (res.success) {
          if (res.data) {
            materialStore.add(res.data);
          }
          emitEntityMutation('materials', { action: 'created', type: currentType.value });
          toasted(true, 'Material Added Successfully');
          closeModal();
        } else {
          toasted(false, '', res.error);
        }
      }
    );
  }
}

function validateAndNext() {
  nextStep();
}
</script>

<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-container">
      <!-- Modal Header -->
      <div class="modal-header">
        <div>
          <h2 class="modal-title">{{ modalTitle }}</h2>
          <p class="modal-subtitle">Fill in the details to add a new material to the library</p>
        </div>
        <button class="modal-close" @click="closeModal">
          <BaseIcon :path="mdiClose" size="20" />
        </button>
      </div>

      <!-- Step Navigation -->
      <div class="step-nav">
        <nav class="step-nav-container">
          <div v-for="(step, index) in steps" :key="step.number" class="step-item">
            <div class="step-indicator-wrapper">
              <div 
                class="step-indicator"
                :class="[
                  currentStep === step.number ? 'step-active' : 
                  currentStep > step.number ? 'step-completed' : 
                  'step-inactive'
                ]"
              >
                <span v-if="currentStep > step.number" class="step-check">✓</span>
                <span v-else class="step-icon">{{ step.icon }}</span>
              </div>
              
              <div class="step-label">
                <p class="step-title" :class="currentStep === step.number ? 'step-title-active' : 'step-title-inactive'">
                  {{ step.title }}
                </p>
              </div>
            </div>
            
            <div 
              v-if="index < steps.length - 1" 
              class="step-connector"
              :class="currentStep > step.number ? 'connector-completed' : 'connector-inactive'"
            ></div>
          </div>
        </nav>
      </div>

      <!-- Form Body -->
      <div class="modal-body">
        <Form :inner="false" id="addMaterialForm">
          <!-- Step 1: Basic Information -->
          <div v-show="currentStep === 1" class="step-content">
            <h3 class="step-title-heading">Basic Information</h3>
            <div class="form-grid">
              <Input name="title" validation="required" label="Title" :attributes="{ placeholder: 'Material Title' }" />
              <Input name="author" validation="required" label="Author" :attributes="{ placeholder: 'Author Name' }" />
              <Input name="isbn" label="ISBN" :attributes="{ placeholder: 'Enter ISBN' }" />
              <Input name="published_date" type="date" label="Published Date" validation="required" />
            </div>
          </div>

          <!-- Step 2: Classification -->
          <div v-show="currentStep === 2" class="step-content">
            <h3 class="step-title-heading">Classification Details</h3>
            <div class="form-grid">
              <Select name="category" label="Category" validation="required"
                :options="['BOOK', 'MAGAZINE', 'RESEARCH PAPER', 'JOURNALS', 'THESIS']"
                :attributes="{ placeholder: 'Select Category' }" />

              <Select name="genre" label="Genre" validation="required"
                :options="['SCIENCE', 'FICTION', 'HISTORY', 'BIOGRAPHY','TECHNOLOGY','EDUCATIONAL', 'OTHER']"
                :attributes="{ placeholder: 'Select Genre' }" />
              
              <Select name="language" label="Language" validation="required"
                :options="['English', 'Amharic']"
                :attributes="{ placeholder: 'e.g. English, Amharic' }" />
              <Input name="department" label="Department" :attributes="{ placeholder: 'Target Department' }" />
              <Select
                :obj="true"
                name="library"
                label="Owning Library"
                validation="required"
                :options="libraryOptions.map((library) => ({
                  label: library?.name,
                  value: library?.id,
                }))"
                :attributes="{ placeholder: 'Select Library' }"
              />
            </div>
          </div>

          <!-- Step 3: Digital File or Physical Inventory -->
          <div v-show="currentStep === 3" class="step-content">
            <h3 class="step-title-heading">
              {{ isDigital ? 'Digital File Upload' : 'Physical Inventory Details' }}
            </h3>
            
            <div v-if="isDigital" class="digital-upload">
              <Input
                name="file"
                type="file"
                validation="required"
                :attributes="{ 
                  accept: '.pdf,.doc,.docx,.epub,.txt,.ppt,.pptx',
                }"
                label="Digital File"
              />
              <p class="file-hint">Accepted formats: PDF, DOC, DOCX, EPUB, TXT, PPT, PPTX</p>
            </div>
            
            <div v-else class="form-grid">
              <Select name="location" label="Library Location" validation="required"
                :options="['STACK', 'SHELF','OTHER']"
                :attributes="{ placeholder: 'Select Location' }" />
              
              <Select name="condition" label="Condition" validation="required"
                :options="['NEW', 'GOOD', 'FAIR', 'DAMAGED']"
                :attributes="{ placeholder: 'Select Condition' }" />
              
              <Input name="total_copies" type="number" validation="required|numeric" label="Total Copies" />
              <Input name="price" type="number" label="Price" :attributes="{ step: '0.01' }" />
              <Select name="can_borrow" label="Can be Borrowed?" validation="required"
                :options="['YES', 'NO']"
                :attributes="{ placeholder: 'Select Status' }" />
            </div>
          </div>
        </Form>
      </div>

      <!-- Modal Footer -->
      <div class="modal-footer">
        <div class="step-buttons">
          <button 
            type="button"
            class="btn-secondary" 
            @click.prevent="prevStep"
            :disabled="currentStep === 1"
          >
            ← Previous
          </button>
          
          <div class="step-buttons-right">
            <button 
              v-if="currentStep < totalSteps"
              type="button"
              class="btn-primary" 
              @click.prevent="validateAndNext"
            >
              Next →
            </button>
            
            <button 
              v-if="currentStep === totalSteps"
              type="button"
              class="btn-primary" 
              :disabled="req.pending.value" 
              @click.prevent="submit(handleCreate)"
            >
              <span v-if="req.pending.value" class="loading-spinner"></span>
              {{ actionLabel }}
            </button>
          </div>
        </div>

        <!-- Progress Summary -->
        <div class="progress-footer">
          <div class="progress-info">
            <span>Step {{ currentStep }} of {{ totalSteps }}</span>
            <span class="progress-step-title">{{ steps[currentStep-1].title }}</span>
            <span>{{ Math.round((currentStep / totalSteps) * 100) }}% Complete</span>
          </div>
          <div class="progress-bar-wrapper">
            <div 
              class="progress-bar-fill"
              :style="{ width: `${(currentStep / totalSteps) * 100}%` }"
            ></div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Modal Overlay */
.modal-overlay {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: grid;
  place-items: center;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  padding: 1rem;
  overflow-y: auto;
}

@media (min-width: 640px) {
  .modal-overlay {
    padding: 1.5rem;
  }
}

@media (min-width: 768px) {
  .modal-overlay {
    padding: 2rem;
  }
}

/* Modal Container */
.modal-container {
  width: 100%;
  max-width: 56rem;
  margin: 0 auto;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(4px);
  border-radius: 1.5rem;
  border: 1px solid rgba(203, 213, 225, 0.5);
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.dark .modal-container {
  background: rgba(30, 41, 59, 0.95);
  border: 1px solid rgba(51, 65, 85, 0.5);
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

/* Modal Header */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
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

.modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  background: rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(203, 213, 225, 0.5);
  cursor: pointer;
  transition: all 0.2s ease;
  color: #64748b;
}

.dark .modal-close {
  background: rgba(15, 23, 42, 0.5);
  border-color: rgba(51, 65, 85, 0.5);
  color: #94a3b8;
}

.modal-close:hover {
  background: rgba(0, 0, 0, 0.1);
  transform: scale(1.05);
}

/* Step Navigation */
.step-nav {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid rgba(203, 213, 225, 0.5);
}

.dark .step-nav {
  border-bottom: 1px solid rgba(51, 65, 85, 0.5);
}

@media (min-width: 640px) {
  .step-nav {
    padding: 1rem 2rem;
  }
}

.step-nav-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

@media (min-width: 640px) {
  .step-nav-container {
    justify-content: flex-start;
  }
}

.step-item {
  display: flex;
  align-items: center;
  flex: 1;
}

@media (min-width: 640px) {
  .step-item {
    flex: 0 1 auto;
  }
}

.step-indicator-wrapper {
  display: flex;
  align-items: center;
}

.step-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 9999px;
  transition: all 0.2s ease;
}

@media (min-width: 640px) {
  .step-indicator {
    width: 2.5rem;
    height: 2.5rem;
  }
}

.step-active {
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  color: white;
  box-shadow: 0 0 0 4px rgba(245, 158, 11, 0.2);
}

.step-completed {
  background: #10b981;
  color: white;
}

.step-inactive {
  background: rgba(203, 213, 225, 0.5);
  color: #64748b;
}

.dark .step-inactive {
  background: rgba(51, 65, 85, 0.5);
  color: #94a3b8;
}

.step-check {
  font-size: 0.75rem;
  font-weight: 700;
}

.step-icon {
  font-size: 0.875rem;
}

.step-label {
  margin-left: 0.5rem;
  display: none;
}

@media (min-width: 640px) {
  .step-label {
    display: block;
  }
}

.step-title {
  font-size: 0.75rem;
  font-weight: 500;
}

@media (min-width: 768px) {
  .step-title {
    font-size: 0.875rem;
  }
}

.step-title-active {
  color: #f59e0b;
}

.step-title-inactive {
  color: #64748b;
}

.dark .step-title-inactive {
  color: #94a3b8;
}

.step-connector {
  flex: 1;
  margin: 0 0.75rem;
  height: 0.125rem;
  transition: all 0.2s ease;
}

@media (min-width: 640px) {
  .step-connector {
    margin: 0 1rem;
  }
}

.connector-completed {
  background: #10b981;
}

.connector-inactive {
  background: rgba(203, 213, 225, 0.5);
}

.dark .connector-inactive {
  background: rgba(51, 65, 85, 0.5);
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

/* Custom scrollbar for modal body */
.modal-body::-webkit-scrollbar {
  width: 6px;
}

.modal-body::-webkit-scrollbar-track {
  background: rgba(203, 213, 225, 0.3);
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb {
  background: rgba(245, 158, 11, 0.5);
  border-radius: 3px;
}

.modal-body::-webkit-scrollbar-thumb:hover {
  background: #f59e0b;
}

.step-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateX(10px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

.step-title-heading {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 1rem;
  color: #0f172a;
}

.dark .step-title-heading {
  color: #f1f5f9;
}

@media (min-width: 640px) {
  .step-title-heading {
    font-size: 1.125rem;
    margin-bottom: 1.5rem;
  }
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 768px) {
  .form-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
}

.digital-upload {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.file-hint {
  font-size: 0.75rem;
  color: #64748b;
}

.dark .file-hint {
  color: #94a3b8;
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

.step-buttons {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.step-buttons-right {
  display: flex;
  gap: 0.75rem;
}

.btn-secondary {
  padding: 0.5rem 1.5rem;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  font-weight: 600;
  transition: all 0.2s ease;
  cursor: pointer;
  background: rgba(0, 0, 0, 0.05);
  color: #475569;
  border: none;
}

.dark .btn-secondary {
  background: rgba(15, 23, 42, 0.5);
  color: #94a3b8;
}

.btn-secondary:hover:not(:disabled) {
  background: #0f172a;
  color: white;
}

.dark .btn-secondary:hover:not(:disabled) {
  background: #f1f5f9;
  color: #0f172a;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  padding: 0.5rem 1.5rem;
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
  gap: 0.5rem;
}

@media (min-width: 640px) {
  .btn-primary {
    padding: 0.5rem 2rem;
  }
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px -5px rgba(245, 158, 11, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Progress Footer */
.progress-footer {
  margin-top: 0.5rem;
}

.progress-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #64748b;
}

.dark .progress-info {
  color: #94a3b8;
}

@media (min-width: 640px) {
  .progress-info {
    font-size: 0.875rem;
  }
}

.progress-step-title {
  font-weight: 500;
  color: #f59e0b;
  display: none;
}

@media (min-width: 640px) {
  .progress-step-title {
    display: inline;
  }
}

.progress-bar-wrapper {
  width: 100%;
  background: rgba(203, 213, 225, 0.5);
  border-radius: 9999px;
  height: 0.375rem;
  margin-top: 0.5rem;
  overflow: hidden;
}

.dark .progress-bar-wrapper {
  background: rgba(51, 65, 85, 0.5);
}

.progress-bar-fill {
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  height: 100%;
  border-radius: 9999px;
  transition: width 0.3s ease;
}
</style>