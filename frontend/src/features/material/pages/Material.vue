<template>
  <div class="materials-container">
    <!-- Hero Banner -->
    <section class="dashboard-hero">
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">
            <BaseIcon :path="mdiBook" size="28" class="hero-icon" />
            Library Materials
          </h1>
          <p class="hero-subtitle">Manage physical and digital materials in your collection</p>
        </div>

        <div class="hero-actions">
          <div class="type-toggle">
            <button
              class="toggle-btn"
              :class="activeType === 'physical' ? 'toggle-active' : 'toggle-inactive'"
              @click="activeType = 'physical'"
            >
              Physical
            </button>
            <button
              class="toggle-btn"
              :class="activeType === 'digital' ? 'toggle-active' : 'toggle-inactive'"
              @click="activeType = 'digital'"
            >
              Digital
            </button>
          </div>

          <button v-if="activeType === 'physical' && canManageMaterial" @click="openImportModal" class="btn-secondary mr-2">
            <BaseIcon :path="mdiUpload" size="18" />
            <span>Import XLS</span>
          </button>

          <button v-if="canManageMaterial" @click="openCreateModal" class="btn-primary">
            <span>{{ addButtonLabel }}</span>
          </button>
        </div>
      </div>
    </section>

    <!-- Stats Cards -->
    <div class="stats-grid">
      <div class="stat-card tone-blue">
        <div class="stat-card-content">
          <div class="stat-info">
            <p class="stat-label">Total Materials</p>
            <p class="stat-value">{{ headerStats.total }}</p>
            <p class="stat-description">{{ activeType }} materials in library</p>
          </div>
          <div class="stat-icon-wrapper icon-tone-blue">
            <BaseIcon :path="mdiBookshelf" size="24" />
          </div>
        </div>
      </div>

      <div class="stat-card tone-green">
        <div class="stat-card-content">
          <div class="stat-info">
            <p class="stat-label">Available</p>
            <p class="stat-value">{{ headerStats.available }}</p>
            <p class="stat-description">Ready for borrowing</p>
          </div>
          <div class="stat-icon-wrapper icon-tone-green">
            <BaseIcon :path="mdiCheckCircle" size="24" />
          </div>
        </div>
      </div>

      <div class="stat-card tone-amber">
        <div class="stat-card-content">
          <div class="stat-info">
            <p class="stat-label">Currently Borrowed</p>
            <p class="stat-value">{{ headerStats.borrowed }}</p>
            <p class="stat-description">Materials in circulation</p>
          </div>
          <div class="stat-icon-wrapper icon-tone-amber">
            <BaseIcon :path="mdiClockOutline" size="24" />
          </div>
        </div>
      </div>

      <div class="stat-card tone-violet">
        <div class="stat-card-content">
          <div class="stat-info">
            <p class="stat-label">Categories</p>
            <p class="stat-value">{{ headerStats.categories }}</p>
            <p class="stat-description">Unique material categories</p>
          </div>
          <div class="stat-icon-wrapper icon-tone-violet">
            <BaseIcon :path="mdiViewDashboard" size="24" />
          </div>
        </div>
      </div>
    </div>

    <!-- Search & Filter Panel -->
    <div class="dashboard-panel">
      <header class="panel-header">
        <div class="panel-header-content">
          <h2 class="panel-title">Search & Filters</h2>
          <p class="panel-subtitle">Find materials by title, author, category, or condition</p>
        </div>
      </header>
      <div class="panel-body">
        <div class="filters-grid">
          <div class="search-wrapper">
            <BaseIcon :path="mdiMagnify" size="18" class="search-icon" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search by title, author, ISBN, or barcode..."
              class="search-input"
            />
            <button v-if="searchQuery" type="button" @click="clearSearch" class="clear-btn">
              <BaseIcon :path="mdiClose" size="16" />
            </button>
          </div>

          <div v-if="activeType === 'physical'" class="scan-panel">
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
            </div>
            <p v-if="barcodeScanPending" class="scan-status">Searching for scanned barcode…</p>
            <BarcodeScanner
              v-if="showBarcodeScanner"
              :active="showBarcodeScanner"
              :allow-image-upload="false"
              @scan="handleBarcodeScan"
            />
          </div>

          <div class="filter-selects">
            <select v-model="selectedCategory" class="filter-select">
              <option value="">All Categories</option>
              <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
            </select>

            <select v-if="!isDigital" v-model="selectedCondition" class="filter-select">
              <option value="">All Conditions</option>
              <option v-for="cond in conditions" :key="cond" :value="cond">{{ cond }}</option>
            </select>
          </div>

          <div class="view-toggle">
            <button
              class="view-btn"
              :class="viewMode === 'grid' ? 'view-active' : 'view-inactive'"
              @click="viewMode = 'grid'"
            >
              <BaseIcon :path="mdiViewDashboard" size="18" />
              Grid
            </button>
            <button
              class="view-btn"
              :class="viewMode === 'table' ? 'view-active' : 'view-inactive'"
              @click="viewMode = 'table'"
            >
              <BaseIcon :path="mdiFormatListBulleted" size="18" />
              Table
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Grid View -->
    <div v-if="viewMode === 'grid'" class="materials-grid">
      <div
        v-for="row in filteredRows"
        :key="row.id"
        class="material-card"
      >
        <div class="material-card-image" @click="openDetail(row)">
          <img
            :src="row?.cover_image || row?.image || row?.thumbnail || defaultCover"
            :alt="row?.title || 'Material cover'"
            @error="onImageError"
          />
          <div class="material-card-badges">
            <span class="badge-type">{{ activeType }}</span>
            <span v-if="!isDigital" class="badge-stock" :class="stockTone(row)">
              {{ getStock(row) > 0 ? `${getStock(row)} in stock` : 'Unavailable' }}
            </span>
            <span v-else class="badge-stock badge-digital">
              {{ row?.format || 'Digital' }}
            </span>
          </div>
        </div>

        <div class="material-card-content">
          <p class="material-library">{{ row?.library_name || 'Library collection' }}</p>
          <button class="material-title" @click="openDetail(row)">
            {{ row?.title || 'Untitled' }}
          </button>
          <p class="material-author">{{ row?.author || '-' }}</p>

          <div class="material-stats">
            <div class="stat-item">
              <p class="stat-label">Category</p>
              <p class="stat-value">{{ row?.category || row?.genre || '-' }}</p>
            </div>
            <div class="stat-item">
              <p class="stat-label">Rating</p>
              <p class="stat-value rating">
                <BaseIcon :path="mdiStar" size="12" />
                {{ getRating(row) || 'N/A' }}
              </p>
            </div>
            <div class="stat-item">
              <p class="stat-label">{{ isDigital ? 'Format' : 'Condition' }}</p>
              <p class="stat-value">{{ isDigital ? (row?.format || 'Digital') : (row?.condition || 'Good') }}</p>
            </div>
            <div class="stat-item">
              <p class="stat-label">{{ isDigital ? 'Size' : 'Stock' }}</p>
              <p class="stat-value">{{ isDigital ? (row?.file_size || '-') : getStock(row) }}</p>
            </div>
          </div>

          <div class="material-actions">
            <button class="action-btn-details" @click="openDetail(row)">
              Details
            </button>
            <template v-if="canManageMaterial">
              <button class="action-btn-edit" @click="router.push('/edit_material/' + row.id + '?type=' + activeType)">
                Edit
              </button>
              <button class="action-btn-delete" @click="remove(row.id)">
                Delete
              </button>
            </template>
          </div>
        </div>
      </div>

      <div v-if="!pagination.pending.value && filteredRows.length === 0" class="empty-state">
        No materials found for the selected filters.
      </div>
    </div>

    <!-- Table View -->
    <div v-else class="table-view">
      <div class="dashboard-panel">
        <header class="panel-header">
          <div class="panel-header-content">
            <h2 class="panel-title">Materials List</h2>
            <p class="panel-subtitle">Complete catalog with all details</p>
          </div>
        </header>
        <div class="panel-body no-padding">
          <Table
            :headers="{
              head: ['Title', 'Author', 'Category', 'ISBN', 'Stock', 'Price', 'Condition', 'Actions'],
              row: ['title', 'author', 'category', 'isbn', 'stock', 'price', 'condition']
            }"
            :cells="{
              category: (_,row)=> row?.category || row?.genre || '-',
              isbn: (_,row)=> row?.isbn || 'N/A',
              stock: (_,row)=> `${getStock(row)}`,
              price: (_,row)=> row?.price ? `$${row.price}` : 'Free',
              condition: (_,row)=> row?.condition || 'Good'
            }"
            :rows="filteredRows"
            :pending="pagination.pending.value"
            :pagination="pagination.meta.value"
            @next-page="pagination.next"
            @prev-page="pagination.previous"
            @page-change="pagination.goToPage"
            @page-size-change="pagination.setPerPage"
          >
            <template #actions="{ row }">
              <div class="table-actions">
                <button class="table-btn-view" @click="openDetail(row)">
                  <BaseIcon :path="mdiEyeOutline" size="18"/>
                </button>
                <template v-if="canManageMaterial">
                  <button class="table-btn-edit" @click="router.push('/edit_material/' + row.id + '?type=' + activeType)">
                    <BaseIcon :path="mdiPencil" size="18"/>
                  </button>
                  <button class="table-btn-delete" @click="remove(row.id)">
                    <BaseIcon :path="mdiDeleteAlert" size="18"/>
                  </button>
                </template>
              </div>
            </template>
          </Table>
        </div>
      </div>
    </div>

    <!-- Pagination for Grid View -->
    <div v-if="viewMode === 'grid'" class="pagination-wrapper">
      <div class="dashboard-panel">
        <div class="panel-body">
          <div class="pagination-content">
            <div class="pagination-info">
              Page {{ pagination.meta.value.page || 1 }} of {{ pagination.meta.value.totalPages || 1 }}
              <span class="pagination-total">({{ pagination.meta.value.totalElements || 0 }} total)</span>
            </div>

            <div class="pagination-controls">
              <select :value="pagination.meta.value.size" class="per-page-select" @change="pagination.setPerPage(Number($event.target.value))">
                <option :value="5">5 / page</option>
                <option :value="10">10 / page</option>
                <option :value="20">20 / page</option>
                <option :value="50">50 / page</option>
              </select>

              <button class="page-btn" :disabled="(pagination.meta.value.page || 1) <= 1" @click="pagination.previous">
                Previous
              </button>
              <button class="page-btn" :disabled="(pagination.meta.value.page || 1) >= (pagination.meta.value.totalPages || 1)" @click="pagination.next">
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- XLS Import Modal -->
    <div v-if="showImportModal" class="import-modal-overlay" @click.self="closeImportModal">
      <div class="import-modal-card">
        <header class="import-modal-header">
          <h3>Import Physical Materials from Excel</h3>
          <button @click="closeImportModal" class="modal-close-btn">
            <BaseIcon :path="mdiClose" size="18" />
          </button>
        </header>
        
        <div class="import-modal-body">
          <p class="import-instructions">
            Upload an Excel sheet (.xlsx) containing physical materials. The sheet <strong>must</strong> include these column headers:
            <span class="headers-list">title, author, category, genre, published_date, total_copies, price</span>.
          </p>
          
          <div class="file-dropzone" :class="{ 'dropzone-active': isDragging }" @dragover.prevent="isDragging = true" @dragleave.prevent="isDragging = false" @drop.prevent="handleFileDrop">
            <input type="file" ref="fileInput" accept=".xlsx" class="hidden-file-input" @change="handleFileSelect" />
            <div class="dropzone-content" @click="$refs.fileInput?.click()">
              <BaseIcon :path="mdiUpload" size="36" class="upload-icon" />
              <p v-if="!selectedFile">Drag & drop your Excel file here or <span class="browse-link">browse</span></p>
              <p v-else class="selected-file-name">{{ selectedFile.name }}</p>
            </div>
          </div>
          
          <!-- Loading State -->
          <div v-if="importing" class="loading-state">
            <div class="spinner"></div>
            <p>Processing import request, please wait...</p>
          </div>
          
          <!-- Results Display -->
          <div v-if="importResults" class="import-results-panel">
            <div class="results-summary" :class="importResults.failed_count > 0 ? 'summary-warning' : 'summary-success'">
              <p><strong>Status:</strong> {{ importResults.failed_count > 0 ? 'Completed with errors' : 'Successfully Imported!' }}</p>
              <p>Created: <strong>{{ importResults.created_count }}</strong> materials</p>
              <p>Failed: <strong>{{ importResults.failed_count }}</strong> rows</p>
            </div>
            
            <div v-if="importResults.errors && importResults.errors.length" class="errors-log mt-3">
              <h4>Error details:</h4>
              <ul class="errors-list">
                <li v-for="(err, idx) in importResults.errors" :key="idx">{{ err }}</li>
              </ul>
            </div>
          </div>
        </div>
        
        <footer class="import-modal-footer">
          <button @click="closeImportModal" class="btn-cancel" :disabled="importing">Close</button>
          <button @click="submitImport" class="btn-primary" :disabled="!selectedFile || importing">
            <span>{{ importing ? 'Importing...' : 'Upload & Import' }}</span>
          </button>
        </footer>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import Table from '@/components/Table.vue'
