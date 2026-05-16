<script setup>
import { ref, computed } from 'vue';
import Form from '@/components/new_form_builder/Form.vue';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { 
  mdiMagnify, 
  mdiClose,
  mdiBook,
  mdiCheckCircle
} from '@mdi/js';

import LibraryHeader from './BorrowHeader.vue';
import MaterialCard from './MaterialCard.vue';
import BorrowSummary from './BorrowSummary.vue';
import MemberSearchModal from './MemberSearchModal.vue';

const props = defineProps({
  materials: { type: Array, default: () => [] },
  members: { type: Array, default: () => [] },
  selectedMaterial: { type: Object, default: null },
  selectedMember: { type: Object, default: null },
  loading: { type: Boolean, default: false },
});

const emit = defineEmits(['update:selectedMaterial', 'update:selectedMember', 'submit']);

const searchQuery = ref('');
const viewMode = ref('grid');
const showMemberModal = ref(false);

const currentStep = computed(() => {
  if (!props.selectedMaterial) return 1;
  if (!props.selectedMember) return 2;
  return 3;
});

const filteredMaterials = computed(() => {
  if (!searchQuery.value) return props.materials;
  const q = searchQuery.value.toLowerCase();
  return props.materials.filter(m => 
    m.title?.toLowerCase().includes(q) || 
    m.author?.toLowerCase().includes(q) ||
    m.isbn?.toLowerCase().includes(q)
  );
});

const stats = computed(() => ({
  total: props.materials.length,
  available: props.materials.filter(m => m.available_copies > 0).length,
  borrowed: props.materials.filter(m => m.total_copies - m.available_copies > 0).length,
  categories: new Set(props.materials.map(m => m.category)).size
}));

function handleSelectMaterial(material) {
  emit('update:selectedMaterial', material);
}

function handleSelectMember(member) {
  emit('update:selectedMember', member);
  showMemberModal.value = false;
}

function handleFinalSubmit() {
  emit('submit', { 
    material: props.selectedMaterial, 
    member: props.selectedMember 
  });
}

function clearSearch() {
  searchQuery.value = '';
}

function resetToMaterialSelection() {
  emit('update:selectedMaterial', null);
  emit('update:selectedMember', null);
}
</script>

