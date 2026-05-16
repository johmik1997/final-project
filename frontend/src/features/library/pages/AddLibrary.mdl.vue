<script setup>
import Button from '@/components/Button.vue';
import NewFormParent from '../../roles/components/NewFormParent.vue';
import LibraryForm from '../components/libraryForm.vue';

import { closeModal } from '@customizer/modal-x';
import { useApiRequest } from '@/composables/useApiRequest';
import { CreateLibrary } from '../api/libraryApi';
import { useLibrary } from '../store/libraryStore';
import { toasted } from '@/utils/utils';
import { useForm } from '@/components/new_form_builder/useForm';
import { emitEntityMutation } from '@/utils/entitySync';

import BaseIcon from '@/components/base/BaseIcon.vue';

import {
  mdiLibrary,
  mdiCheckCircle,
  mdiMapMarker,
} from '@mdi/js';

const req = useApiRequest();
const libraryStore = useLibrary();

const { submit } = useForm('addLibraryForm');

function handleCreate({ values }) {
  req.send(
    () => CreateLibrary(values),
    (res) => {
      if (res.success) {
        libraryStore.add(res.data);

        emitEntityMutation('libraries', {
          action: 'created',
          id: res.data?.id,
        });

        toasted(true, 'Library Created Successfully');

        closeModal();
      } else {
        toasted(false, 'Failed to create library', res.error);
      }
    }
  );
}
</script>

<template>
  <div
    class="fixed inset-0 bg-black/60 backdrop-blur-md min-h-full p-4 sm:p-6 md:p-10 grid place-items-center z-50 overflow-y-auto"
  >
    <div class="w-full max-w-3xl">
      <NewFormParent
        title="Add New Library"
        size="md"
      >
        <template #header-icon>
          <div
            class="bg-gradient-to-r from-amber-500 to-orange-500 p-2.5 rounded-xl shadow-lg"
          >
            <BaseIcon
              :path="mdiLibrary"
              size="22"
              class="text-white"
            />
          </div>
        </template>

        <div class="space-y-6 p-6 sm:p-8">
          <div class="rounded-2xl border border-amber-200 bg-gradient-to-r from-amber-50 to-orange-50 p-4 shadow-sm dark:border-amber-800 dark:from-amber-950/30 dark:to-orange-950/20">
            <div class="flex items-start gap-3">
              <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-md">
                <BaseIcon :path="mdiMapMarker" size="18" />
              </div>
              <div>
                <p class="text-sm font-semibold text-amber-900 dark:text-amber-200">Create a library branch</p>
                <p class="mt-1 text-xs text-amber-700 dark:text-amber-300">
                  Add the branch name, campus, location, and contact details so materials, users, and policies stay aligned.
                </p>
              </div>
            </div>
          </div>

          <LibraryForm form-id="addLibraryForm" />
        </div>

        <div class="flex flex-col gap-3 border-t border-gray-200 px-6 py-5 dark:border-slate-700 sm:flex-row sm:justify-end">
          <Button
            :pending="req.pending.value"
            class="flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 px-6 py-3 font-semibold text-white shadow-md transition-all duration-300 hover:from-amber-600 hover:to-orange-600"
            @click.prevent="submit(handleCreate)"
          >
            <BaseIcon
              :path="mdiCheckCircle"
              size="18"
            />

            Create Library
          </Button>

          <button
            type="button"
            class="flex items-center justify-center rounded-xl border border-gray-300 bg-gray-100 px-6 py-3 font-semibold text-gray-700 transition-colors hover:bg-gray-200 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
            @click.prevent="closeModal"
          >
            Cancel
          </button>
        </div>
      </NewFormParent>
    </div>
  </div>
</template>

<style scoped>
:deep(input:focus),
:deep(select:focus) {
  box-shadow: 0 0 0 3px rgba(245, 158, 11, 0.15);
  outline: none;
}

:deep(.error-message) {
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #ef4444;
}

.dark :deep(.error-message) {
  color: #f87171;
}

:deep(input::placeholder) {
  color: #9ca3af;
}

.dark :deep(input::placeholder) {
  color: #6b7280;
}
</style>