import { useMaterials } from '../store/materialStore'
import { useApiRequest } from '@/composables/useApiRequest'
import { getAllMaterials, lookupMaterialBarcode, removeMaterialById } from '../api/materialApi'
import { normalizeRoleValue } from '@/utils/authNavigation'
import { toasted } from '@/utils/utils'
import { openModal } from '@customizer/modal-x'
import ApiService from '@/service/ApiService'
import BaseIcon from '@/components/base/BaseIcon.vue'
import { 
  mdiPencil, 
  mdiDeleteAlert, 
  mdiBook, 
  mdiMagnify, 
  mdiClose, 
  mdiEyeOutline, 
  mdiStar,
  mdiBookshelf,
  mdiCheckCircle,
  mdiClockOutline,
  mdiViewDashboard,
  mdiFormatListBulleted,
  mdiUpload,
  mdiBarcode
} from '@mdi/js'
import { usePaginations } from '@/composables/usePaginationTemp'
import defaultCover from '@/assets/default-coverpage.png'
import { emitEntityMutation, subscribeEntityMutation } from '@/utils/entitySync'
import BarcodeScanner from '@/components/BarcodeScanner.vue'

const materialStore = useMaterials()
const router = useRouter()
const activeType = ref('physical')
const viewMode = ref('grid')
const selectedCategory = ref('')
const selectedCondition = ref('')
const showBarcodeScanner = ref(false)
const barcodeScanPending = ref(false)

