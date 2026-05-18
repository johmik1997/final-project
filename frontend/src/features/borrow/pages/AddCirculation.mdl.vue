<script setup>
import { onMounted, computed, ref } from 'vue';
import Button from '@/components/Button.vue';
import NewFormParent from '../../roles/components/NewFormParent.vue';
import { ModalParent, closeModal } from '@customizer/modal-x';
import { useApiRequest } from '@/composables/useApiRequest';
import { createCirculation } from '../api/circulationApi';
import { getAllMaterials } from '../../material/api/materialApi';
import { getAllUser } from '../../users/Api/UserApi';
import { useCirculation } from '../store/circulationStore';
import { secondDateFormatWithTime, toasted } from '@/utils/utils';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { 
  mdiCheckCircle,
  mdiAlertCircle,
  mdiCloseCircle,
  mdiMagnify,
  mdiBook
} from '@mdi/js';

const circStore = useCirculation();
const req = useApiRequest();
const materialReq = useApiRequest();
const memberReq = useApiRequest();

const selectedMaterial = ref(null);
const selectedMember = ref(null);
const errorMessage = ref('');
const searchQuery = ref('');
const showMemberModal = ref(false);
const memberSearch = ref('');

onMounted(() => {
  loadMaterials();
  loadMembers();
});

async function loadMaterials() {
  try {
    await materialReq.send(() => getAllMaterials({ page: 1, size: 500 }, 'physical'));
  } catch (error) {
    console.error('Error loading materials:', error);
    toasted(false, 'Failed to load shelf catalog');
  }
}

async function loadMembers(search = '') {
  try {
    await memberReq.send(() => getAllUser({ page: 1, size: 50, role: 'MEMBER', search }));
  } catch (error) {
    console.error('Error loading members:', error);
    toasted(false, 'Failed to load members');
  }
}

const shelfMaterials = computed(() => {
  const payload = materialReq.response.value;
  let list = [];
  if (!payload) list = [];
  else if (Array.isArray(payload)) list = payload;
  else if (Array.isArray(payload?.content)) list = payload.content;
  else if (Array.isArray(payload?.response)) list = payload.response;
  else if (Array.isArray(payload?.data)) list = payload.data;
  else if (payload?.results && Array.isArray(payload.results)) list = payload.results;
  else if (payload?.result && Array.isArray(payload.result)) list = payload.result;
  
  // Filter: ONLY materials currently on SHELF are allowed for on-site library circulation!
  return list.filter(m => m.location === 'SHELF');
});

const filteredMaterials = computed(() => {
  if (!searchQuery.value) return shelfMaterials.value;
  const q = searchQuery.value.toLowerCase();
  return shelfMaterials.value.filter(m => 
    m.title?.toLowerCase().includes(q) || 
    m.author?.toLowerCase().includes(q) ||
    m.isbn?.toLowerCase().includes(q)
  );
});

const members = computed(() => {
  const payload = memberReq.response.value;
  let list = [];
  if (!payload) list = [];
  else if (Array.isArray(payload)) list = payload;
  else if (Array.isArray(payload?.content)) list = payload.content;
  else if (Array.isArray(payload?.response)) list = payload.response;
  else if (Array.isArray(payload?.results)) list = payload.results;
  else if (Array.isArray(payload?.data)) list = payload.data;
  else if (Array.isArray(payload?.result)) list = payload.result;
  return list;
});

const filteredMembers = computed(() => {
  if (!memberSearch.value) return members.value;
  const q = memberSearch.value.toLowerCase();
  return members.value.filter(m => 
    m.first_name?.toLowerCase().includes(q) || 
    m.last_name?.toLowerCase().includes(q) ||
    m.id_number?.toLowerCase().includes(q)
  );
});

async function handleSubmitCirculation() {
  errorMessage.value = '';
  
  if (!selectedMaterial.value || !selectedMember.value) {
    toasted(false, 'Please select both material and member');
    return;
  }

  const payload = {
    member: selectedMember.value.id,
    material: selectedMaterial.value.id
  };

  req.send(
    () => createCirculation(payload),
    (res) => {
      if (res?.success) {
        toasted(true, 'Library circulation logged successfully');
        circStore.add(res.data);
        closeModal();
      } else {
        const err = res?.error || 'Failed to create circulation';
        errorMessage.value = err;
        toasted(false, err);
      }
    }
  );
}

function setInitialMaterial(material) {
  if (material && (!selectedMaterial.value || selectedMaterial.value.id !== material.id)) {
    selectedMaterial.value = material;
  }
  return '';
}

const step = computed(() => {
  if (!selectedMaterial.value) return 1;
  return 2;
});
</script>

