<script setup>
import { computed, reactive, ref, watch } from 'vue';
import Input from '@/components/new_form_elements/Input.vue';
import Select from '@/components/new_form_elements/Select.vue';
import Textarea from '@/components/new_form_elements/Textarea.vue';
import Form from '@/components/new_form_builder/Form.vue';
import BarcodeScanner from '@/components/BarcodeScanner.vue';
import { closeModal } from '@customizer/modal-x';
import { useApiRequest } from '@/composables/useApiRequest';
import { CreateMaterial, lookupMaterialBarcode } from '../api/materialApi';
import { toasted } from '@/utils/utils';
import { useForm } from '@/components/new_form_builder/useForm';
import { useMaterials } from '../store/materialStore';
import { emitEntityMutation } from '@/utils/entitySync';
import { getAllLibrary } from '@/features/library/api/libraryApi';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiBarcode, mdiClose, mdiMagnify } from '@mdi/js';

const { submit } = useForm('addMaterialForm');
const req = useApiRequest();
const libraryReq = useApiRequest();
const materialStore = useMaterials();
const currentStep = ref(1);
const totalSteps = computed(() => 3);
const showBarcodeScanner = ref(false);
const lookupPending = ref(false);
const lookupPreview = ref(null);
const scannedBarcode = ref('');
const currentType = computed(() => materialStore.createType || 'physical');
const isDigital = computed(() => currentType.value === 'digital');
const modalTitle = computed(() => isDigital.value ? 'Add New Digital Material' : 'Add New Physical Material');
const actionLabel = computed(() => isDigital.value ? 'Add Digital Material' : 'Add Physical Material');
const libraryOptions = computed(() => libraryReq.response.value?.libraries || libraryReq.response.value || []);

const userLibraryId = computed(() => {
  const stored = JSON.parse(localStorage.getItem('userDetail') || '{}');
  const user = stored?.user || stored || {};
  return user?.library_id || user?.libraryId || '';
});

const isSuperAdmin = computed(() => {
  const stored = JSON.parse(localStorage.getItem('userDetail') || '{}');
  const user = stored?.user || stored || {};
  const role = String(user?.roleName || user?.role || user?.userRole || '').toUpperCase().replace(/\s+/g, '');
  return role === 'SUPERADMIN';
});

const prefillData = reactive({
  title: '',
  author: '',
  isbn: '',
  published_date: '',
  category: '',
  genre: '',
  language: '',
  department: '',
  description: '',
  library: '',
  location: '',
  condition: '',
  total_copies: '',
  price: '',
  can_borrow: '',
});

const steps = computed(() => {
  const baseSteps = [
    { number: 1, title: 'Basic Information', icon: '📚' },
    { number: 2, title: 'Classification', icon: '🏷️' },
    { number: 3, title: isDigital.value ? 'File Upload' : 'Inventory Details', icon: isDigital.value ? '📎' : '📦' },
  ];

  return baseSteps;
});

libraryReq.send(() => getAllLibrary({ page: 1, size: 200 }));

watch(
  userLibraryId,
  (value) => {
    if (value && !String(prefillData.library || '').trim()) {
      prefillData.library = value;
    }
  },
  { immediate: true }
);

watch(
  isDigital,
  (digital) => {
    if (!digital) {
      if (!String(prefillData.total_copies || '').trim()) prefillData.total_copies = '1';
      if (!String(prefillData.condition || '').trim()) prefillData.condition = 'NEW';
      if (!String(prefillData.location || '').trim()) prefillData.location = 'STACK';
      if (!String(prefillData.can_borrow || '').trim()) prefillData.can_borrow = 'YES';
    }
  },
  { immediate: true }
);

function toDateInputValue(value) {
  if (!value) return '';
  if (typeof value === 'string') return value.slice(0, 10);
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '';
  return date.toISOString().slice(0, 10);
}

function normalizePrefillValue(name, value) {
  if (value === undefined || value === null) return '';
  if (name === 'published_date') return toDateInputValue(value);
  if (name === 'can_borrow') {
    if (value === true) return 'YES';
    if (value === false) return 'NO';
    const normalized = String(value || '').trim().toUpperCase();
    return normalized === 'TRUE' ? 'YES' : normalized === 'FALSE' ? 'NO' : normalized;
  }
  return String(value);
}

function setPrefillValues(values = {}, options = {}) {
  const onlyIfBlank = Boolean(options.onlyIfBlank);
  Object.entries(values).forEach(([name, rawValue]) => {
    const nextValue = normalizePrefillValue(name, rawValue);
    if (!Object.hasOwn(prefillData, name) || nextValue === '') return;
    if (onlyIfBlank && String(prefillData[name] || '').trim()) return;
    prefillData[name] = nextValue;
  });
}

