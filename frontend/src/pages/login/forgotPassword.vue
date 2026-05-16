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
          <h1 class="text-3xl font-bold" :class="isDarkTheme ? 'text-white' : 'text-slate-800'">Forgot Password?</h1>
          <p class="mt-2" :class="isDarkTheme ? 'text-slate-400' : 'text-slate-500'">Enter your email to receive a reset code</p>
        </div>

        <!-- Form Card -->
        <div class="rounded-2xl backdrop-blur-sm p-6 sm:p-8 shadow-2xl transition-all duration-300" :class="isDarkTheme ? 'bg-slate-800/60 border-white/10' : 'bg-white/90 border-gray-200 shadow-xl'">
          <NewFormLayout v-slot="{ submit }" id="forgot-password-form">
            <div class="space-y-6">
              <!-- Email Input -->
              <div>
                <label class="block text-sm font-medium mb-2" :class="isDarkTheme ? 'text-slate-300' : 'text-slate-700'">
                  Email Address
                </label>
                <Input
                  name="email"
                  validation="required|email"
                  :attributes="{ 
                    placeholder: 'Enter your registered email',
                    class: 'w-full px-4 py-3 rounded-xl transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent'
                  }"
                  :theme="isDarkTheme ? 'dark' : 'light'"
                />
              </div>

              <!-- Submit Button -->
              <button
                @click.prevent="submit(requestResetCode)"
                :disabled="resetRequest.pending.value"
                class="w-full bg-gradient-to-r from-amber-500 to-red-500 text-white font-semibold py-3 rounded-xl hover:shadow-lg hover:shadow-amber-500/25 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="resetRequest.pending.value" class="flex items-center justify-center gap-2">
                  <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Sending...
                </span>
                <span v-else>Send Reset Code</span>
              </button>
            </div>
          </NewFormLayout>

          <!-- Back to Login Link -->
          <div class="mt-6 text-center">
            <router-link to="/login" class="text-sm transition-colors inline-flex items-center gap-1" :class="isDarkTheme ? 'text-amber-500 hover:text-amber-400' : 'text-amber-600 hover:text-amber-700'">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
              </svg>
              Back to Login
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from "vue-router";
import { useApiRequest } from "@/composables/useApiRequest";
import { toasted } from "@/utils/utils";
import { forgotPassword } from "./api/LoginApi";
import NewFormLayout from "@/components/NewFormLayout.vue";
import Input from "@/components/new_form_elements/Input.vue";
import { ref, onMounted } from "vue";

const router = useRouter();
const resetRequest = useApiRequest();

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

onMounted(() => {
  loadSavedTheme();
});

function requestResetCode({ values }) {
  const emailData = {
    email: values.email
  };
  
  console.log("Sending forgot password request with:", emailData);
  
  resetRequest.send(
    () => forgotPassword(emailData),
    (res) => {
      console.log("Forgot password response:", res);
      
      if (res.success) {
        toasted(true, "Success", "Reset code sent to your email");
        localStorage.setItem("resetEmail", values.email);
        router.push(`/verify-otp`);
      } else {
        const errorMsg = res.error || res.message || "Failed to send reset code";
        toasted(false, "Error", errorMsg);
      }
    }
  );
}
</script>

<style scoped>
/* Optional: Add smooth fade-in animation */
</style>