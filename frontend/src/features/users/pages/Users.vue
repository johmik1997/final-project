<script setup>
import { ref, watch, computed, onMounted, onBeforeUnmount } from 'vue';
import Table from '@/components/Table.vue';
import { useUsers } from '../store/userStore';
import { useApiRequest } from '@/composables/useApiRequest';
import { getAllUser, removeUserById, verifyUser } from '../Api/UserApi';
import { toasted } from '@/utils/utils';
import { openModal } from '@customizer/modal-x';
import BaseIcon from '@/components/base/BaseIcon.vue';
import { 
  mdiPencil, 
  mdiDeleteAlert, 
  mdiCheckDecagram, 
  mdiBagPersonalPlus, 
  mdiNaturePeople, 
  mdiHuman,
  mdiMagnify,
  mdiFilter,
  mdiRefresh,
  mdiAccountCheck,
  mdiAccountCancel,
  mdiShieldAccount,
  mdiShieldAccountVariant,
  mdiEmail,
  mdiPhone,
  mdiIdentifier
} from '@mdi/js';
import { usePaginations } from '@/composables/usePaginationTemp';
import { emitEntityMutation, subscribeEntityMutation } from '@/utils/entitySync';

const usersStore = useUsers();
let unsubscribeEntitySync = () => {};
const selectedUser = ref(null);
const roleFilter = ref('');
const statusFilter = ref('');
const searchQuery = ref('');
const searchTimeout = ref(null);

// Role options for filter
const roleOptions = [
  { value: 'MEMBER', label: 'Member', icon: mdiHuman, color: 'blue' },
  { value: 'ADMIN', label: 'Admin', icon: mdiShieldAccount, color: 'purple' },
  { value: 'SUPER ADMIN', label: 'Super Admin', icon: mdiShieldAccountVariant, color: 'red' },
  { value: 'TECHNICAL STAFF', label: 'Technical Staff', icon: mdiNaturePeople, color: 'green' },
  { value: 'STACK STAFF', label: 'Stack Staff', icon: mdiAccountCheck, color: 'emerald' },
  { value: 'FRONT DESK STAFF', label: 'Front Desk Staff', icon: mdiAccountCheck, color: 'teal' },
  { value: 'DEPARTMENT HEAD', label: 'Department Head', icon: mdiBagPersonalPlus, color: 'orange' }
];

// Status options
const statusOptions = [
  { value: 'ACTIVE', label: 'Active', color: 'green' },
  { value: 'INACTIVE', label: 'Inactive', color: 'gray' },
  { value: 'PENDING', label: 'Pending', color: 'yellow' },
  { value: 'BLOCKED', label: 'Blocked', color: 'red' }
];

function getUserId(user) {
  return user?.userUuid || user?.id;
}

function getPhone(user) {
  return user?.phone || user?.mobilePhone || "";
}

function getFullName(user) {
  const first = user?.first_name;
  const last = user?.last_name;
  console.log(first)
  return [first, last].filter(Boolean).join(' ');
}

// Enhanced pagination with filters
const pagination = usePaginations({
  store: usersStore,
  cb: (query) => {
    const filters = {
      ...query,
      role: roleFilter.value || '',
      search: searchQuery.value || ''
    };
    return getAllUser(filters);
  },
});

onMounted(() => {
  unsubscribeEntitySync = subscribeEntityMutation('users', () => {
    pagination.refresh();
  });
});

onBeforeUnmount(() => {
  unsubscribeEntitySync?.();
});

// Watch for filter changes
watch([roleFilter, statusFilter], () => {
  pagination.goToPage(1);
});

// Debounced search
watch(searchQuery, (newVal) => {
  clearTimeout(searchTimeout.value);
  searchTimeout.value = setTimeout(() => {
    pagination.goToPage(1);
  }, 500);
});

// Reset all filters
function resetFilters() {
  roleFilter.value = '';
  statusFilter.value = '';
  searchQuery.value = '';
}

// Active filters count
const activeFiltersCount = computed(() => {
  let count = 0;
  if (roleFilter.value) count++;
  if (statusFilter.value) count++;
  if (searchQuery.value) count++;
  return count;
});

// Get role badge color
function getRoleColor(role) {
  const found = roleOptions.find(r => r.value === role);
  return found?.color || 'gray';
}

// Get status badge color
function getStatusColor(status) {
  const found = statusOptions.find(s => s.value === status);
  return found?.color || 'gray';
}

const removeReq = useApiRequest();
function remove(id) {
  openModal(
    'Confirmation',
    {
      title: 'Remove User',
      message: 'Are you sure you want to delete this user?',
      confirmText: 'Delete',
      cancelText: 'Cancel',
      type: 'danger'
    },
    (confirm) => {
      if (confirm) {
        removeReq.send(
          () => removeUserById(id),
          (res) => {
            if (res?.success) {
              usersStore.remove(id);
              emitEntityMutation('users', { action: 'deleted', id });
              toasted(true, 'User removed successfully');
              pagination.refresh();
            } else {
              toasted(false, 'Failed to remove user', res?.error || 'Unknown error');
            }
          }
        );
      }
    }
  );
}