function formatLookupSourceLabel(source) {
  const normalized = String(source || '').trim().toLowerCase();
  if (normalized === 'library') return 'existing library record';
  if (normalized === 'openlibrary' || normalized === 'openlibrary_search') return 'Open Library';
  if (normalized === 'google_books') return 'Google Books';
  return 'book metadata service';
}

function formatDisplayDate(value) {
  const normalized = toDateInputValue(value);
  if (!normalized) return '—';
  const date = new Date(`${normalized}T00:00:00`);
  if (Number.isNaN(date.getTime())) return normalized;
  return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
}

function updateLookupPreview(data = {}, source = '') {
  const title = String(data?.title || '').trim();
  const author = String(data?.author || '').trim();
  const published = toDateInputValue(data?.published_date);
  const isbn = String(data?.isbn || prefillData.isbn || '').trim();
  const barcode = String(scannedBarcode.value || '').trim();

  if (!title && !author && !published && !isbn && !barcode) {
    lookupPreview.value = null;
    return;
  }

  lookupPreview.value = {
    title: title || '—',
    author: author || '—',
    published_label: formatDisplayDate(published),
    isbn: isbn || '—',
    barcode: barcode || '—',
    source: formatLookupSourceLabel(source),
  };
}

function syncScannedCode(scannedCode) {
  const normalized = String(scannedCode || '').trim();
  if (!normalized) return;
  scannedBarcode.value = normalized;
  const digitsOnly = normalized.replace(/\D/g, '');
  if (digitsOnly.length === 10 || digitsOnly.length === 13) {
    setPrefillValues({ isbn: digitsOnly });
  }
}

function applyLookupData(data = {}, options = {}) {
  const source = String(options.source || '').trim().toLowerCase();
  const scannedCode = String(options.scannedCode || '').trim();
  const digitsOnly = scannedCode.replace(/\D/g, '');

  setPrefillValues({
    title: data.title,
    author: data.author,
    isbn: data.isbn || (digitsOnly.length === 10 || digitsOnly.length === 13 ? digitsOnly : ''),
    published_date: data.published_date,
    category: data.category,
    genre: data.genre,
    language: data.language,
    department: data.department,
    description: data.description,
  });

  if (!isDigital.value) {
    setPrefillValues(
      {
        library: data.library,
        total_copies: data.total_copies || 1,
        condition: data.condition || 'NEW',
        location: data.location || 'STACK',
        can_borrow: data.can_borrow ?? 'YES',
        price: data.price,
      },
      { onlyIfBlank: source !== 'library' }
    );
  }
}

function getLookupCode() {
  const fromIsbn = String(prefillData.isbn || '').trim();
  if (fromIsbn) return fromIsbn;
  return String(scannedBarcode.value || '').trim();
}

async function lookupScannedMaterial(rawCode, options = {}) {
  const code = String(rawCode || getLookupCode() || '').trim();
  if (!code) {
    toasted(false, '', 'Scan a barcode or enter an ISBN first.');
    return;
  }

  lookupPending.value = true;
  try {
    const res = await lookupMaterialBarcode(code);
    const payload = res?.data || res;

    if (payload?.found && payload?.data) {
      syncScannedCode(code);
      applyLookupData(payload.data, {
        scannedCode: code,
        source: payload.source,
      });
      updateLookupPreview(payload.data, payload.source);
      toasted(true, `Book details loaded from ${formatLookupSourceLabel(payload.source)}`);
      return;
    }

    lookupPreview.value = null;
    if (!options.silentNotFound) {
      toasted(false, '', 'No book metadata found for this code. You can continue manually.');
    }
  } catch {
    toasted(false, '', 'Could not look up metadata for this code.');
  } finally {
    lookupPending.value = false;
  }
}

async function handleBarcodeScan(code) {
  const scanned = String(code || '').trim();
  if (!scanned) return;
  syncScannedCode(scanned);
  await lookupScannedMaterial(scanned, { silentNotFound: false });
  showBarcodeScanner.value = false;
}

