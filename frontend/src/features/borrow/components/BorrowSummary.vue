<script setup>
import BaseIcon from '@/components/base/BaseIcon.vue';
import Button from '@/components/Button.vue';
import { 
  mdiBook, 
  mdiAccount, 
  mdiCalendar,
  mdiClockOutline,
  mdiClose,
  mdiCheckCircle,
  mdiAlertCircle
} from '@mdi/js';
import { computed } from 'vue';

const props = defineProps({
  material: Object,
  member: Object
});

const emit = defineEmits(['change-member', 'submit', 'clear']);

const dueDate = computed(() => {
  const date = new Date();
  date.setDate(date.getDate() + 14);
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric' 
  });
});

const isComplete = computed(() => {
  return props.material && props.member;
});
</script>

<template>
  <div class="bg-white dark:bg-slate-800 rounded-xl border border-gray-200 dark:border-slate-700 shadow-sm overflow-hidden transition-all duration-300 sticky top-4">
    <div class="p-5 space-y-4">
      <!-- Selected Material -->
      <div class="space-y-2">
        <div class="flex items-center justify-between">
          <p class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Material</p>
          <button 
            @click="emit('clear')"
            class="text-xs text-amber-600 dark:text-amber-400 hover:text-amber-800 dark:hover:text-amber-300 font-medium transition-colors duration-200"
          >
            Change Material
          </button>
        </div>
        <div class="bg-gray-50 dark:bg-slate-900 rounded-xl p-3 border border-gray-200 dark:border-slate-700 transition-all duration-200">
          <div class="flex items-start gap-3">
            <div class="bg-amber-100 dark:bg-amber-950 p-2 rounded-lg">
              <BaseIcon :path="mdiBook" size="20" class="text-amber-600 dark:text-amber-400" />
            </div>
            <div class="flex-1">
              <p class="font-medium text-gray-900 dark:text-white text-sm">{{ material.title }}</p>
              <p class="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1 mt-1">
                <BaseIcon :path="mdiAccount" size="10" />
                {{ material.author }}
              </p>
              <div class="flex items-center gap-2 mt-2">
                <span class="text-[10px] bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 px-2 py-0.5 rounded-full font-medium">
                  {{ material.available_copies }} copies available
                </span>
              </div>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-2 mt-3 text-xs">
            <div class="bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-md p-2">
              <p class="text-gray-500 dark:text-gray-500">Category</p>
              <p class="font-medium text-gray-800 dark:text-gray-300 mt-1">{{ material.category || 'General' }}</p>
            </div>
            <div class="bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-md p-2">
              <p class="text-gray-500 dark:text-gray-500">Availability</p>
              <p class="font-medium text-gray-800 dark:text-gray-300 mt-1">{{ material.available_copies || 0 }} copies</p>
            </div>
            <div class="bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-md p-2">
              <p class="text-gray-500 dark:text-gray-500">Total Copies</p>
              <p class="font-medium text-gray-800 dark:text-gray-300 mt-1">{{ material.total_copies || 0 }}</p>
            </div>
            <div class="bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-md p-2">
              <p class="text-gray-500 dark:text-gray-500">ISBN</p>
              <p class="font-medium text-gray-800 dark:text-gray-300 mt-1">{{ material.isbn || 'N/A' }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Selected Member -->
      <div class="space-y-2">
        <div class="flex items-center justify-between">
          <p class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Member</p>
          <button 
            @click="emit('change-member')"
            class="text-xs px-3 py-1.5 rounded-lg border border-amber-200 dark:border-amber-800 text-amber-700 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/50 hover:bg-amber-100 dark:hover:bg-amber-900 font-medium transition-all duration-200"
          >
            {{ member ? 'Change Member' : 'Select Member' }}
          </button>
        </div>
        
        <div v-if="member" class="bg-gray-50 dark:bg-slate-900 rounded-xl p-3 border border-gray-200 dark:border-slate-700">
          <div class="flex items-start gap-3">
            <div class="bg-purple-100 dark:bg-purple-950 p-2 rounded-lg">
              <BaseIcon :path="mdiAccount" size="20" class="text-purple-600 dark:text-purple-400" />
            </div>
            <div class="flex-1">
              <p class="font-medium text-gray-900 dark:text-white text-sm">
                {{ member.first_name }} {{ member.last_name }}
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">{{ member.id_number }}</p>
            </div>
          </div>
        </div>

        <div v-else class="bg-amber-50 dark:bg-amber-950/30 rounded-xl p-4 border border-amber-200 dark:border-amber-800">
          <div class="flex items-center gap-2">
            <BaseIcon :path="mdiAlertCircle" size="18" class="text-amber-600 dark:text-amber-400" />
            <p class="text-sm text-amber-800 dark:text-amber-300">No member selected</p>
          </div>
          <button
            @click="emit('change-member')"
            class="mt-3 w-full text-sm px-3 py-2 rounded-lg bg-gradient-to-r from-amber-500 to-orange-500 text-white hover:from-amber-600 hover:to-orange-600 font-medium transition-all duration-200 shadow-sm"
          >
            Select Member
          </button>
        </div>
      </div>

      <!-- Borrow Details -->
      <div class="space-y-2">
        <p class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Borrow Details</p>
        <div class="bg-gray-50 dark:bg-slate-900 rounded-xl p-3 border border-gray-200 dark:border-slate-700 space-y-2">
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-600 dark:text-gray-400 flex items-center gap-1">
              <BaseIcon :path="mdiCalendar" size="14" class="text-gray-400 dark:text-gray-500" />
              Borrow Date
            </span>
            <span class="font-medium text-gray-900 dark:text-white">{{ new Date().toLocaleDateString() }}</span>
          </div>
          <div class="flex items-center justify-between text-sm">
            <span class="text-gray-600 dark:text-gray-400 flex items-center gap-1">
              <BaseIcon :path="mdiClockOutline" size="14" class="text-gray-400 dark:text-gray-500" />
              Due Date
            </span>
            <span class="font-medium text-amber-600 dark:text-amber-400">{{ dueDate }}</span>
          </div>
        </div>
      </div>

      <!-- Submit Button -->
      <button
        class="w-full py-3 bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white rounded-xl font-medium transition-all duration-300 disabled:opacity-60 disabled:cursor-not-allowed shadow-md hover:shadow-lg flex items-center justify-center gap-2"
        :disabled="!isComplete"
        @click="emit('submit')"
      >
        <BaseIcon :path="mdiCheckCircle" size="18" />
        Complete Borrow
      </button>

      <p v-if="!isComplete" class="text-xs text-center text-gray-500 dark:text-gray-500">
        Select both material and member to continue
      </p>
    </div>
  </div>
</template>