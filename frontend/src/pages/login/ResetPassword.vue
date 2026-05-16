<template>
  <div class="min-h-screen w-full relative overflow-auto transition-colors duration-300" :class="isDarkTheme ? 'bg-slate-900' : 'bg-gray-50'">
    <!-- Animated Background Gradient -->
    <div class="absolute inset-0 transition-colors duration-300" :class="isDarkTheme ? 'bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900' : 'bg-gradient-to-br from-gray-100 via-gray-50 to-gray-100'"></div>
    
    <!-- Decorative Blur Elements -->
    <div class="absolute top-20 left-10 w-72 h-72 rounded-full blur-3xl" :class="isDarkTheme ? 'bg-amber-500/10' : 'bg-amber-500/20'"></div>
    <div class="absolute bottom-20 right-10 w-96 h-96 rounded-full blur-3xl" :class="isDarkTheme ? 'bg-red-500/5' : 'bg-red-500/10'"></div>
    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] rounded-full blur-3xl" :class="isDarkTheme ? 'bg-amber-500/5' : 'bg-amber-500/10'"></div>

    <!-- Theme Toggle Button -->
    <button 
      @click="toggleTheme" 
      class="fixed top-4 right-4 z-20 p-2 rounded-lg transition-colors" 
      :class="isDarkTheme ? 'text-amber-400 hover:bg-white/10' : 'text-amber-500 hover:bg-gray-200'"
      aria-label="Toggle theme"
    >
      <svg v-if="isDarkTheme" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
      </svg>
      <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z"></path>
      </svg>
    </button>

    <div class="relative z-10 min-h-screen flex items-center justify-center p-4">
      <div class="w-full max-w-md">
        <!-- Header -->
        <div class="text-center mb-8">
          <div class="flex justify-center mb-4">
            <div class="flex items-center space-x-2">
              <img 
                src="@/assets/logolib.jpg" 
                alt="Logo" 
                class="w-16 h-16 rounded-full object-cover border-2 border-amber-500 shadow-lg shadow-amber-500/30"
              >
              <span class="font-bold text-xl" :class="isDarkTheme ? 'text-white' : 'text-slate-800'">HU<span class="text-amber-500">-DLRBS</span></span>
            </div>
          </div>
          <h1 class="text-3xl font-bold" :class="isDarkTheme ? 'text-white' : 'text-slate-800'">Reset Password</h1>
          <p class="mt-2" :class="isDarkTheme ? 'text-slate-400' : 'text-slate-500'">Create a new password for your account</p>
        </div>

        <!-- Reset Password Form Card -->
        <div class="rounded-2xl backdrop-blur-sm p-6 sm:p-8 shadow-2xl transition-all duration-300" :class="isDarkTheme ? 'bg-slate-800/60 border-white/10' : 'bg-white/90 border-gray-200 shadow-xl'">
          <form @submit.prevent="handleResetPassword">
            <div class="space-y-5">
              <!-- Email Display -->
              <div class="rounded-xl p-3 text-center transition-colors" :class="isDarkTheme ? 'bg-slate-900/50 border-white/5' : 'bg-gray-100/80 border-gray-200'">
                <p class="text-sm" :class="isDarkTheme ? 'text-slate-400' : 'text-slate-500'">
                  Resetting password for: <span class="font-medium text-amber-500">{{ email }}</span>
                </p>
              </div>

              <!-- New Password Input -->
              <div>
                <label class="block text-sm font-medium mb-2" :class="isDarkTheme ? 'text-slate-300' : 'text-slate-700'">
                  New Password
                </label>
                <div class="relative">
                  <input
                    :type="showNewPassword ? 'text' : 'password'"
                    v-model="form.new_password"
                    required
                    class="w-full px-4 py-3 rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent pr-12"
                    :class="isDarkTheme ? 'bg-slate-900 border-white/10 text-white placeholder-slate-500' : 'bg-gray-50 border-gray-200 text-slate-800 placeholder-slate-400'"
                    placeholder="Enter new password"
                    :disabled="loading"
                  />
                  <button
                    type="button"
                    @click="showNewPassword = !showNewPassword"
                    class="absolute right-3 top-1/2 transform -translate-y-1/2 transition-colors"
                    :class="isDarkTheme ? 'text-slate-400 hover:text-amber-500' : 'text-slate-500 hover:text-amber-600'"
                  >
                    <svg v-if="!showNewPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Confirm Password Input -->
              <div>
                <label class="block text-sm font-medium mb-2" :class="isDarkTheme ? 'text-slate-300' : 'text-slate-700'">
                  Confirm Password
                </label>
                <div class="relative">
                  <input
                    :type="showConfirmPassword ? 'text' : 'password'"
                    v-model="form.confirm_password"
                    required
                    class="w-full px-4 py-3 rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent pr-12"
                    :class="isDarkTheme ? 'bg-slate-900 border-white/10 text-white placeholder-slate-500' : 'bg-gray-50 border-gray-200 text-slate-800 placeholder-slate-400'"
                    placeholder="Confirm new password"
                    :disabled="loading"
                  />
                  <button
                    type="button"
                    @click="showConfirmPassword = !showConfirmPassword"
                    class="absolute right-3 top-1/2 transform -translate-y-1/2 transition-colors"
                    :class="isDarkTheme ? 'text-slate-400 hover:text-amber-500' : 'text-slate-500 hover:text-amber-600'"
                  >
                    <svg v-if="!showConfirmPassword" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Password Requirements -->
              <div class="rounded-xl p-4 transition-colors" :class="isDarkTheme ? 'bg-slate-900/50 border-white/5' : 'bg-gray-100/80 border-gray-200'">
                <p class="text-xs font-medium mb-2" :class="isDarkTheme ? 'text-slate-300' : 'text-slate-700'">Password must contain:</p>
                <ul class="space-y-1">
                  <li class="flex items-center gap-2 text-xs" :class="passwordValid.length ? 'text-emerald-400' : (isDarkTheme ? 'text-slate-500' : 'text-slate-400')">
                    <svg v-if="passwordValid.length" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                    At least 8 characters
                  </li>
                  <li class="flex items-center gap-2 text-xs" :class="passwordValid.hasUpperCase ? 'text-emerald-400' : (isDarkTheme ? 'text-slate-500' : 'text-slate-400')">
                    <svg v-if="passwordValid.hasUpperCase" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                    At least one uppercase letter
                  </li>
                  <li class="flex items-center gap-2 text-xs" :class="passwordValid.hasLowerCase ? 'text-emerald-400' : (isDarkTheme ? 'text-slate-500' : 'text-slate-400')">
                    <svg v-if="passwordValid.hasLowerCase" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                    At least one lowercase letter
                  </li>
                  <li class="flex items-center gap-2 text-xs" :class="passwordValid.hasNumber ? 'text-emerald-400' : (isDarkTheme ? 'text-slate-500' : 'text-slate-400')">
                    <svg v-if="passwordValid.hasNumber" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                    <svg v-else class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                    At least one number
                  </li>
                </ul>
              </div>

              <!-- Submit Button -->
              <button
                type="submit"
                :disabled="!isFormValid || loading"
                class="w-full bg-gradient-to-r from-amber-500 to-red-500 text-white font-semibold py-3 rounded-xl hover:shadow-lg hover:shadow-amber-500/25 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="loading" class="flex items-center justify-center gap-2">
                  <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Resetting...
                </span>
                <span v-else>Reset Password</span>
              </button>
            </div>
          </form>

          <!-- Back to Login Link -->
          <div class="mt-6 text-center">
            <router-link to="/login" class="text-sm transition-colors inline-flex items-center gap-1" :class="isDarkTheme ? 'text-amber-500 hover:text-amber-400' : 'text-amber-600 hover:text-amber-700'">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
              </svg>
              Back to Login
            </router-link>
          </div>

          <!-- Message Display -->
          <div v-if="message" class="mt-4">
            <p :class="[
              'text-sm text-center p-3 rounded-xl',
              messageType === 'error' 
                ? (isDarkTheme ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-red-100 text-red-700 border border-red-200')
                : (isDarkTheme ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-emerald-100 text-emerald-700 border border-emerald-200')
            ]">
              {{ message }}
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { toasted } from "@/utils/utils";
import { resetPassword } from "./api/LoginApi";

const router = useRouter();

// Theme state
const isDarkTheme = ref(true);

// Toggle theme function
function toggleTheme() {
  isDarkTheme.value = !isDarkTheme.value;
  localStorage.setItem('theme', isDarkTheme.value ? 'dark' : 'light');
  if (isDarkTheme.value) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
}

// Load saved theme
function loadSavedTheme() {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'light') {
    isDarkTheme.value = false;
    document.documentElement.classList.remove('dark');
  } else {
    isDarkTheme.value = true;
    document.documentElement.classList.add('dark');
  }
}