function searchCurrentCode() {
  lookupScannedMaterial(getLookupCode(), { silentNotFound: false });
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
const departments = [
  'Biology',
  'Chemistry',
  'Physics',
  'Mathematics',
  'Statistics',
  'Civil Engineering',
  'Mechanical Engineering',
  'Electrical & Computer Engineering',
  'Software Engineering',
  'Information Technology',
  'Computer Science',
  'Architecture',
  'Agronomy',
  'Animal Science',
  'Plant Science',
  'Nursing',
  'Public Health',
  'Medicine',
  'Pharmacy',
  'Economics',
  'Sociology',
  'Political Science',
  'History',
  'Geography',
  'Law',
  'Business Administration',
  'Accounting & Finance',
  'Management',
  'Education',
  'Journalism & Communication',
  'Other'
];
function handleCreate({ values }) {
  if (isDigital.value) {
    const fileInput = document.querySelector('input[name="file"]');
    const uploadFile = fileInput?.files?.[0] || null;
    const coverImageInput = document.querySelector('input[name="cover_image"]');
    const coverImageFile = coverImageInput?.files?.[0] || null;
    
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
    payload.append('description', values.description || '');
    if (values.library) {
      payload.append('library', values.library);
    }
    payload.append('file', uploadFile, uploadFile.name);
    if (coverImageFile) {
      payload.append('cover_image', coverImageFile, coverImageFile.name);
    }
    
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
    const imageInput = document.querySelector('input[name="image"]');
    const imageFile = imageInput?.files?.[0] || null;
    const payload = new FormData();
    Object.entries(values || {}).forEach(([key, value]) => {
      payload.append(key, value ?? '');
    });
    const barcode = String(scannedBarcode.value || '').trim();
    if (barcode) {
      payload.set('barcode', barcode);
    }
    payload.set('published_date', toDateInputValue(values.published_date));
    payload.set('price', Number(values.price || 0));
    payload.set('can_borrow', String(values.can_borrow || '').toUpperCase() === 'YES');
    payload.set('total_copies', Number(values.total_copies || 0));
    if (imageFile) {
      payload.append('image', imageFile, imageFile.name);
    }
    
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

            <div v-if="!isDigital" class="scan-panel">
              <div class="scan-actions-row">
                <button
                  type="button"
                  class="scan-toggle-btn"
                  :class="{ active: showBarcodeScanner }"
                  @click="showBarcodeScanner = !showBarcodeScanner"
                >
                  <BaseIcon :path="mdiBarcode" size="18" />
                  {{ showBarcodeScanner ? 'Hide scanner' : 'Scan ISBN / barcode' }}
                </button>
                <button
                  type="button"
                  class="scan-search-btn"
                  :disabled="lookupPending"
                  @click="searchCurrentCode"
                >
                  <BaseIcon :path="mdiMagnify" size="18" />
                  Load book details
                </button>
              </div>
              <p v-if="lookupPending" class="scan-status">Looking up book information...</p>
              <BarcodeScanner
                v-if="showBarcodeScanner"
                :active="showBarcodeScanner"
                :allow-image-upload="false"
                @scan="handleBarcodeScan"
              />
            </div>

            <div v-if="lookupPreview" class="lookup-preview">
              <p class="lookup-preview-title">Scanned book details</p>
              <dl class="lookup-preview-grid">
                <div>
                  <dt>Title</dt>
                  <dd>{{ lookupPreview.title }}</dd>
                </div>
                <div>
                  <dt>Author</dt>
                  <dd>{{ lookupPreview.author }}</dd>
                </div>
                <div>
                  <dt>Published</dt>
                  <dd>{{ lookupPreview.published_label }}</dd>
                </div>
                <div>
                  <dt>ISBN / Barcode</dt>
                  <dd>{{ lookupPreview.isbn !== '—' ? lookupPreview.isbn : lookupPreview.barcode }}</dd>
                </div>
              </dl>
              <p class="lookup-preview-source">Source: {{ lookupPreview.source }}</p>
            </div>

            <div class="form-grid">
              <Input
                name="title"
                validation="required"
                label="Title"
                :value="prefillData.title"
                :attributes="{ placeholder: 'Material Title' }"
              />
              <Input
                name="author"
                validation="required"
                label="Author"
                :value="prefillData.author"
                :attributes="{ placeholder: 'Author Name' }"
              />
              <Input
                name="isbn"
                :label="isDigital ? 'ISBN' : 'ISBN (optional)'"
                :value="prefillData.isbn"
                :attributes="{ placeholder: isDigital ? 'Enter ISBN' : 'Enter ISBN if available' }"
              />
              <Input
                name="published_date"
                type="date"
                label="Published Date"
                validation="required"
                :value="prefillData.published_date"
              />
            </div>
          </div>

          <!-- Step 2: Classification -->
          <div v-show="currentStep === 2" class="step-content">
            <h3 class="step-title-heading">Classification Details</h3>
            <div class="form-grid">
              <Select
                name="category"
                label="Category"
                validation="required"
                :value="prefillData.category"
                :options="['BOOK', 'MAGAZINE', 'RESEARCH PAPER', 'JOURNALS', 'THESIS']"
                :attributes="{ placeholder: 'Select Category' }"
              />

              <Select
                name="genre"
                label="Genre"
                validation="required"
                :value="prefillData.genre"
                :options="['SCIENCE', 'FICTION', 'HISTORY', 'BIOGRAPHY','TECHNOLOGY','EDUCATIONAL', 'OTHER']"
                :attributes="{ placeholder: 'Select Genre' }"
              />
              
              <Select
                name="language"
                label="Language"
                validation="required"
                :value="prefillData.language"
                :options="['English', 'Amharic']"
                :attributes="{ placeholder: 'e.g. English, Amharic' }"
              />
              <Select
                name="department"
                label="Department"
                :value="prefillData.department"
                :options="departments"
                :attributes="{ placeholder: 'Target Department' }"
              />
              <Select
                :obj="true"
                name="library"
                label="Owning Library"
                validation="required"
                :options="libraryOptions.map((library) => ({
                  label: library?.name,
                  value: library?.id,
                }))"
                :value="prefillData.library || userLibraryId"
                :attributes="{ placeholder: 'Select Library', disabled: !isSuperAdmin ? 'disabled' : undefined }"
              />
              <Textarea
                name="description"
                label="Description"
                :value="prefillData.description"
                :attributes="{ placeholder: 'Optional description', rows: 3 }"
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
              <Input
                name="cover_image"
                type="file"
                :attributes="{ accept: '.jpg,.jpeg,.png,.webp,.gif' }"
                label="Custom Cover Image (Optional)"
              />
              <p class="file-hint">Accepted formats: PDF, DOC, DOCX, EPUB, TXT, PPT, PPTX</p>
            </div>
            
            <div v-else class="form-grid">
              <Input
                name="image"
                type="file"
                :attributes="{ accept: '.jpg,.jpeg,.png,.webp,.gif' }"
                label="Material Image (Optional)"
              />
              <Select
                name="location"
                label="Library Location"
                validation="required"
                :value="prefillData.location"
                :options="['STACK', 'SHELF','OTHER']"
                :attributes="{ placeholder: 'Select Location' }"
              />
              
              <Select
                name="condition"
                label="Condition"
                validation="required"
                :value="prefillData.condition"
                :options="['NEW', 'GOOD', 'FAIR', 'DAMAGED']"
                :attributes="{ placeholder: 'Select Condition' }"
              />
              
              <Input
                name="total_copies"
                type="number"
                validation="required|numeric"
                label="Total Copies"
                :value="prefillData.total_copies"
              />
              <Input
                name="price"
                type="number"
                label="Price"
                :value="prefillData.price"
                :attributes="{ step: '0.01' }"
              />
              <Select
                name="can_borrow"
                label="Can be Borrowed?"
                validation="required"
                :value="prefillData.can_borrow"
                :options="['YES', 'NO']"
                :attributes="{ placeholder: 'Select Status' }"
              />
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

