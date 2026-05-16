<script setup>
import { ModalParent, closeModal } from '@customizer/modal-x';
import { useApiRequest } from '@/composables/useApiRequest';
import { toasted } from '@/utils/utils.js';
import { useLibrary } from '../store/libraryStore';
import NewFormParent from '../../roles/components/NewFormParent.vue';
import Button from '@/components/Button.vue';
import { useForm } from '@/components/new_form_builder/useForm';
import LibraryForm from '../components/libraryForm.vue';
import { updateLibraryById } from '../api/libraryApi';
import { emitEntityMutation } from '@/utils/entitySync';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { mdiBookEditOutline, mdiLibrary, mdiCheckCircle, mdiCloseCircle } from '@mdi/js';

const modalName = 'EditLibrary';
const libraryStore = useLibrary();
const { submit } = useForm('libraryForm');
const updateReq = useApiRequest();

function getLibraryId(library) {
  return library?.id || library?.uuid || library?.libraryUuid;
}

function update({ values }, libraryId, currentLibrary = {}) {
  if (!libraryId) {
    toasted(false, '', 'Library id is missing.');
    return;
  }

  updateReq.send(
    () => updateLibraryById(libraryId, values),
    (res) => {
      toasted(res.success, 'Successfully Updated', res.error);
      if (res.success) {
        const updatedLibrary = { ...(currentLibrary || {}), ...(res.data || {}), ...values };
        libraryStore.update(libraryId, updatedLibrary);
        emitEntityMutation('libraries', { action: 'updated', id: libraryId });
        closeModal();
      }
    }
  );
}
</script>

<template>
  <ModalParent v-slot="{ data }" :name="modalName">
    <div class="fixed inset-0 bg-black/60 backdrop-blur-md flex items-center justify-center z-50 p-4 overflow-y-auto">
      <div class="w-full max-w-3xl animate-in fade-in duration-300">
        <NewFormParent title="Update Library" size="md">
          <template #header-icon>
            <div class="bg-gradient-to-r from-amber-500 to-orange-500 p-2.5 rounded-xl shadow-lg">
              <BaseIcon :path="mdiBookEditOutline" size="22" class="text-white" />
            </div>
          </template>

          <div class="relative p-6 sm:p-8">
            <div class="absolute inset-0 overflow-hidden pointer-events-none rounded-2xl">
              <div class="absolute -top-24 -right-24 w-48 h-48 bg-gradient-to-br from-amber-500/5 to-orange-500/5 rounded-full blur-3xl"></div>
              <div class="absolute -bottom-24 -left-24 w-48 h-48 bg-gradient-to-tr from-amber-500/5 to-orange-500/5 rounded-full blur-3xl"></div>
            </div>

            <div class="relative space-y-6">
              <div
                v-if="data?.library"
                class="rounded-2xl border border-amber-200 bg-gradient-to-r from-amber-50/70 to-orange-50/60 p-4 shadow-sm dark:border-amber-800 dark:from-amber-950/30 dark:to-orange-950/20"
              >
                <div class="flex items-start gap-3">
                  <div class="flex-shrink-0">
                    <div class="w-10 h-10 bg-gradient-to-br from-amber-500 to-orange-500 rounded-xl flex items-center justify-center shadow-md">
                      <BaseIcon :path="mdiLibrary" size="18" class="text-white" />
                    </div>
                  </div>
                  <div class="flex-1">
                    <p class="text-xs font-medium text-amber-600 dark:text-amber-400 uppercase tracking-wider">Currently Editing</p>
                    <p class="text-base font-semibold text-gray-900 dark:text-white mt-1">
                      {{ data?.library?.name || 'Unnamed Library' }}
                    </p>
                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                      {{ data?.library?.campus || 'No campus specified' }} • {{ data?.library?.location || 'No location specified' }}
                    </p>
                  </div>
                </div>
              </div>

              <LibraryForm form-id="libraryForm" :library="data?.library || {}" />

           
            </div>
          </div>

          <template #bottom>
            <div class="flex flex-col gap-3 border-t border-gray-200 px-6 py-5 dark:border-slate-700 sm:flex-row sm:justify-end">
              <Button
                class="flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 px-6 py-3 font-semibold text-white shadow-md transition-all duration-300 hover:from-amber-600 hover:to-orange-600"
                :pending="updateReq.pending.value"
                @click.prevent="submit((payload) => update(payload, getLibraryId(data?.library), data?.library || {}))"
              >
                <BaseIcon :path="mdiCheckCircle" size="18" />
                Update Library
              </Button>

              <button
                type="button"
                @click="closeModal"
                class="flex items-center justify-center gap-2 rounded-xl border border-gray-300 bg-gray-100 px-6 py-3 font-semibold text-gray-700 transition-colors hover:bg-gray-200 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
              >
                <BaseIcon :path="mdiCloseCircle" size="18" />
                Cancel
              </button>
            </div>
          </template>
        </NewFormParent>
      </div>
    </div>
  </ModalParent>
</template>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

.animate-in {
  animation: fade-in 0.2s ease-out;
}

:deep(.modal-content) {
  max-height: 85vh;
  overflow-y: auto;
}

:deep(.modal-content::-webkit-scrollbar) {
  width: 6px;
}

:deep(.modal-content::-webkit-scrollbar-track) {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 10px;
}

:deep(.modal-content::-webkit-scrollbar-thumb) {
  background: rgba(245, 158, 11, 0.4);
  border-radius: 10px;
}

:deep(.modal-content::-webkit-scrollbar-thumb:hover) {
  background: rgba(245, 158, 11, 0.6);
}

:deep(input:focus),
:deep(textarea:focus),
:deep(select:focus) {
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.1);
  border-color: #f59e0b;
}
</style>