const email = ref("");
const confirmationToken = ref("");
const form = ref({
  new_password: "",
  confirm_password: ""
});
const showNewPassword = ref(false);
const showConfirmPassword = ref(false);
const loading = ref(false);
const message = ref("");
const messageType = ref("success");

onMounted(() => {
  loadSavedTheme();
  
  const storedEmail = localStorage.getItem("resetEmail");
  const storedOtp = localStorage.getItem("resetOtp");
  const storedConfirmationToken = localStorage.getItem("confirmationToken");
  
  if (storedEmail && storedOtp && storedConfirmationToken) {
    email.value = storedEmail;
    confirmationToken.value = storedConfirmationToken;
  } else if (storedEmail) {
    email.value = storedEmail;
  } else {
    showMessage("Session expired. Please request a new reset code.", "error");
    setTimeout(() => router.push("/forgot-password"), 2000);
  }
});

const passwordValid = computed(() => {
  const password = form.value.new_password;
  return {
    length: password.length >= 8,
    hasUpperCase: /[A-Z]/.test(password),
    hasLowerCase: /[a-z]/.test(password),
    hasNumber: /[0-9]/.test(password)
  };
});

const isFormValid = computed(() => {
  const allRequirements = passwordValid.value.length &&
    passwordValid.value.hasUpperCase &&
    passwordValid.value.hasLowerCase &&
    passwordValid.value.hasNumber;
  
  return allRequirements && 
    form.value.new_password === form.value.confirm_password &&
    form.value.new_password.length > 0;
});