const verifyReq = useApiRequest();
function openVerifyModal(user) {
  selectedUser.value = user;
  openModal(
    'VerificationModal',
    {
      title: 'Verify User',
      message: `Enter verification code sent to ${getPhone(user)}`,
      inputLabel: 'Verification Code',
      inputPlaceholder: 'Enter 6-digit code',
      inputType: 'text',
      inputPattern: '[0-9]{6}',
      confirmText: 'Verify',
      cancelText: 'Cancel'
    },
    (code) => {
      if (code) verifyUserCode(getPhone(user), code);
    }
  );
}

function verifyUserCode(phone, code) {
  verifyReq.send(
    () => verifyUser(phone, code),
    (res) => {
      if (res?.success) {
        usersStore.updateVerification(getUserId(selectedUser.value), true);
        emitEntityMutation('users', { action: 'verified', id: getUserId(selectedUser.value) });
        toasted(true, 'User verified successfully');
        pagination.refresh();
      } else {
        toasted(false, 'Verification failed', res?.error || 'Invalid code');
      }
    }
  );
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50/30 dark:from-slate-950 dark:to-slate-900 p-4 sm:p-6">
    <!-- Header -->
    <div class="mb-6">
      <div class="flex items-center gap-3 mb-2">
        <div class="p-2.5 bg-gradient-to-br from-gray-500 to-gray-600 dark:from-gray-600 dark:to-gray-700 rounded-xl shadow-lg shadow-gray-200 dark:shadow-slate-900/50">
          <BaseIcon :path="mdiHuman" size="28" class="text-white" />
        </div>
        <div>
          <h1 class="text-2xl font-bold bg-gradient-to-r from-gray-600 to-gray-800 dark:from-gray-400 dark:to-gray-200 bg-clip-text text-transparent">
            User Management
          </h1>
          <p class="text-gray-500 dark:text-slate-400 text-sm">Manage users, roles, and permissions</p>
        </div>
      </div>
    </div>
    
    <!-- Filters and Actions Card -->
    <div class="bg-white/80 dark:bg-slate-900/80 backdrop-blur-sm rounded-xl border border-gray-100 dark:border-slate-800 shadow-lg mb-6 overflow-hidden">
      <!-- Search Bar -->
      <div class="p-4 border-b border-gray-100 dark:border-slate-800">
        <div class="flex flex-col gap-3 lg:flex-row lg:items-center">
          <div class="flex-1">
            <div class="relative">
              <BaseIcon 
                :path="mdiMagnify" 
                size="18" 
                class="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 dark:text-slate-500"
              />
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search by name, ID, email, or phone..."
                class="w-3/4 rounded-lg border border-gray-200 dark:border-slate-700 bg-white dark:bg-slate-800 py-2.5 pl-9 pr-4 text-sm text-gray-900 dark:text-slate-100 transition-all focus:border-gray-400 dark:focus:border-slate-600 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:focus:ring-slate-700"
              />
            </div>
          </div>
          
          <!-- Active Filters Badge -->
          <div class="flex flex-wrap items-center gap-3">
            <button
              @click="openModal('AddUser')"
              class="flex items-center gap-2 whitespace-nowrap rounded-lg bg-gradient-to-r from-orange-600 to-orange-700 dark:from-orange-700 dark:to-orange-800 px-4 py-2.5 text-sm font-medium text-white shadow-md shadow-gray-200 dark:shadow-slate-900 transition-all hover:from-gray-700 hover:to-gray-800 dark:hover:from-gray-600 dark:hover:to-gray-700"
            >
              <svg width="14" height="14" viewBox="0 0 12 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M6 0V14M0 7H12" stroke="white" stroke-width="2"/>
              </svg>
              <span>Add New User</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Filter Options -->
      <div class="grid grid-cols-1 gap-3 p-4 sm:grid-cols-2 lg:grid-cols-4">
        <!-- Role Filter -->
        <div class="mr-8">
          <label class="block text-xs font-medium text-gray-500 dark:text-slate-400 mb-1.5 flex items-center gap-1">
            <BaseIcon :path="mdiFilter" size="12" />
            Role
          </label>
          <select
            v-model="roleFilter"
            class="w-full mr-12 border border-gray-200 dark:border-slate-700 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-gray-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:focus:ring-slate-700 focus:border-gray-400 dark:focus:border-slate-600 transition-all text-sm"
          >
            <option value="">All Roles</option>
            <option v-for="role in roleOptions" :key="role.value" :value="role.value">
              {{ role.label }}
            </option>
          </select>
        </div>

        <!-- Status Filter -->
        <div class="mr-12"> 
          <label class="block text-xs font-medium text-gray-500 dark:text-slate-400 mb-1.5 flex items-center gap-1">
            <BaseIcon :path="mdiFilter" size="12" />
            Status
          </label>
          <select
            v-model="statusFilter"
            class="w-full border border-gray-200 dark:border-slate-700 rounded-lg px-3 py-2 bg-white dark:bg-slate-800 text-gray-900 dark:text-slate-100 focus:outline-none focus:ring-2 focus:ring-gray-200 dark:focus:ring-slate-700 focus:border-gray-400 dark:focus:border-slate-600 transition-all text-sm"
          >
            <option value="">All Status</option>
            <option v-for="status in statusOptions" :key="status.value" :value="status.value">
              {{ status.label }}
            </option>
          </select>
        </div>

        <!-- Stats Cards -->
        <div class="sm:col-span-2 grid grid-cols-2 gap-3">
          <div class="bg-gradient-to-br from-green-50 to-green-100/50 dark:from-green-950/30 dark:to-green-900/20 rounded-lg p-3 border border-green-200 dark:border-green-800/50">
            <p class="text-xs text-green-700 dark:text-green-400">Total Users</p>
            <p class="text-xl font-bold text-green-800 dark:text-green-300">{{ usersStore.users?.length || 0 }}</p>
          </div>
          <div class="bg-gradient-to-br from-blue-50 to-blue-100/50 dark:from-blue-950/30 dark:to-blue-900/20 rounded-lg p-3 border border-blue-200 dark:border-blue-800/50">
            <p class="text-xs text-blue-700 dark:text-blue-400">Active Now</p>
            <p class="text-xl font-bold text-blue-800 dark:text-blue-300">
              {{ usersStore.users?.filter(u => u.status === 'ACTIVE').length || 0 }}
            </p>
          </div>
        </div>
      </div>
    </div>
    
  <!-- Users Table -->
<div class="bg-white dark:bg-slate-900 rounded-xl border border-gray-100 dark:border-slate-800 shadow-lg overflow-hidden">
  <div class="border-b border-gray-100 dark:border-slate-800">
    
  <Table
  class="table-fixed w-full"
  :pending="pagination.pending.value"
  :pagination="pagination.meta.value"
  @next-page="pagination.next"
  @prev-page="pagination.previous"
  @page-change="pagination.goToPage"
  @page-size-change="pagination.setPerPage"
  :headers="{
    head: [
      'User',
      'ID Number',
      'Email',
      'Phone',
      'Library',
      'Role',
      'Status',
      'Actions'
    ],
    row: [
      'first_name',
      'id_number',
      'email',
      'phone',
      'library_name',
      'role',
      'status'
    ]
  }"
  :rows="usersStore.users || []"
