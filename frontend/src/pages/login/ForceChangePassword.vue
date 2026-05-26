<template>
  <div class="min-h-screen w-full relative overflow-auto transition-colors duration-300" :class="isDarkTheme ? 'bg-slate-900' : 'bg-gray-50'">
    <div class="absolute inset-0 transition-colors duration-300" :class="isDarkTheme ? 'bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900' : 'bg-gradient-to-br from-gray-100 via-gray-50 to-gray-100'"></div>

    <div class="relative z-10 min-h-screen flex items-center justify-center p-4">
      <div class="w-full max-w-md">
        <div class="text-center mb-8">
          <h1 class="text-3xl font-bold" :class="isDarkTheme ? 'text-white' : 'text-slate-800'">Set Your Password</h1>
          <p class="mt-2" :class="isDarkTheme ? 'text-slate-400' : 'text-slate-500'">
            For security, choose a new password before continuing.
          </p>
        </div>

        <div class="rounded-2xl backdrop-blur-sm p-6 sm:p-8 shadow-2xl transition-all duration-300" :class="isDarkTheme ? 'bg-slate-800/60 border-white/10' : 'bg-white/90 border-gray-200 shadow-xl'">
          <form @submit.prevent="handleSubmit">
            <div class="space-y-5">
              <div>
                <label class="block text-sm font-medium mb-2" :class="isDarkTheme ? 'text-slate-300' : 'text-slate-700'">New Password</label>
                <input
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  required
                  class="w-full px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500"
                  :class="isDarkTheme ? 'bg-slate-900 border-white/10 text-white' : 'bg-gray-50 border-gray-200 text-slate-800'"
                  placeholder="Enter new password"
                  :disabled="loading"
                />
              </div>

              <div>
                <label class="block text-sm font-medium mb-2" :class="isDarkTheme ? 'text-slate-300' : 'text-slate-700'">Confirm Password</label>
                <input
                  v-model="form.confirm_password"
                  :type="showConfirmPassword ? 'text' : 'password'"
                  required
                  class="w-full px-4 py-3 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500"
                  :class="isDarkTheme ? 'bg-slate-900 border-white/10 text-white' : 'bg-gray-50 border-gray-200 text-slate-800'"
                  placeholder="Confirm new password"
                  :disabled="loading"
                />
              </div>

              <button
                type="submit"
                :disabled="!isFormValid || loading"
                class="w-full bg-gradient-to-r from-amber-500 to-red-500 text-white font-semibold py-3 rounded-xl hover:shadow-lg transition-all disabled:opacity-50"
              >
                {{ loading ? 'Saving...' : 'Save Password' }}
              </button>
            </div>
          </form>

          <p v-if="message" class="mt-4 text-sm text-center" :class="messageType === 'error' ? 'text-red-500' : 'text-emerald-500'">
            {{ message }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '@/stores/auth';
import { toasted } from '@/utils/utils';
import { firstLoginChangePassword } from './api/LoginApi';

const router = useRouter();
const auth = useAuth();
const isDarkTheme = ref(true);
const showPassword = ref(false);
const showConfirmPassword = ref(false);
const loading = ref(false);
const message = ref('');
const messageType = ref('success');
const form = ref({ password: '', confirm_password: '' });

onMounted(() => {
  const savedTheme = localStorage.getItem('theme');
  isDarkTheme.value = savedTheme !== 'light';
  if (!auth.auth?.accessToken) {
    router.replace('/login');
  }
});

const isFormValid = computed(() => {
  const password = form.value.password;
  const confirm = form.value.confirm_password;
  return (
    password.length >= 8 &&
    /[A-Z]/.test(password) &&
    /[a-z]/.test(password) &&
    /[0-9]/.test(password) &&
    password === confirm
  );
});

async function handleSubmit() {
  if (!isFormValid.value) {
    message.value = 'Please meet all password requirements.';
    messageType.value = 'error';
    return;
  }

  loading.value = true;
  message.value = '';

  try {
    const res = await firstLoginChangePassword({
      password: form.value.password,
      confirm_password: form.value.confirm_password,
    });

    if (res?.success || res?.status === 200) {
      const user = auth.auth?.user || {};
      user.must_change_password = false;
      auth.setAuth({ ...auth.auth, user });
      localStorage.setItem('userDetail', JSON.stringify(auth.auth));
      toasted(true, 'Password updated. Welcome!');
      router.replace('/app/dashboard');
      return;
    }

    const errorMsg = res?.error || res?.data?.detail || 'Failed to update password';
    message.value = errorMsg;
    messageType.value = 'error';
    toasted(false, errorMsg);
  } catch (error) {
    const errorMsg = error?.response?.data?.detail || error?.message || 'Failed to update password';
    message.value = errorMsg;
    messageType.value = 'error';
    toasted(false, errorMsg);
  } finally {
    loading.value = false;
  }
}
</script>