async function handleResetPassword() {
  if (!isFormValid.value) {
    if (form.value.new_password !== form.value.confirm_password) {
      showMessage("Passwords do not match", "error");
    } else {
      showMessage("Please meet all password requirements", "error");
    }
    return;
  }
  
  loading.value = true;
  
  try {
    const payload = {
      email: email.value,
      password: form.value.new_password,
      confirm_password: form.value.confirm_password,
      confirm_token: confirmationToken.value
    };
    
    console.log("Sending reset password request:", payload);
    
    const response = await resetPassword(payload);
    
    console.log("Reset password response:", response);
    
    if (response && response.status === 200) {
      showMessage("Password reset successfully! Redirecting to login...", "success");
      toasted(true, "Success", "Your password has been reset");
      
      localStorage.removeItem("resetEmail");
      localStorage.removeItem("resetOtp");
      localStorage.removeItem("confirmationToken");
      
      setTimeout(() => {
        router.push("/login");
      }, 2000);
    } else {
      const errorMsg = response?.data?.message || response?.message || "Failed to reset password";
      showMessage(errorMsg, "error");
      toasted(false, "Error", errorMsg);
    }
  } catch (error) {
    console.error("Reset password error:", error);
    const errorMsg = error.response?.data?.message || error.message || "An error occurred. Please try again.";
    showMessage(errorMsg, "error");
    toasted(false, "Error", errorMsg);
  } finally {
    loading.value = false;
  }
}

function showMessage(msg, type) {
  message.value = msg;
  messageType.value = type;
  setTimeout(() => {
    if (message.value === msg) {
      message.value = "";
    }
  }, 5000);
}
</script>

<style scoped>
/* Optional: Add smooth fade-in animation */
</style>