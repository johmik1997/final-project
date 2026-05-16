<script setup>
import { ref, computed } from 'vue';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { 
  mdiMagnify, 
  mdiAccount, 
  mdiClose, 
  mdiEmail, 
  mdiPhone, 
  mdiCardAccountDetails,
  mdiBook,
  mdiAccountGroup,
  mdiChevronRight,
  mdiBadgeAccount
} from '@mdi/js';

const props = defineProps({
  members: {
    type: Array,
    default: () => [],
  }
});

const emit = defineEmits(['select', 'close']);

const searchQuery = ref('');

const filteredMembers = computed(() => {
  if (!searchQuery.value) return props.members;
  const query = searchQuery.value.toLowerCase();
  return props.members.filter(member => 
    `${member.first_name} ${member.last_name}`.toLowerCase().includes(query) ||
    member.id_number?.toLowerCase().includes(query) ||
    member.email?.toLowerCase().includes(query)
  );
});

function getInitials(member) {
  const first = member.first_name?.charAt(0) || '';
  const last = member.last_name?.charAt(0) || '';
  return (first + last).toUpperCase();
}

function getRandomGradient(index) {
  const gradients = [
    'from-amber-500 to-orange-500',
    'from-emerald-500 to-teal-500',
    'from-blue-500 to-indigo-500',
    'from-purple-500 to-pink-500',
    'from-rose-500 to-red-500'
  ];
  return gradients[index % gradients.length];
}
</script>

