<script setup>
import LoginForm from "./components/LoginForm.vue";
import { useRouter } from "vue-router";
import { ref, onMounted } from "vue";

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

onMounted(() => {
  loadSavedTheme();
});

function goToSignup() {
  router.push("/signUp"); 
}
</script>

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

    <div class="grid grid-cols-1 lg:grid-cols-2 min-h-screen relative z-10">
      <!-- Left Side - Hero Section -->
      <div class="hidden lg:flex flex-col justify-center p-8 md:p-12 lg:p-16 xl:p-20">
        <div class="max-w-lg mx-auto">
          <!-- Logo Area -->
          <div class="flex items-center space-x-3 mb-8">
            <img 
              src="@/assets/logolib.jpg" 
              alt="Logo" 
              class="w-14 h-14 rounded-full object-cover border-2 border-amber-500 shadow-lg shadow-amber-500/30"
            >
            <div>
              <span class="font-bold text-2xl" :class="isDarkTheme ? 'text-white' : 'text-slate-800'">HU<span class="text-amber-500">-DLRBS</span></span>
              <p :class="isDarkTheme ? 'text-slate-400' : 'text-slate-500'" class="text-xs">Digital Library System</p>
            </div>
          </div>

          <!-- Welcome Message -->
          <div class="space-y-4">
            <h1 class="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight" :class="isDarkTheme ? 'text-white' : 'text-slate-800'">
              Welcome to 
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-amber-500 to-red-500">
                Your Digital Library
              </span>
            </h1>
            <p class="text-base md:text-lg leading-relaxed" :class="isDarkTheme ? 'text-slate-300' : 'text-slate-600'">
              Borrow books, access e-books, and manage your reading all in one place. 
              Explore a wide range of resources and keep track of your reading history effortlessly.
            </p>
            
            <!-- Features List -->
            <div class="space-y-3 pt-4">
              <div class="flex items-center space-x-3" :class="isDarkTheme ? 'text-slate-300' : 'text-slate-600'">
                <div class="w-8 h-8 rounded-full flex items-center justify-center" :class="isDarkTheme ? 'bg-amber-500/20' : 'bg-amber-500/10'">
                  <svg class="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                  </svg>
                </div>
                <span>80,000+ Books & Resources</span>
              </div>
              <div class="flex items-center space-x-3" :class="isDarkTheme ? 'text-slate-300' : 'text-slate-600'">
                <div class="w-8 h-8 rounded-full flex items-center justify-center" :class="isDarkTheme ? 'bg-amber-500/20' : 'bg-amber-500/10'">
                  <svg class="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                  </svg>
                </div>
                <span>9 Campus Libraries</span>
              </div>
              <div class="flex items-center space-x-3" :class="isDarkTheme ? 'text-slate-300' : 'text-slate-600'">
                <div class="w-8 h-8 rounded-full flex items-center justify-center" :class="isDarkTheme ? 'bg-amber-500/20' : 'bg-amber-500/10'">
                  <svg class="w-4 h-4 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <span>24/7 Digital Access</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Side - Login Form -->
      <div class="flex items-center justify-center p-4 sm:p-6 lg:p-8">
        <LoginForm :isDarkTheme="isDarkTheme" />
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Optional: Add smooth fade-in animation */
</style>