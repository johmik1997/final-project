<script setup>
import { ref, onMounted, watch } from "vue";
import { useAuth } from "@/stores/auth";
import { useRouter } from "vue-router";
import icons from "@/utils/icons";
import imageSrc from "@/assets/img/profile.png";

// Define props
const props = defineProps({
  modelValue: {
    type: String,
  },
  title: {
    type: String,
  },
});

// Initialize store and router
const authStore = useAuth();
console.log(authStore);

const router = useRouter();
const isScrolled = ref(false);

// Default profile picture
const profilePicture = ref(imageSrc);

// Check if user data is available
const user = authStore?.auth?.user || { name: "Birhane Araya", role: "Marketing Administrator" };

// Process the profile image
async function processProfilePicture() {
  console.log("authStore:", authStore);
  console.log("authStore.auth:", authStore.auth);
  console.log("authStore.auth.user:", authStore.auth?.user);
  
  const profilePic = authStore.auth?.user?.profilePicture;

  console.log("Profile Picture:", profilePic);

  if (profilePic) {
    if (!profilePic.startsWith("data:image/")) {
      profilePicture.value = `data:image/png;base64,${profilePic}`;
    } else {
      profilePicture.value = profilePic;
    }
  } else {
    profilePicture.value = imageSrc;
  }
}

// Handle image load error and fallback to default image
function handleImageError() {
  profilePicture.value = imageSrc;
}

// Handle logout functionality
function logout() {
  localStorage.removeItem("userDetail");
  window.location.href = "/login";
}

onMounted(() => {
  processProfilePicture();
  window.addEventListener('scroll', () => {
    isScrolled.value = window.scrollY > 10;
  });
});

// Watch for changes in input data
const inputData = ref("");
const emit = defineEmits(["update:modelValue"]);
watch(inputData, () => {
  emit("update:modelValue", inputData.value);
});

// Toggle user menu dropdown visibility
const showUserMenu = ref(false);
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value;
};

// Navigate to previous page (back button)
const goBack = () => {
  router.go(-1);
};

// Navigate to Profile or Settings page
const navigateTo = (page) => {
  if (page === "profile") {
    router.push('/profile'); 
  } else if (page === "settings") {
    router.push('/SettingsPage'); 
  }
  showUserMenu.value = false;
};
</script>

<template>
  <div class="navbar-container" :class="{ 'scrolled': isScrolled }">
    <!-- Left Side - Back Button and Title -->
    <div class="flex items-center gap-2 sm:gap-4">
      <button 
        @click="goBack" 
        class="back-button"
      >
        <svg width="7" height="13" viewBox="0 0 7 13" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path opacity="0.6" fill-rule="evenodd" clip-rule="evenodd"
            d="M5.82539 1.0134C6.03505 1.20471 6.05933 1.54072 5.87962 1.76391L2.15854 6.38525L5.87962 11.0066C6.05933 11.2298 6.03505 11.5658 5.82539 11.7571C5.61572 11.9484 5.30007 11.9226 5.12036 11.6994L1.12037 6.73164C0.959876 6.53232 0.959876 6.23819 1.12037 6.03887L5.12036 1.07113C5.30008 0.847943 5.61572 0.822096 5.82539 1.0134Z"
            fill="#F59E0B" stroke="#F59E0B" stroke-linecap="round" 
          />
        </svg>
      </button>
      <span class="page-title">{{ props.title }}</span>
    </div>

    <!-- Right Side - User Info and Icons -->
    <div class="flex gap-2 sm:gap-4 items-center">
      <!-- Icons - Hidden on mobile, visible on tablet and up -->
      <div class="hidden sm:flex gap-2 items-center">
        <button class="icon-button">
          <i v-html="icons.notification" />
        </button>
        <button class="icon-button">
          <i v-html="icons.message" />
        </button>
        <button class="icon-button">
          <i v-html="icons.bire" />
        </button>
      </div>

      <!-- User Profile Section -->
      <div class="relative">
        <button 
          @click="toggleUserMenu"
          class="user-button"
        >
          <div class="relative">
            <div class="user-avatar">
              <img
                :src="profilePicture || imageSrc"
                alt="User avatar"
                class="avatar-image"
                @error="handleImageError"
              />
            </div>
            <span class="online-indicator"></span>
          </div>
          
          <!-- User Info - Hidden on mobile -->
          <div class="hidden sm:block text-right">
            <p class="user-name">{{ user.name }}</p>
            <p class="user-role">{{ user.role }}</p>
          </div>
          
          <i v-html="icons.down" class="dropdown-icon" :class="{ 'rotated': showUserMenu }" />
        </button>

        <!-- Dropdown Menu -->
        <div v-if="showUserMenu" class="dropdown-menu">
          <!-- Mobile-only icons -->
          <div class="sm:hidden mobile-icons-section">
            <button class="dropdown-item">
              <i v-html="icons.notification" />
              <span>Notifications</span>
            </button>
            <button class="dropdown-item">
              <i v-html="icons.message" />
              <span>Messages</span>
            </button>
          </div>
          
          <!-- Common menu items -->
          <button @click="navigateTo('profile')" class="dropdown-item">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span>Profile</span>
          </button>
          <button @click="logout()" class="dropdown-item logout-item">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            <span>Logout</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Overlay for closing dropdown -->
    <div v-if="showUserMenu" 
         @click="showUserMenu = false"
         class="dropdown-overlay">
    </div>
  </div>
