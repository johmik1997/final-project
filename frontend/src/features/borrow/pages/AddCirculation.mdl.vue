<script setup>
import { onMounted, computed, ref } from 'vue';
import NewFormParent from '../../roles/components/NewFormParent.vue';
import { ModalParent, closeModal } from '@customizer/modal-x';
import { useApiRequest } from '@/composables/useApiRequest';
import { createCirculation } from '../api/circulationApi';
import { getAllMaterials } from '../../material/api/materialApi';
import { getAllUser } from '../../users/Api/UserApi';
import { useCirculation } from '../store/circulationStore';
import { toasted } from '@/utils/utils';
import { emitEntityMutation } from '@/utils/entitySync';
import BaseIcon from '@/components/base/BaseIcon.vue';
import MaterialCard from '../components/MaterialCard.vue';
import { mdiMagnify, mdiBook, mdiAccount } from '@mdi/js';

const circStore = useCirculation();
const req = useApiRequest();
const materialReq = useApiRequest();
const memberReq = useApiRequest();

const selectedMaterial = ref(null);
const selectedMember = ref(null);
const errorMessage = ref('');
const searchQuery = ref('');
const memberSearch = ref('');

onMounted(() => {
  loadMaterials();
  loadMembers();
});

async function loadMaterials() {
  await materialReq.send(() => getAllMaterials({ page: 1, size: 500 }, 'physical'));
}

async function loadMembers(search = '') {
  await memberReq.send(() => getAllUser({ page: 1, size: 50, role: 'MEMBER', search }));
}

function rowsFromPayload(payload) {
  if (!payload) return [];
  if (Array.isArray(payload)) return payload;
  if (Array.isArray(payload?.content)) return payload.content;
  if (Array.isArray(payload?.response)) return payload.response;
  if (Array.isArray(payload?.data)) return payload.data;
  if (Array.isArray(payload?.results)) return payload.results;
  if (Array.isArray(payload?.result)) return payload.result;
  return [];
}

const shelfMaterials = computed(() =>
  rowsFromPayload(materialReq.response.value).filter((m) => m.location === 'SHELF')
);

const filteredMaterials = computed(() => {
  if (!searchQuery.value) return shelfMaterials.value;
  const q = searchQuery.value.toLowerCase();
  return shelfMaterials.value.filter(
    (m) =>
      m.title?.toLowerCase().includes(q) ||
      m.author?.toLowerCase().includes(q) ||
      m.isbn?.toLowerCase().includes(q)
  );
});

const members = computed(() => rowsFromPayload(memberReq.response.value));

const filteredMembers = computed(() => {
  if (!memberSearch.value) return members.value;
  const q = memberSearch.value.toLowerCase();
  return members.value.filter(
    (m) =>
      m.first_name?.toLowerCase().includes(q) ||
      m.last_name?.toLowerCase().includes(q) ||
      m.id_number?.toLowerCase().includes(q)
  );
});