const showImportModal = ref(false)
const selectedFile = ref(null)
const isDragging = ref(false)
const importing = ref(false)
const importResults = ref(null)
const fileInput = ref(null)

function openImportModal() {
  showImportModal.value = true
  selectedFile.value = null
  importResults.value = null
  isDragging.value = false
  importing.value = false
}

function closeImportModal() {
  if (importing.value) return
  showImportModal.value = false
}

function handleFileSelect(e) {
  const file = e.target.files[0]
  if (file) {
    if (!file.name.endsWith('.xlsx')) {
      toasted(false, 'Only Excel (.xlsx) files are supported')
      return
    }
    selectedFile.value = file
  }
}

function handleFileDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer.files[0]
  if (file) {
    if (!file.name.endsWith('.xlsx')) {
      toasted(false, 'Only Excel (.xlsx) files are supported')
      return
    }
    selectedFile.value = file
  }
}

async function submitImport() {
  if (!selectedFile.value) return
  importing.value = true
  importResults.value = null
  
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  
  try {
    const apiService = new ApiService()
    const res = await apiService.addAuthenticationHeader().post('/material/physical-materials/import-xls/', formData)
    
    const responseData = res?.data || res
    
    // In Vue, standard api responses are wrapped. Let's make sure we check the actual count values returned by django view.
    if (res?.success || responseData?.success || responseData?.created_count !== undefined) {
      importResults.value = responseData
      toasted(true, `Successfully imported ${responseData.created_count} physical materials`)
      pagination.refresh()
    } else {
      toasted(false, 'Failed to import materials', res?.error || responseData?.detail || 'Validation error')
    }
  } catch (err) {
    const apiError = err?.response?.data || {};
    if (apiError.created_count !== undefined) {
      importResults.value = apiError
      toasted(false, `Import partially failed: ${apiError.failed_count} errors`)
      pagination.refresh()
    } else {
      toasted(false, 'An unexpected error occurred during import')
    }
  } finally {
    importing.value = false
  }
}