>

  <!-- Actions -->
  <template #actions="{ row }">
    <div class="flex items-center justify-center gap-2 w-[110px]">

      <button
        class="p-2 rounded-lg bg-blue-50 dark:bg-blue-950/50 text-blue-600 dark:text-blue-400 hover:bg-blue-600 hover:text-white dark:hover:bg-blue-600 transition-all duration-200"
        @click="openModal('EditUser', { user: row })"
      >
        <BaseIcon :path="mdiPencil" size="18" />
      </button>

      <button
        class="p-2 rounded-lg bg-red-50 dark:bg-red-950/50 text-red-600 dark:text-red-400 hover:bg-red-600 hover:text-white dark:hover:bg-red-600 transition-all duration-200"
        @click="remove(getUserId(row))"
      >
        <BaseIcon :path="mdiDeleteAlert" size="18" />
      </button>

    </div>
  </template>

  <!-- Empty State -->
  <template #empty>
    <div class="flex flex-col items-center justify-center py-14">
      <BaseIcon
        :path="mdiHuman"
        size="48"
        class="text-gray-300 dark:text-slate-600 mb-3"
      />

      <p class="text-gray-600 dark:text-slate-400 font-medium">
        No users found
      </p>

      <p class="text-sm text-gray-400 dark:text-slate-500">
        Try changing filters or search
      </p>
    </div>
  </template>

</Table>
  </div>
</div>
  </div>
</template>

<style scoped>
/* Smooth transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Custom scrollbar - Light mode */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}

/* Custom scrollbar - Dark mode */
@media (prefers-color-scheme: dark) {
  ::-webkit-scrollbar-track {
    background: #1e293b;
  }
  
  ::-webkit-scrollbar-thumb {
    background: #475569;
  }
  
  ::-webkit-scrollbar-thumb:hover {
    background: #64748b;
  }
}
.dark ::-webkit-scrollbar-track {
  background: #1e293b;
}

.dark ::-webkit-scrollbar-thumb {
  background: #475569;
}

.dark ::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}

/* Prevent text wrapping in table cells */
:deep(td) {
  white-space: nowrap;
}

/* Dark mode table cell text */
.dark :deep(td) {
  @apply text-slate-200;
}

.dark :deep(th) {
  @apply text-slate-300;
}

/* Responsive table container */
@media (max-width: 768px) {
  .overflow-x-auto {
    overflow-x: auto;
  }
}
</style>