function handleSubmitCirculation() {
  errorMessage.value = '';
  if (!selectedMaterial.value || !selectedMember.value) {
    toasted(false, 'Please select both material and member');
    return;
  }

  req.send(
    () =>
      createCirculation({
        member: selectedMember.value.id,
        material: selectedMaterial.value.id,
      }),
    (res) => {
      if (res?.success) {
        toasted(true, 'Library circulation logged successfully');
        circStore.add(res.data);
        emitEntityMutation('circulations', { action: 'created', id: res.data?.id || null });
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

const step = computed(() => (selectedMaterial.value ? 2 : 1));
</script>

<template>
  <ModalParent
    v-slot="{ data }"
    name="AddCirculation"
    class="bg-black/50 min-h-full p-4 sm:p-6 md:p-10 grid place-items-center"
  >
    <span class="hidden" v-if="data?.material">{{ setInitialMaterial(data.material) }}</span>
    <div class="w-[94vw] max-w-5xl max-h-[90vh] mx-auto">
      <NewFormParent title="Log shelf circulation" size="xs" class="w-full max-h-[90vh]">
        <div class="p-5 sm:p-6 space-y-5 overflow-y-auto max-h-[calc(90vh-4rem)]">
          <div class="steps-bar">
            <div class="step" :class="{ active: step >= 1 }">
              <span class="step-num">1</span>
              <span>Pick shelf material</span>
            </div>
            <div class="step" :class="{ active: step >= 2 }">
              <span class="step-num">2</span>
              <span>Select member & confirm</span>
            </div>
          </div>

          <div v-if="step === 1" class="space-y-4">
            <div class="search-wrap">
              <BaseIcon :path="mdiMagnify" size="20" class="search-icon" />
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search shelf inventory by title, author, or ISBN..."
                class="search-input"
              />
            </div>

            <div v-if="materialReq.pending.value" class="state-box">Loading shelf catalog...</div>
            <div v-else-if="!filteredMaterials.length" class="state-box empty">
              <BaseIcon :path="mdiBook" size="32" />
              <p>No shelf materials found</p>
              <span>Complete transfer requests to move books to the shelf first.</span>
            </div>
            <div v-else class="material-grid">
              <MaterialCard
                v-for="item in filteredMaterials"
                :key="item.id"
                :material="item"
                :is-selected="selectedMaterial?.id === item.id"
                @select="selectedMaterial = $event"
              />
            </div>
          </div>

          <div v-else class="space-y-4">
            <div class="selected-material-banner">
              <div>
                <p class="banner-label">Selected shelf material</p>
                <h3>{{ selectedMaterial.title }}</h3>
                <p class="banner-meta">by {{ selectedMaterial.author }}</p>
              </div>
              <button type="button" class="btn-link" @click="selectedMaterial = null">Change</button>
            </div>

            <label class="field-label">Select library member</label>
            <div class="search-wrap">
              <BaseIcon :path="mdiMagnify" size="18" class="search-icon" />
              <input
                v-model="memberSearch"
                type="text"
                placeholder="Search members by name or ID..."
                class="search-input"
              />
            </div>

            <div class="member-grid">
              <button
                v-for="user in filteredMembers"
                :key="user.id"
                type="button"
                class="member-card"
                :class="{ selected: selectedMember?.id === user.id }"
                @click="selectedMember = user"
              >
                <div class="member-avatar">
                  <BaseIcon :path="mdiAccount" size="20" />
                </div>
                <div>
                  <h4>{{ user.first_name }} {{ user.last_name }}</h4>
                  <p>ID: {{ user.id_number || '-' }}</p>
                </div>
              </button>
            </div>

            <div v-if="errorMessage" class="error-box">{{ errorMessage }}</div>

            <div class="footer-actions">
              <button type="button" class="btn-outline" @click="selectedMaterial = null">Back</button>
              <button
                type="button"
                class="btn-primary"
                :disabled="!selectedMember || req.pending.value"
                @click="handleSubmitCirculation"
              >
                Confirm circulation
              </button>
            </div>
          </div>
        </div>
      </NewFormParent>
    </div>
  </ModalParent>
</template>

<style scoped>
.steps-bar {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.85rem;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
}

.dark .steps-bar {
  background: #0f172a;
  border-color: #334155;
}

.step {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #94a3b8;
}

.step.active {
  color: #0f172a;
  font-weight: 600;
}

.dark .step.active {
  color: #f1f5f9;
}

.step-num {
  width: 1.5rem;
  height: 1.5rem;
  display: grid;
  place-items: center;
  border-radius: 999px;
  background: #e2e8f0;
  font-size: 0.7rem;
  font-weight: 700;
}

.step.active .step-num {
  background: linear-gradient(135deg, #f59e0b, #ea580c);
  color: white;
}

.search-wrap {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 0.9rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
}

.search-input {
  width: 100%;
  padding: 0.7rem 0.9rem 0.7rem 2.5rem;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
  background: #fff;
  font-size: 0.875rem;
}

.dark .search-input {
  background: #1e293b;
  border-color: #334155;
  color: #f1f5f9;
}

.material-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
  max-height: 42vh;
  overflow-y: auto;
  padding-right: 0.25rem;
}

.member-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.65rem;
  max-height: 24vh;
  overflow-y: auto;
}

.member-card {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  padding: 0.75rem;
  border-radius: 0.75rem;
  border: 1px solid #e2e8f0;
  background: #fff;
  text-align: left;
  transition: all 0.15s ease;
}

.member-card.selected {
  border-color: #f59e0b;
  background: #fffbeb;
  box-shadow: 0 0 0 2px rgba(245, 158, 11, 0.25);
}

.dark .member-card {
  background: #1e293b;
  border-color: #334155;
}

.member-avatar {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.65rem;
  display: grid;
  place-items: center;
  background: rgba(245, 158, 11, 0.12);
  color: #f59e0b;
}

.member-card h4 {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 700;
}

.member-card p {
  margin: 0.15rem 0 0;
  font-size: 0.75rem;
  color: #64748b;
}

.selected-material-banner {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.85rem;
  background: linear-gradient(135deg, #fff7ed, #fffbeb);
  border: 1px solid rgba(245, 158, 11, 0.25);
}

.banner-label {
  margin: 0;
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #b45309;
  font-weight: 700;
}

.selected-material-banner h3 {
  margin: 0.25rem 0 0;
  font-size: 1.1rem;
}

.banner-meta {
  margin: 0.2rem 0 0;
  font-size: 0.8rem;
  color: #64748b;
}

.field-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #475569;
}

.state-box {
  padding: 2rem;
  text-align: center;
  color: #64748b;
  border-radius: 0.85rem;
  border: 1px dashed #e2e8f0;
}

.state-box.empty {
  display: grid;
  gap: 0.35rem;
  justify-items: center;
}

.error-box {
  padding: 0.75rem 1rem;
  border-radius: 0.65rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  color: #b91c1c;
  font-size: 0.8rem;
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.65rem;
  padding-top: 0.5rem;
}

.btn-primary,
.btn-outline,
.btn-next,
.btn-link {
  padding: 0.6rem 1rem;
  border-radius: 0.65rem;
  font-size: 0.85rem;
  font-weight: 600;
}

.btn-primary,
.btn-next {
  background: linear-gradient(135deg, #f59e0b, #ea580c);
  color: #0f172a;
}

.btn-primary:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.btn-outline {
  border: 1px solid #e2e8f0;
  color: #475569;
}

.btn-link {
  color: #b45309;
  text-decoration: underline;
}
</style>