<template>
  <ModalParent v-slot="{ data }" name="AddCirculation" class="bg-black/50 min-h-full p-4 sm:p-6 md:p-10 grid place-items-center">
    <span class="hidden" v-if="data?.material">{{ setInitialMaterial(data.material) }}</span>
    <div class="w-[94vw] max-w-4xl max-h-[88vh] mx-auto my-12">
      <NewFormParent title="Log Library Circulation (Shelf Materials Only)" size="xs" class="w-full h-full max-h-[88vh]">
        <div class="p-6 space-y-6">
        <!-- Steps Indicator -->
        <div class="bg-zinc-50 dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl p-4">
          <div class="grid grid-cols-2 gap-4 text-center">
            <div class="flex items-center justify-center gap-2">
              <span class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold"
                    :class="step >= 1 ? 'bg-black text-white dark:bg-white dark:text-black' : 'bg-zinc-200 text-zinc-600'">1</span>
              <span class="text-sm font-medium" :class="step >= 1 ? 'text-zinc-900 dark:text-zinc-100' : 'text-zinc-400'">Pick Shelf Material</span>
            </div>
            <div class="flex items-center justify-center gap-2">
              <span class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold"
                    :class="step >= 2 ? 'bg-black text-white dark:bg-white dark:text-black' : 'bg-zinc-200 text-zinc-600'">2</span>
              <span class="text-sm font-medium" :class="step >= 2 ? 'text-zinc-900 dark:text-zinc-100' : 'text-zinc-400'">Select Member & Confirm</span>
            </div>
          </div>
        </div>

        <!-- Step 1: Material Selection -->
        <div v-if="step === 1" class="space-y-4">
          <div class="relative">
            <BaseIcon :path="mdiMagnify" size="20" class="absolute left-4 top-1/2 -translate-y-1/2 text-zinc-400" />
            <input v-model="searchQuery" type="text" placeholder="Search shelf inventory by title, author, or ISBN..."
                   class="w-full pl-12 pr-4 py-3 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl outline-none" />
          </div>

          <!-- Shelf Catalog -->
          <div v-if="materialReq.pending.value" class="py-8 text-center text-zinc-500">Loading shelf catalog...</div>
          <div v-else-if="filteredMaterials.length === 0" class="py-12 text-center bg-zinc-50 dark:bg-zinc-900/50 rounded-xl border-2 border-dashed border-zinc-200 dark:border-zinc-800">
            <BaseIcon :path="mdiBook" size="32" class="text-zinc-300 mx-auto mb-2" />
            <p class="text-zinc-500 font-medium">No shelf materials found</p>
            <p class="text-xs text-zinc-400 mt-1">Make sure transfer requests are completed to bring books to the Shelf first.</p>
          </div>
          <div v-else class="grid grid-cols-1 sm:grid-cols-2 gap-4 max-h-[40vh] overflow-y-auto pr-1">
            <div v-for="item in filteredMaterials" :key="item.id"
                 class="p-4 rounded-xl border text-left transition-all cursor-pointer flex flex-col justify-between"
                 :class="selectedMaterial?.id === item.id ? 'border-black bg-zinc-50 dark:border-white dark:bg-zinc-900' : 'border-zinc-200 dark:border-zinc-800 hover:border-zinc-400'"
                 @click="selectedMaterial = item">
              <div>
                <h4 class="font-bold text-zinc-900 dark:text-zinc-100">{{ item.title }}</h4>
                <p class="text-xs text-zinc-500">by {{ item.author }}</p>
              </div>
              <div class="mt-4 flex justify-between items-center text-xs">
                <span class="px-2 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400">{{ item.category }}</span>
                <span class="font-semibold text-zinc-700 dark:text-zinc-300">Copies: {{ item.available_copies }} available</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Step 2: Member Confirmation -->
        <div v-else class="space-y-4">
          <div class="p-4 bg-zinc-50 dark:bg-zinc-900 border border-zinc-100 dark:border-zinc-800 rounded-xl flex justify-between items-center">
            <div>
              <p class="text-xs text-zinc-400 uppercase tracking-wider font-bold">Selected Shelf Material</p>
              <h3 class="text-lg font-bold text-zinc-950 dark:text-zinc-50">{{ selectedMaterial.title }}</h3>
              <p class="text-xs text-zinc-500">by {{ selectedMaterial.author }}</p>
            </div>
            <button @click="selectedMaterial = null" class="text-xs font-semibold underline text-zinc-500 hover:text-black">Change</button>
          </div>

          <div class="space-y-3">
            <label class="bw-label">Select Library Member</label>
            <div class="relative">
              <BaseIcon :path="mdiMagnify" size="18" class="absolute left-3 top-1/2 -translate-y-1/2 text-zinc-400" />
              <input v-model="memberSearch" type="text" placeholder="Search members by name or ID..."
                     class="w-full pl-10 pr-4 py-2 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl outline-none" />
            </div>

            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 max-h-[22vh] overflow-y-auto pr-1">
              <div v-for="user in filteredMembers" :key="user.id"
                   class="p-3 border rounded-xl cursor-pointer text-left transition-all"
                   :class="selectedMember?.id === user.id ? 'border-black bg-zinc-50 dark:border-white dark:bg-zinc-900' : 'border-zinc-200 dark:border-zinc-800 hover:border-zinc-400'"
                   @click="selectedMember = user">
                <h4 class="font-bold text-zinc-900 dark:text-zinc-100">{{ user.first_name }} {{ user.last_name }}</h4>
                <p class="text-xs text-zinc-500">ID: {{ user.id_number || '-' }}</p>
              </div>
            </div>
          </div>

          <div v-if="errorMessage" class="p-3 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-900 rounded-xl text-xs text-red-600 dark:text-red-400">
            {{ errorMessage }}
          </div>

          <div class="flex justify-end gap-3 pt-2">
            <button @click="selectedMaterial = null" class="bw-btn bw-btn-outline">Back</button>
            <button @click="handleSubmitCirculation" :disabled="!selectedMember || req.pending.value"
                    class="bw-btn bw-btn-primary disabled:opacity-50">
              Confirm Circulation
            </button>
          </div>
        </div>
      </div>
    </NewFormParent>
  </div>
  </ModalParent>
</template>