const pagination = usePaginations({
  store: materialStore,
  cb: (query) => {
    const enrichedQuery = { ...query }
    if (activeType.value === 'physical') {
      if (userRole.value === 'FRONT DESK STAFF') {
        enrichedQuery.location = 'SHELF'
      } else if (userRole.value === 'STACK STAFF') {
        enrichedQuery.location = 'STACK'
      }
    }
    return getAllMaterials(enrichedQuery, activeType.value)
  },
})

const searchQuery = pagination.search

const removeReq = useApiRequest()
let unsubscribeEntitySync = () => {}

const addButtonLabel = computed(() =>
  activeType.value === 'digital' ? 'Add Digital Material' : 'Add Physical Material'
)

const userRole = computed(() => {
  const stored = JSON.parse(localStorage.getItem('userDetail') || '{}')
  const user = stored?.user || stored || {}
  return normalizeRoleValue(user?.roleName || user?.role || user?.userRole)
})

const typeFilteredRows = computed(() => {
  return (materialStore.materials || []).filter((row) => {
    const rowType = String(row?.material_type || row?.materialType || row?.type || '')
      .toLowerCase()
      .replace(/_/g, ' ')
      .trim()

    if (!rowType) return true
    const matchType = activeType.value === 'digital'
      ? rowType.includes('digital')
      : rowType.includes('physical')

    if (!matchType) return false

    if (activeType.value === 'physical') {
      const loc = String(row?.location || '').toUpperCase().trim()
      if (loc === 'SHELF') {
        return ['FRONT DESK STAFF', 'ADMIN', 'SUPER ADMIN', 'TECHNICAL STAFF'].includes(userRole.value)
      }
      if (loc === 'STACK') {
        return ['STACK STAFF', 'ADMIN', 'SUPER ADMIN', 'TECHNICAL STAFF'].includes(userRole.value)
      }
    }
    return true
  })
})

const categories = computed(() => {
  return Array.from(
    new Set((typeFilteredRows.value || []).map((row) => row?.category || row?.genre).filter(Boolean))
  ).sort()
})

const conditions = computed(() => {
  return Array.from(new Set((typeFilteredRows.value || []).map((row) => row?.condition).filter(Boolean))).sort()
})

const filteredRows = computed(() => {
  let rows = typeFilteredRows.value || []

  if (selectedCategory.value) {
    rows = rows.filter((row) => (row?.category || row?.genre) === selectedCategory.value)
  }

  if (selectedCondition.value) {
    rows = rows.filter((row) => row?.condition === selectedCondition.value)
  }

  return rows
})

const headerStats = computed(() => {
  const rows = typeFilteredRows.value || []
  return {
    total: rows.length,
    available: rows.filter((row) => Number(row?.available_copies ?? row?.copy_number ?? 0) > 0).length,
    borrowed: rows.filter((row) => Number(row?.available_copies ?? row?.copy_number ?? 0) <= 0).length,
    categories: new Set(rows.map((row) => row?.category || row?.genre).filter(Boolean)).size,
  }
})

const isDigital = computed(() => activeType.value === 'digital')

const canManageMaterial = computed(() => !['MEMBER', 'STACK STAFF', 'FRONT DESK STAFF'].includes(userRole.value))