<template>
  <Form @submit.prevent class="relative" id="borrowform" :inner="false">
    
    <div class="mb-6">
      <LibraryHeader 
        :stats="stats" 
        v-model:viewMode="viewMode" 
      />
    </div>

    <!-- Step Navigation -->
    <div class="mb-6 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl p-4 transition-all duration-300">
      <div class="grid grid-cols-3 gap-2">
        <div class="flex items-center gap-2">
          <div
            class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold transition-all duration-200"
            :class="currentStep >= 1 ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-md' : 'bg-gray-200 dark:bg-slate-700 text-gray-600 dark:text-gray-400'"
          >
            1
          </div>
          <span class="text-sm font-medium" :class="currentStep >= 1 ? 'text-gray-900 dark:text-white' : 'text-gray-500 dark:text-gray-500'">Pick Material</span>
        </div>
        <div class="flex items-center gap-2">
          <div
            class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold transition-all duration-200"
            :class="currentStep >= 2 ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-md' : 'bg-gray-200 dark:bg-slate-700 text-gray-600 dark:text-gray-400'"
          >
            2
          </div>
          <span class="text-sm font-medium" :class="currentStep >= 2 ? 'text-gray-900 dark:text-white' : 'text-gray-500 dark:text-gray-500'">Review Summary</span>
        </div>
        <div class="flex items-center gap-2">
          <div
            class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold transition-all duration-200"
            :class="currentStep >= 3 ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white shadow-md' : 'bg-gray-200 dark:bg-slate-700 text-gray-600 dark:text-gray-400'"
          >
            <BaseIcon v-if="currentStep >= 3" :path="mdiCheckCircle" size="14" />
            <span v-else>3</span>
          </div>
          <span class="text-sm font-medium" :class="currentStep >= 3 ? 'text-green-700 dark:text-green-400' : 'text-gray-500 dark:text-gray-500'">Complete Borrow</span>
        </div>
      </div>
    </div>

    <!-- Step 1: Material Selection -->
    <div v-if="!selectedMaterial">
      <div class="mb-3 text-sm text-gray-600 dark:text-gray-400">
        Select a material card to continue.
      </div>
      <div class="mb-6">
        <div class="relative">
          <BaseIcon 
            :path="mdiMagnify" 
            size="20" 
            class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500"
          />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by title, author, or ISBN..."
            class="w-full pl-12 pr-12 py-3.5 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-amber-400 outline-none transition-all duration-200 text-gray-900 dark:text-gray-100 placeholder:text-gray-400 dark:placeholder:text-gray-500"
          />
          <button
            v-if="searchQuery"
            @click="clearSearch"
            class="absolute right-4 top-1/2 -translate-y-1/2 p-1 hover:bg-gray-100 dark:hover:bg-slate-700 rounded-full transition-colors duration-200"
          >
            <BaseIcon :path="mdiClose" size="18" class="text-gray-400 dark:text-gray-500" />
          </button>
        </div>
      </div>
      <div class="flex-1 min-w-0 transition-all duration-300">
        <div v-if="props.loading" class="bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-800 rounded-xl p-4 flex items-center gap-3">
          <div class="animate-spin rounded-full h-5 w-5 border-2 border-amber-600 border-t-transparent"></div>
          <p class="text-sm text-blue-800 dark:text-blue-300">Loading catalog...</p>
        </div>

        <div v-else-if="filteredMaterials.length === 0" class="py-16 text-center bg-gray-50 dark:bg-slate-800/50 rounded-xl border-2 border-dashed border-gray-200 dark:border-slate-700">
          <div class="bg-white dark:bg-slate-700 w-20 h-20 rounded-xl flex items-center justify-center mx-auto mb-4 shadow-sm">
            <BaseIcon :path="mdiBook" size="32" class="text-gray-300 dark:text-gray-600" />
          </div>
          <p class="text-gray-600 dark:text-gray-400 font-medium">No materials found</p>
          <p class="text-sm text-gray-400 dark:text-gray-500 mt-1">Try adjusting your search</p>
        </div>

        <div v-else>
          <div v-if="viewMode === 'grid'" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <MaterialCard 
              v-for="item in filteredMaterials" 
              :key="item.id"
              :material="item"
              :is-selected="selectedMaterial?.id === item.id"
              :view-mode="viewMode"
              @select="handleSelectMaterial"
            />
          </div>

          <div v-else class="overflow-x-auto rounded-xl border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800">
            <table class="min-w-full text-sm">
              <thead class="bg-gray-50 dark:bg-slate-900 border-b border-gray-200 dark:border-slate-700">
                <tr>
                  <th class="text-left px-4 py-3 font-semibold text-gray-700 dark:text-gray-300">Title</th>
                  <th class="text-left px-4 py-3 font-semibold text-gray-700 dark:text-gray-300">Author</th>
                  <th class="text-left px-4 py-3 font-semibold text-gray-700 dark:text-gray-300">Category</th>
                  <th class="text-left px-4 py-3 font-semibold text-gray-700 dark:text-gray-300">Available</th>
                  <th class="text-left px-4 py-3 font-semibold text-gray-700 dark:text-gray-300">Total</th>
                  <th class="text-left px-4 py-3 font-semibold text-gray-700 dark:text-gray-300">Status</th>
                  <th class="text-left px-4 py-3 font-semibold text-gray-700 dark:text-gray-300">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in filteredMaterials"
                  :key="item.id"
                  class="border-b border-gray-100 dark:border-slate-700 hover:bg-amber-50 dark:hover:bg-amber-950/30 transition-colors duration-200"
                  :class="selectedMaterial?.id === item.id ? 'bg-amber-50 dark:bg-amber-950/50' : ''"
                >
                  <td class="px-4 py-3 font-medium text-gray-900 dark:text-white">{{ item.title || 'Untitled' }}</td>
                  <td class="px-4 py-3 text-gray-600 dark:text-gray-400">{{ item.author || '-' }}</td>
                  <td class="px-4 py-3 text-gray-600 dark:text-gray-400">{{ item.category || 'General' }}</td>
                  <td class="px-4 py-3 text-gray-700 dark:text-gray-300">{{ item.available_copies || 0 }}</td>
                  <td class="px-4 py-3 text-gray-700 dark:text-gray-300">{{ item.total_copies || 0 }}</td>
                  <td class="px-4 py-3">
                    <span
                      class="text-xs font-semibold px-2 py-1 rounded-full"
                      :class="item.available_copies > 0 ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300' : 'bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300'"
                    >
                      {{ item.available_copies > 0 ? 'Available' : 'Unavailable' }}
                    </span>
                  </td>
                  <td class="px-4 py-3">
                    <button
                      class="text-xs px-3 py-1.5 rounded-lg font-medium transition-all duration-200"
                      :class="item.available_copies > 0 ? 'bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:from-amber-600 hover:to-orange-600 shadow-sm' : 'bg-gray-200 dark:bg-slate-700 text-gray-500 dark:text-gray-500 cursor-not-allowed'"
                      :disabled="item.available_copies <= 0"
                      @click="handleSelectMaterial(item)"
                    >
                      {{ selectedMaterial?.id === item.id ? 'Selected ✓' : 'Select' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="max-w-6xl mx-auto">
      <BorrowSummary 
        :material="selectedMaterial"
        :member="selectedMember"
        @change-member="showMemberModal = true"
        @submit="handleFinalSubmit"
        @clear="resetToMaterialSelection"
      />
    </div>

    <MemberSearchModal
      v-if="showMemberModal"
      :members="members"
      @select="handleSelectMember"
      @close="showMemberModal = false"
    />
  </Form>
</template>