</template>

<style scoped>
.navbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  background: transparent;
  transition: all 0.3s ease;
}

.navbar-container.scrolled {
  background: rgba(15, 23, 42, 0.95);
  backdrop-filter: blur(12px);
  border-radius: 1rem;
  padding: 0.5rem;
  margin: -0.5rem;
}

/* Back Button */
.back-button {
  padding: 0.5rem;
  background: rgba(245, 158, 11, 0.1);
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
  border: 1px solid rgba(245, 158, 11, 0.2);
}

.back-button:hover {
  background: rgba(245, 158, 11, 0.2);
  border-color: rgba(245, 158, 11, 0.4);
  transform: translateX(-2px);
}

/* Page Title */
.page-title {
  text-transform: capitalize;
  font-size: 1rem;
  font-weight: 700;
  color: white;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  background: linear-gradient(135deg, #F59E0B, #EF4444);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

@media (min-width: 640px) {
  .page-title {
    font-size: 1.125rem;
  }
}

@media (max-width: 640px) {
  .page-title {
    max-width: 150px;
  }
}

/* Icon Buttons */
.icon-button {
  padding: 0.5rem;
  background: rgba(245, 158, 11, 0.08);
  border-radius: 0.75rem;
  transition: all 0.2s ease;
  color: #94A3B8;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(245, 158, 11, 0.15);
}

.icon-button:hover {
  background: rgba(245, 158, 11, 0.2);
  color: #F59E0B;
  transform: translateY(-2px);
  border-color: rgba(245, 158, 11, 0.4);
}

/* User Button */
.user-button {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  background: rgba(245, 158, 11, 0.08);
  border-radius: 1rem;
  transition: all 0.2s ease;
  border: 1px solid rgba(245, 158, 11, 0.15);
}

.user-button:hover {
  background: rgba(245, 158, 11, 0.15);
  border-color: rgba(245, 158, 11, 0.3);
}

/* User Avatar */
.user-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.75rem;
  overflow: hidden;
  border: 2px solid #F59E0B;
  box-shadow: 0 0 10px rgba(245, 158, 11, 0.3);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.user-button:hover .avatar-image {
  transform: scale(1.1);
}

/* Online Indicator */
.online-indicator {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 0.75rem;
  height: 0.75rem;
  background: #10B981;
  border-radius: 9999px;
  border: 2px solid #0F172A;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
  }
  70% {
    transform: scale(1);
    box-shadow: 0 0 0 4px rgba(16, 185, 129, 0);
  }
  100% {
    transform: scale(0.95);
    box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
  }
}

/* User Info Text */
.user-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: white;
  margin: 0;
}

.user-role {
  font-size: 0.7rem;
  color: #F59E0B;
  margin: 0;
}

/* Dropdown Icon */
.dropdown-icon {
  transition: transform 0.2s ease;
  color: #94A3B8;
}

.dropdown-icon.rotated {
  transform: rotate(180deg);
  color: #F59E0B;
}

/* Dropdown Menu */
.dropdown-menu {
  position: absolute;
  right: 0;
  top: 100%;
  margin-top: 0.5rem;
  width: 13rem;
  background: #1E293B;
  border-radius: 1rem;
  box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.5);
  padding: 0.5rem;
  z-index: 50;
  border: 1px solid rgba(245, 158, 11, 0.2);
  backdrop-filter: blur(10px);
}

/* Mobile Icons Section */
.mobile-icons-section {
  display: flex;
  flex-direction: column;
  border-bottom: 1px solid rgba(245, 158, 11, 0.2);
  padding-bottom: 0.5rem;
  margin-bottom: 0.5rem;
}

/* Dropdown Items */
.dropdown-item {
  width: 100%;
  padding: 0.625rem 1rem;
  text-align: left;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  transition: all 0.2s ease;
  color: #CBD5E1;
  font-size: 0.875rem;
}

.dropdown-item:hover {
  background: rgba(245, 158, 11, 0.15);
  color: #F59E0B;
}

.logout-item {
  color: #EF4444;
}

.logout-item:hover {
  background: rgba(239, 68, 68, 0.15);
  color: #EF4444;
}

/* Dropdown Overlay */
.dropdown-overlay {
  position: fixed;
  inset: 0;
  z-index: 40;
}

/* Responsive Adjustments */
@media (min-width: 640px) {
  .mobile-icons-section {
    display: none;
  }
}

@media (max-width: 640px) {
  .dropdown-menu {
    width: 12rem;
  }
}
</style>