async function handleBarcodeScan(code) {
  const normalized = String(code || '').trim()
  if (!normalized) return

  showBarcodeScanner.value = false
  barcodeScanPending.value = true
  try {
    const res = await lookupMaterialBarcode(normalized)
    const payload = res?.data || res
    const match = payload?.data || {}

    if (payload?.found && payload?.source === 'library' && match?.id) {
      barcodeScanPending.value = false
      toasted(true, `Found ${match?.title || 'material'} from barcode`)
      router.push({
        path: `/material/${match.id}`,
        query: { type: match?.material_type || 'physical' },
      })
      return
    }

    searchQuery.value = normalized
    toasted(
      true,
      payload?.found
        ? `Barcode matched metadata for ${match?.title || normalized}`
        : `Searching materials for ${normalized}`
    )
  } catch {
    searchQuery.value = normalized
    toasted(false, '', 'Could not look up that barcode. Showing search results instead.')
  } finally {
    barcodeScanPending.value = false
  }
}

watch(activeType, () => {
  materialStore.setCreateType(activeType.value)
  searchQuery.value = ''
  selectedCategory.value = ''
  selectedCondition.value = ''
  pagination.send()
}, { immediate: true })

onMounted(() => {
  unsubscribeEntitySync = subscribeEntityMutation('materials', () => {
    pagination.refresh()
  })
})

onBeforeUnmount(() => {
  unsubscribeEntitySync?.()
})

function clearSearch() {
  searchQuery.value = ''
}

function getMaterialId(row) {
  return row?.id || row?.uuid || row?.materialUuid
}

function getStock(row) {
  return Number(row?.available_copies ?? row?.copy_number ?? 0)
}

function getRating(row) {
  const rating = Number(row?.average_rating || row?.rating || row?.avg_rating || 0)
  return Number.isFinite(rating) ? rating.toFixed(1) : 'N/A'
}

function stockTone(row) {
  const stock = getStock(row)
  if (stock > 3) return 'bg-emerald-100 text-emerald-700'
  if (stock > 0) return 'bg-amber-100 text-amber-700'
  return 'bg-rose-100 text-rose-700'
}

function onImageError(event) {
  if (event?.target) event.target.src = defaultCover
}

function openCreateModal() {
  materialStore.setCreateType(activeType.value)
  openModal('AddMaterial')
}

function openDetail(row) {
  const id = getMaterialId(row)
  if (id) {
    router.push({
      path: `/material/${id}`,
      query: { type: activeType.value },
    })
  }
}

function remove(id) {
  openModal(
    'Confirmation',
    {
      title: 'Remove Material',
      message: 'Are you sure you want to delete this material?',
    },
    (confirm) => {
      if (confirm) {
        removeReq.send(
          () => removeMaterialById(id, activeType.value),
          (res) => {
            if (res.success) {
              materialStore.remove(id)
              emitEntityMutation('materials', { action: 'deleted', id, type: activeType.value })
              toasted(true, 'Material removed successfully')
            } else {
              toasted(false, 'Failed to remove material', res.error)
            }
          }
        )
      }
    }
  )
}
</script>

<style scoped>
/* Copy all the styles from the previous version - keep everything except modal styles */
/* Container */
.materials-container {
  min-height: 100vh;
  padding: 1rem;
  background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
  transition: background 0.3s ease;
}

.dark .materials-container {
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
}

@media (min-width: 640px) {
  .materials-container {
    padding: 1.5rem;
  }
}

/* Hero Banner */
.dashboard-hero {
  border-radius: 1.5rem;
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(239, 68, 68, 0.1));
  border: 1px solid rgba(245, 158, 11, 0.2);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.1);
}

.dark .dashboard-hero {
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.3);
}

@media (min-width: 768px) {
  .dashboard-hero {
    padding: 2rem;
  }
}

.hero-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