<template>
  <div 
    class="fixed inset-0 bg-black/60 backdrop-blur-md flex items-center justify-center z-50 p-4 transition-all duration-300"
    @click.self="$emit('close')"
  >
    <div class="bg-white dark:bg-slate-800 rounded-2xl w-full max-w-2xl max-h-[90vh] overflow-hidden shadow-2xl transform transition-all duration-300 scale-100">
      
      <!-- Header -->
      <div class="bg-gradient-to-r from-amber-500 to-orange-500 px-6 py-5">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="bg-white/20 p-2.5 rounded-xl backdrop-blur-sm">
              <BaseIcon :path="mdiAccountGroup" size="22" class="text-white" />
            </div>
            <div>
              <h3 class="text-xl font-bold text-white">Select Member</h3>
              <p class="text-sm text-white/80 mt-0.5">Choose a member for this transaction</p>
            </div>
          </div>
          <button 
            @click="$emit('close')" 
            class="p-2 hover:bg-white/20 rounded-xl transition-all duration-200 hover:scale-110"
          >
            <BaseIcon :path="mdiClose" size="20" class="text-white" />
          </button>
        </div>
      </div>

      <!-- Search Section -->
      <div class="p-5 border-b border-gray-200 dark:border-slate-700 bg-gray-50/50 dark:bg-slate-900/30">
        <div class="relative">
          <BaseIcon 
            :path="mdiMagnify" 
            size="18" 
            class="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 dark:text-gray-500"
          />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search by name, ID, or email..."
            class="w-full pl-11 pr-4 py-3 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl focus:ring-2 focus:ring-amber-400 focus:border-amber-400 outline-none text-sm text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500 transition-all duration-200"
            autofocus
          />
        </div>
      </div>

      <!-- Members List -->
      <div class="overflow-y-auto p-5" style="max-height: 420px;">
        <div v-if="filteredMembers.length === 0" class="text-center py-16">
          <div class="bg-gray-100 dark:bg-slate-700 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <BaseIcon :path="mdiAccount" size="32" class="text-gray-400 dark:text-gray-500" />
          </div>
          <p class="text-gray-600 dark:text-gray-400 font-medium">No members found</p>
          <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">Try a different search term</p>
        </div>

        <div v-else class="space-y-3">
          <div
            v-for="(member, index) in filteredMembers"
            :key="member.id"
            @click="$emit('select', member)"
            class="group relative p-4 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-xl hover:border-amber-300 dark:hover:border-amber-700 hover:shadow-lg transition-all duration-300 cursor-pointer overflow-hidden"
          >
            <!-- Hover Background Effect -->
            <div class="absolute inset-0 bg-gradient-to-r from-amber-50/0 to-orange-50/0 group-hover:from-amber-50/30 group-hover:to-orange-50/30 dark:group-hover:from-amber-950/20 dark:group-hover:to-orange-950/20 transition-all duration-300"></div>
            
            <div class="relative flex items-center gap-4">
              <!-- Avatar with Gradient -->
              <div 
                class="w-14 h-14 rounded-xl flex items-center justify-center flex-shrink-0 text-white font-bold text-lg shadow-md transition-transform group-hover:scale-105 duration-300"
                :class="`bg-gradient-to-br ${getRandomGradient(index)}`"
              >
                {{ getInitials(member) }}
              </div>

              <!-- Member Info -->
              <div class="flex-1 min-w-0">
                <div class="flex items-center justify-between mb-1.5 flex-wrap gap-2">
                  <h4 class="font-semibold text-gray-900 dark:text-white group-hover:text-amber-600 dark:group-hover:text-amber-400 transition-colors text-base">
                    {{ member.first_name }} {{ member.last_name }}
                  </h4>
                  <span class="text-[10px] font-semibold bg-green-100 dark:bg-green-900/50 text-green-700 dark:text-green-300 px-2.5 py-1 rounded-full">
                    Active Member
                  </span>
                </div>
                
                <div class="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-gray-500 dark:text-gray-400">
                  <span class="flex items-center gap-1.5">
                    <BaseIcon :path="mdiCardAccountDetails" size="12" class="text-amber-500 dark:text-amber-400" />
                    <span class="font-mono">{{ member.id_number || 'N/A' }}</span>
                  </span>
                  <span v-if="member.email" class="flex items-center gap-1.5">
                    <BaseIcon :path="mdiEmail" size="12" class="text-amber-500 dark:text-amber-400" />
                    <span>{{ member.email }}</span>
                  </span>
                  <span v-if="member.phone" class="flex items-center gap-1.5">
                    <BaseIcon :path="mdiPhone" size="12" class="text-amber-500 dark:text-amber-400" />
                    <span>{{ member.phone }}</span>
                  </span>
                </div>

                <!-- Member Stats -->
                <div class="flex items-center gap-4 mt-2 text-[10px] text-gray-400 dark:text-gray-500">
                  <span class="flex items-center gap-1">
                    <BaseIcon :path="mdiBook" size="10" />
                    Books borrowed: {{ member.borrowed_count || 0 }}
                  </span>
                </div>
              </div>

              <!-- Select Button -->
              <div class="flex-shrink-0">
                <button class="px-4 py-2 bg-gradient-to-r from-amber-500 to-orange-500 text-white rounded-xl text-sm font-medium shadow-md hover:from-amber-600 hover:to-orange-600 transition-all duration-300 group-hover:scale-105 flex items-center gap-2">
                  Select
                  <BaseIcon :path="mdiChevronRight" size="14" class="group-hover:translate-x-0.5 transition-transform" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="px-5 py-3 border-t border-gray-200 dark:border-slate-700 bg-gray-50/50 dark:bg-slate-900/30">
        <div class="flex items-center justify-between">
          <p class="text-xs text-gray-500 dark:text-gray-400">
            Showing <span class="font-medium text-gray-700 dark:text-gray-300">{{ filteredMembers.length }}</span> of 
            <span class="font-medium text-gray-700 dark:text-gray-300">{{ props.members.length }}</span> members
          </p>
          <p class="text-xs text-amber-600 dark:text-amber-400 flex items-center gap-1">
            <BaseIcon :path="mdiBadgeAccount" size="12" />
            Click on any member to select
          </p>
        </div>
      </div>
    </div>
  </div>
</template>