.scan-panel {
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.scan-actions-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.scan-toggle-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.9rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(245, 158, 11, 0.45);
  background: rgba(245, 158, 11, 0.08);
  color: #b45309;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
}

.scan-toggle-btn.active {
  background: rgba(245, 158, 11, 0.18);
}

.scan-search-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.9rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(37, 99, 235, 0.35);
  background: rgba(37, 99, 235, 0.08);
  color: #1d4ed8;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
}

.scan-search-btn:disabled {
  cursor: wait;
  opacity: 0.7;
}

.scan-status {
  margin: 0;
  font-size: 0.8rem;
  color: #b45309;
}

.lookup-preview {
  margin-bottom: 1rem;
  padding: 0.9rem 1rem;
  border-radius: 0.85rem;
  border: 1px solid rgba(16, 185, 129, 0.35);
  background: rgba(236, 253, 245, 0.9);
}

.lookup-preview-title {
  margin: 0 0 0.65rem;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: #047857;
}

.lookup-preview-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.65rem;
  margin: 0;
}

@media (min-width: 640px) {
  .lookup-preview-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.lookup-preview-grid dt {
  margin: 0;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: #065f46;
}

.lookup-preview-grid dd {
  margin: 0.15rem 0 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: #064e3b;
  word-break: break-word;
}

.lookup-preview-source {
  margin: 0.65rem 0 0;
  font-size: 0.75rem;
  color: #047857;
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