@media (min-width: 1024px) {
  .hero-content {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.hero-text {
  flex: 1;
}

.hero-icon {
  display: inline-block;
  margin-right: 0.5rem;
}

.hero-title {
  font-size: 1.5rem;
  font-weight: 800;
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.dark .hero-title {
  background: linear-gradient(135deg, #fbbf24, #f87171);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

@media (min-width: 640px) {
  .hero-title {
    font-size: 2rem;
  }
}

.hero-subtitle {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #475569;
}

.dark .hero-subtitle {
  color: #94a3b8;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  align-items: center;
}

/* Type Toggle */
.type-toggle {
  padding: 0.25rem;
  border-radius: 0.75rem;
  background: rgba(255, 255, 255, 0.5);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(203, 213, 225, 0.5);
  display: flex;
}

.dark .type-toggle {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(51, 65, 85, 0.5);
}

.toggle-btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  transition: all 0.2s ease;
  cursor: pointer;
}

.toggle-active {
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  color: white;
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
}

.toggle-inactive {
  background: transparent;
  color: #475569;
}

.dark .toggle-inactive {
  color: #94a3b8;
}

.toggle-inactive:hover {
  background: rgba(0, 0, 0, 0.05);
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  border-radius: 9999px;
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: white;
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px -5px rgba(245, 158, 11, 0.4);
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

@media (min-width: 640px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1280px) {
  .stats-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.stat-card {
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(203, 213, 225, 0.5);
  padding: 1.25rem;
  transition: all 0.2s ease;
}

.dark .stat-card {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(51, 65, 85, 0.5);
}

.stat-card:hover {
  transform: translateY(-2px);
  border-color: rgba(245, 158, 11, 0.3);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.stat-card-content {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #64748b;
}

.dark .stat-label {
  color: #94a3b8;
}

.stat-value {
  margin-top: 0.5rem;
  font-size: 1.875rem;
  font-weight: 800;
  color: #0f172a;
  line-height: 1.2;
}

.dark .stat-value {
  color: #f1f5f9;
}

@media (min-width: 640px) {
  .stat-value {
    font-size: 2.25rem;
  }
}

.stat-description {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #94a3b8;
  line-height: 1.25rem;
}

.stat-icon-wrapper {
  display: flex;
  height: 3rem;
  width: 3rem;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  border-radius: 1rem;
  background: rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(203, 213, 225, 0.5);
  transition: all 0.2s ease;
}

.dark .stat-icon-wrapper {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(51, 65, 85, 0.5);
}

.stat-card:hover .stat-icon-wrapper {
  transform: scale(1.05);
}

.stat-card.tone-blue .stat-icon-wrapper { color: #3b82f6; border-color: rgba(59, 130, 246, 0.2); }
.stat-card.tone-green .stat-icon-wrapper { color: #10b981; border-color: rgba(16, 185, 129, 0.2); }
.stat-card.tone-amber .stat-icon-wrapper { color: #f59e0b; border-color: rgba(245, 158, 11, 0.2); }
.stat-card.tone-violet .stat-icon-wrapper { color: #8b5cf6; border-color: rgba(139, 92, 246, 0.2); }

.icon-tone-blue { color: #3b82f6; }
.icon-tone-green { color: #10b981; }
.icon-tone-amber { color: #f59e0b; }
.icon-tone-violet { color: #8b5cf6; }

/* Dashboard Panel */
.dashboard-panel {
  border-radius: 1rem;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(4px);
  border: 1px solid rgba(203, 213, 225, 0.5);
  overflow: hidden;
  transition: all 0.2s ease;
  margin-bottom: 1.5rem;
}

.dark .dashboard-panel {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(51, 65, 85, 0.5);
}

.dashboard-panel:hover {
  border-color: rgba(245, 158, 11, 0.3);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.panel-header {
  padding: 1rem 1.25rem;
  border-bottom: 1px solid rgba(203, 213, 225, 0.5);
}

.dark .panel-header {
  border-bottom: 1px solid rgba(51, 65, 85, 0.5);
}

.panel-header-content {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.panel-title {
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: -0.01em;
  color: #0f172a;
}

.dark .panel-title {
  color: #f1f5f9;
}

@media (min-width: 640px) {
  .panel-title {
    font-size: 1.125rem;
  }
}

.panel-subtitle {
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.25rem;
}

.dark .panel-subtitle {
  color: #94a3b8;
}

.panel-body {
  padding: 1.25rem;
}

.panel-body.no-padding {
  padding: 0;
}

@media (min-width: 640px) {
  .panel-body {
    padding: 1.5rem;
  }
}

/* Filters */
.filters-grid {
  display: flex;
  flex-direction: column;
  flex-wrap: wrap;
  gap: 1rem;
}

@media (min-width: 768px) {
  .filters-grid {
    flex-direction: row;
    align-items: center;
  }
}

.search-wrapper {
  flex: 2;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
}

.search-input {
  width: 100%;
  padding: 0.625rem 2.5rem 0.625rem 2.25rem;
  box-sizing: border-box;
  border-radius: 0.75rem;
  border: 1px solid rgba(203, 213, 225, 0.5);
  background: rgba(255, 255, 255, 0.5);
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.dark .search-input {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(51, 65, 85, 0.5);
  color: #f1f5f9;
}

.search-input:focus {
  outline: none;
  border-color: #f59e0b;
  box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.1);
}

.scan-btn {
  position: absolute;
  right: 2.5rem;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(203, 213, 225, 0.6);
  background: rgba(255, 255, 255, 0.9);
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
}

.scan-btn:hover,
.scan-btn.active {
  border-color: #f59e0b;
  color: #d97706;
  background: rgba(245, 158, 11, 0.1);
}

.dark .scan-btn {
  background: rgba(30, 41, 59, 0.9);
  border-color: rgba(51, 65, 85, 0.6);
  color: #cbd5e1;
}

.scan-panel {
  width: 100%;
  flex: 1 1 100%;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.85rem;
  border-radius: 0.85rem;
  border: 1px dashed rgba(245, 158, 11, 0.45);
  background: rgba(255, 251, 235, 0.9);
}

.scan-actions-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.65rem;
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

.scan-status {
  margin: 0;
  font-size: 0.8rem;
  font-weight: 600;
  color: #b45309;
}

.clear-btn {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  cursor: pointer;
  background: none;
  border: none;
}

.clear-btn:hover {
  color: #f59e0b;
}

.filter-selects {
  flex: 1;
  display: flex;
  gap: 0.75rem;
}

.filter-select {
  flex: 1;
  padding: 0.625rem 0.75rem;
  border-radius: 0.75rem;
  border: 1px solid rgba(203, 213, 225, 0.5);
  background: rgba(255, 255, 255, 0.5);
  font-size: 0.875rem;
  cursor: pointer;
}

.dark .filter-select {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(51, 65, 85, 0.5);
  color: #f1f5f9;
}

.view-toggle {
  display: flex;
  gap: 0.5rem;
  padding: 0.25rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 0.75rem;
  border: 1px solid rgba(203, 213, 225, 0.5);
}

.dark .view-toggle {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(51, 65, 85, 0.5);
}

.view-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s ease;
  cursor: pointer;
  background: transparent;
  border: none;
}

.view-active {
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  color: white;
}

.view-inactive {
  color: #64748b;
}

.dark .view-inactive {
  color: #94a3b8;
}

.view-inactive:hover {
  background: rgba(0, 0, 0, 0.05);
}

/* Materials Grid */
.materials-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

@media (min-width: 768px) {
  .materials-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1280px) {
  .materials-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.material-card {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(4px);
  border-radius: 1.5rem;
  border: 1px solid rgba(203, 213, 225, 0.5);
  overflow: hidden;
  transition: all 0.2s ease;
}

.dark .material-card {
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(51, 65, 85, 0.5);
}

.material-card:hover {
  transform: translateY(-2px);
  border-color: rgba(245, 158, 11, 0.3);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.material-card-image {
  position: relative;
  height: 14rem;
  overflow: hidden;
  background: #f1f5f9;
  cursor: pointer;
}

.dark .material-card-image {
  background: #1e293b;
}

.material-card-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.material-card:hover .material-card-image img {
  transform: scale(1.05);
}

.material-card-badges {
  position: absolute;
  top: 1rem;
  left: 1rem;
  right: 1rem;
  display: flex;
  justify-content: space-between;
  gap: 0.5rem;
}

.badge-type {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(4px);
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: white;
}

.badge-stock {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.6875rem;
  font-weight: 700;
}

.bg-emerald-100 {
  background: rgba(16, 185, 129, 0.9);
  color: white;
}

.bg-amber-100 {
  background: rgba(245, 158, 11, 0.9);
  color: white;
}

.bg-rose-100 {
  background: rgba(239, 68, 68, 0.9);
  color: white;
}

.badge-digital {
  background: rgba(139, 92, 246, 0.9);
  color: white;
}

.material-card-content {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.material-library {
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: #94a3b8;
}

.material-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #0f172a;
  line-height: 1.4;
  text-align: left;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s ease;
}

.dark .material-title {
  color: #f1f5f9;
}

.material-title:hover {
  color: #f59e0b;
}

.material-author {
  font-size: 0.875rem;
  color: #64748b;
}

.dark .material-author {
  color: #94a3b8;
}

.material-stats {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
}

.stat-item {
  padding: 0.75rem;
  border-radius: 0.75rem;
  background: rgba(0, 0, 0, 0.02);
  border: 1px solid rgba(203, 213, 225, 0.3);
}

.dark .stat-item {
  background: rgba(15, 23, 42, 0.3);
  border-color: rgba(51, 65, 85, 0.3);
}

.stat-label {
  font-size: 0.625rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #94a3b8;
  margin-bottom: 0.25rem;
}

.stat-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #0f172a;
}

.dark .stat-value {
  color: #f1f5f9;
}

.stat-value.rating {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  color: #f59e0b;
}

.material-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.action-btn-details,
.action-btn-edit,
.action-btn-delete {
  flex: 1;
  padding: 0.625rem;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  font-weight: 600;
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
}

.action-btn-details {
  background: rgba(0, 0, 0, 0.05);
  color: #475569;
}

.dark .action-btn-details {
  background: rgba(15, 23, 42, 0.5);
  color: #94a3b8;
}

.action-btn-details:hover {
  background: #0f172a;
  color: white;
}

.action-btn-edit {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.action-btn-edit:hover {
  background: #3b82f6;
  color: white;
}

.action-btn-delete {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.action-btn-delete:hover {
  background: #ef4444;
  color: white;
}

/* Table View */
.table-view {
  margin-bottom: 1.5rem;
}

.table-actions {
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}

.table-btn-view,
.table-btn-edit,
.table-btn-delete {
  padding: 0.5rem;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
}

.table-btn-view {
  background: rgba(0, 0, 0, 0.05);
  color: #64748b;
}

.table-btn-view:hover {
  background: #0f172a;
  color: white;
}

.table-btn-edit {
  background: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
}

.table-btn-edit:hover {
  background: #3b82f6;
  color: white;
}

.table-btn-delete {
  background: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.table-btn-delete:hover {
  background: #ef4444;
  color: white;
}

/* Pagination */
.pagination-wrapper {
  margin-top: 1.5rem;
}

.pagination-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  justify-content: space-between;
  align-items: center;
}

@media (min-width: 640px) {
  .pagination-content {
    flex-direction: row;
  }
}

.pagination-info {
  font-size: 0.875rem;
  color: #64748b;
}

.dark .pagination-info {
  color: #94a3b8;
}

.pagination-total {
  color: #94a3b8;
}

.pagination-controls {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.per-page-select {
  padding: 0.5rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(203, 213, 225, 0.5);
  background: rgba(255, 255, 255, 0.5);
  font-size: 0.875rem;
  cursor: pointer;
}

.dark .per-page-select {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(51, 65, 85, 0.5);
  color: #f1f5f9;
}

.page-btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(203, 213, 225, 0.5);
  background: rgba(255, 255, 255, 0.5);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.dark .page-btn {
  background: rgba(30, 41, 59, 0.6);
  border-color: rgba(51, 65, 85, 0.5);
  color: #f1f5f9;
}

.page-btn:hover:not(:disabled) {
  background: #f59e0b;
  border-color: #f59e0b;
  color: white;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.empty-state {
  grid-column: 1 / -1;
  border-radius: 1rem;
  border: 1px dashed rgba(203, 213, 225, 0.5);
  background: rgba(245, 158, 11, 0.05);
  padding: 2rem;
  text-align: center;
  font-size: 0.875rem;
  color: #64748b;
}

.dark .empty-state {
  border: 1px dashed rgba(51, 65, 85, 0.5);
  background: rgba(245, 158, 11, 0.02);
  color: #94a3b8;
}

/* Button & Modal Styles */
.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  border-radius: 9999px;
  background: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(245, 158, 11, 0.4);
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
  font-weight: 600;
  color: #d97706;
  transition: all 0.2s ease;
  cursor: pointer;
}

.btn-secondary:hover {
  transform: translateY(-2px);
  background: white;
  border-color: #f59e0b;
  box-shadow: 0 10px 20px -5px rgba(245, 158, 11, 0.2);
}

.dark .btn-secondary {
  background: rgba(30, 41, 59, 0.8);
  border-color: rgba(251, 191, 36, 0.4);
  color: #fbbf24;
}

.dark .btn-secondary:hover {
  background: #1e293b;
  border-color: #fbbf24;
}

.import-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}

.import-modal-card {
  background: white;
  border-radius: 1.5rem;
  width: 90%;
  max-width: 550px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(226, 232, 240, 0.8);
  display: flex;
  flex-direction: column;
  max-height: 85vh;
  overflow: hidden;
  animation: slideUp 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.dark .import-modal-card {
  background: #1e293b;
  border-color: rgba(51, 65, 85, 0.8);
  color: #f1f5f9;
}

.import-modal-header {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.dark .import-modal-header {
  border-color: #334155;
}

.import-modal-header h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
}

.dark .import-modal-header h3 {
  color: #f1f5f9;
}

.modal-close-btn {
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 9999px;
  transition: all 0.2s;
}

.modal-close-btn:hover {
  background: rgba(0, 0, 0, 0.05);
  color: #0f172a;
}

.dark .modal-close-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  color: white;
}

.import-modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.import-instructions {
  font-size: 0.875rem;
  color: #475569;
  line-height: 1.4;
  margin-bottom: 1.25rem;
}

.dark .import-instructions {
  color: #94a3b8;
}

.headers-list {
  display: block;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: #f1f5f9;
  border-radius: 0.5rem;
  font-family: monospace;
  font-size: 0.8rem;
  color: #d97706;
}

.dark .headers-list {
  background: #0f172a;
  color: #fbbf24;
}

.file-dropzone {
  border: 2px dashed #cbd5e1;
  border-radius: 1rem;
  padding: 2rem 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  background: #f8fafc;
}

.dark .file-dropzone {
  border-color: #475569;
  background: #0f172a;
}

.file-dropzone:hover, .dropzone-active {
  border-color: #f59e0b;
  background: rgba(245, 158, 11, 0.03);
}

.hidden-file-input {
  display: none;
}

.dropzone-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.upload-icon {
  color: #f59e0b;
}

.browse-link {
  color: #ef4444;
  font-weight: 600;
  text-decoration: underline;
}

.selected-file-name {
  font-weight: 600;
  color: #10b981;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1.25rem;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid rgba(245, 158, 11, 0.1);
  border-radius: 50%;
  border-top-color: #f59e0b;
  animation: spin 1s linear infinite;
}

.import-results-panel {
  margin-top: 1.25rem;
  border-radius: 0.75rem;
  overflow: hidden;
}

.results-summary {
  padding: 1rem;
  font-size: 0.875rem;
}

.summary-success {
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

.summary-warning {
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.errors-log {
  max-height: 120px;
  overflow-y: auto;
  border: 1px solid #cbd5e1;
  border-radius: 0.5rem;
  padding: 0.75rem;
  background: #fafafa;
}

.dark .errors-log {
  background: #0f172a;
  border-color: #334155;
}

.errors-log h4 {
  font-size: 0.8rem;
  font-weight: 700;
  color: #e11d48;
  margin-bottom: 0.25rem;
}

.errors-list {
  list-style: none;
  font-size: 0.75rem;
  line-height: 1.4;
  color: #64748b;
  padding: 0;
  margin: 0;
}

.dark .errors-list {
  color: #94a3b8;
}

.errors-list li {
  margin-bottom: 0.25rem;
}

.import-modal-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
}

.dark .import-modal-footer {
  border-color: #334155;
}

.btn-cancel {
  padding: 0.5rem 1.25rem;
  border-radius: 9999px;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #e2e8f0;
}

.dark .btn-cancel {
  background: #334155;
  border-color: #475569;
  color: #f1f5f9;
}

.dark .btn-cancel:hover {
  background: #475569;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
</style>
