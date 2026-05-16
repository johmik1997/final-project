<script setup>
import { ref, watch, onMounted } from "vue";
import { useAuth } from "@/stores/auth";
import ProfileForm from "../components/ProfileForm.vue";
import SecurityForm from "../components/SecurityForm.vue";
import Button from "@/components/Button.vue";
import { useApiRequest } from "@/composables/useApiRequest";
import { updateProfileData, uploadProfilePicture, getProfilePicture } from "../api/profileApi";
import { convertBase64Image, toasted } from "@/utils/utils";
import { useForm } from "@/components/new_form_builder/useForm";
import icons from "@/utils/icons";
import imageSrc from '@/assets/img/profile.png'

const auth = useAuth();

const profilePicture = ref(null);
const isLoading = ref(false);

// Process the profile picture when component mounts
onMounted(() => {
  loadProfilePicture();
});

async function loadProfilePicture() {
  const userUuid = auth.auth?.user?.userUuid;
  if (!userUuid) {
    profilePicture.value = imageSrc;
    return;
  }

  isLoading.value = true;
  
  try {
    // Try to fetch the profile picture via API
    const response = await getProfilePicture(userUuid);
    
   if (response.success && response.data) {
  let imagePayload = response.data;

  // If imageData is nested in the object, use it
  if (typeof imagePayload === 'object' && imagePayload.imageData) {
    imagePayload = imagePayload.imageData;
  }

  if (typeof imagePayload === 'string') {
    if (imagePayload.startsWith('http') || imagePayload.startsWith('/')) {
      profilePicture.value = imagePayload;
      return;
    }

    if (isValidBase64(imagePayload)) {
      profilePicture.value = `data:image/png;base64,${imagePayload}`;
      testImageLoad(profilePicture.value);
      return;
    }
  }
}

    
    // Fallback to auth store data
    processAuthStorePicture();
  } catch (error) {
    console.error("Error loading profile picture:", error);
    processAuthStorePicture();
  } finally {
    isLoading.value = false;
  }
}

function processAuthStorePicture() {
  const rawPicture = auth.auth?.user?.profilePicture;
  
  if (!rawPicture) {
    profilePicture.value = imageSrc;
    return;
  }
  
  // If it's already a data URL, use it directly
  if (rawPicture.startsWith("data:image/")) {
    profilePicture.value = rawPicture;
    return;
  }
  
  // Check if it's a URL
  if (isUrl(rawPicture)) {
    profilePicture.value = rawPicture;
    return;
  }
  
  // Check if the base64 string looks valid
  if (isValidBase64(rawPicture)) {
    profilePicture.value = `data:image/png;base64,${rawPicture}`;
    testImageLoad(profilePicture.value);
    return;
  }
  
  // Final fallback
  profilePicture.value = imageSrc;
}

// Check if a string is valid base64
function isValidBase64(str) {
  try {
    // Base64 should only contain these characters
    const base64Regex = /^[A-Za-z0-9+/=]+$/;
    if (!base64Regex.test(str)) {
      return false;
    }
    
    // Check if the length is a multiple of 4
    if (str.length % 4 !== 0) {
      return false;
    }
    
    // Try to decode it
    atob(str);
    return true;
  } catch (error) {
    return false;
  }
}

// Check if string is a URL
function isUrl(str) {
  try {
    new URL(str);
    return true;
  } catch (error) {
    return false;
  }
}

// Test if an image URL loads successfully
function testImageLoad(url) {
  const testImg = new Image();
  testImg.onload = function() {
    console.log("Image loaded successfully");
  };
  testImg.onerror = function() {
    console.log("Image failed to load, using default");
    profilePicture.value = imageSrc;
  };
  testImg.src = url;
}

// Also watch for changes to the auth user's profile picture
watch(() => auth.auth?.user?.profilePicture, (newValue) => {
  if (newValue) {
    processAuthStorePicture();
  }
});

const fileInput = ref(null);
const api = useApiRequest();
const profileApi = useApiRequest();

const triggerFileInput = () => {
  fileInput.value?.click();
};

const handleFileChange = (event) => {
  const file = event.target.files[0];
  if (!file) return;

  if (!file.type.startsWith("image/")) {
    toasted(false, "Please select a valid image file.");
    return;
  }

  const userUuid = auth.auth?.user?.userUuid;
  if (!userUuid) {
    toasted(false, "User ID missing.");
    return;
  }

  // Create a temporary URL for immediate preview
  const tempUrl = URL.createObjectURL(file);
  profilePicture.value = tempUrl;

  profileApi.send(
    () => uploadProfilePicture(file, userUuid),
    (res) => {
      if (res.success) {
        toasted(true, "Profile picture updated successfully!");
        // Update the auth store with the new profile picture if needed
        if (res.data && res.data.profilePicture) {
          auth.auth.user.profilePicture = res.data.profilePicture;
          loadProfilePicture(); // Reload the picture
        }
      } else {
        toasted(false, res.error || "Failed to update profile picture.");
        // Revert to the original picture if upload failed
        loadProfilePicture();
      }
    }
  );
};

const active = ref(0);

const setActive = (item) => {
  active.value = item;
};

const components = [
  {
    name: "Profile",
    component: ProfileForm,
  },
  {
    name: "Security",
    component: SecurityForm,
  },
];

const { submit } = useForm('ProfileForm');

const authStore = useAuth();

function handleUpdateProfile({ values }) {
  api.send(() => updateProfileData(authStore.auth?.user?.userUuid, values), res => {
    toasted(res.success, 'Profile Updated Successfully', res.error);
  });
}
</script>

<template>
  <div class="w-full min-h-screen bg-gray-50">
    <!-- Header section -->
    <div class="relative bg-primary rounded-b-2xl h-56">
      <!-- Content section -->
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 absolute top-32 w-full">
        <div class="flex flex-col lg:flex-row gap-6">
          
          <!-- Profile Picture Section -->
          <div class="bg-white rounded-2xl p-4 flex-shrink-0 w-full max-w-xs mx-auto lg:mx-0">
            <div v-if="isLoading" class="rounded-lg w-full h-[206px] flex items-center justify-center bg-gray-200">
              <i v-html="icons.spinner" class="text-2xl" />
            </div>
            <img
              v-else
              :src="profilePicture"
              class="rounded-lg w-full h-[206px] object-cover"
              alt="Profile"
              @error="profilePicture = imageSrc"
            />
            <!-- Hidden file input -->
            <input
              ref="fileInput"
              type="file"
              accept="image/*"
              class="hidden"
              @change="handleFileChange"
            />
            <button
              @click.prevent="triggerFileInput"
              class="mt-4 flex items-center justify-center gap-2 h-12 w-full rounded text-white font-medium bg-primary hover:bg-primary/80"
            >
              <i v-if="profileApi.pending.value" v-html="icons.spinner" />
              <p v-else>Change Photo</p>
            </button>
          </div>

          <!-- Form Section -->
          <div class="bg-white flex-1 rounded-2xl p-6 space-y-6">
            <!-- Tabs + Edit Button -->
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <!-- Tabs -->
              <div class="flex border border-gray-500 rounded overflow-hidden w-fit mx-auto sm:mx-0">
                <div
                  v-for="(item, index) in components"
                  :key="index"
                  @click="setActive(index)"
                  :class="[
                    'px-4 py-2 text-sm sm:text-base cursor-pointer transition-all',
                    active === index ? 'bg-gray-500 text-white font-semibold' : 'text-gray-700',
                    index === 0 ? 'rounded-l' : '',
                    index === components.length - 1 ? 'rounded-r' : '',
                  ]"
                >
                  {{ item.name }}
                </div>
              </div>

              <!-- Edit Button -->
              <Button
                v-if="active === 0"
                :pending="api.pending.value"
                @click.prevent="submit(handleUpdateProfile)"
                class="bg-yellow-400 hover:bg-yellow-300 text-black font-semibold px-4 py-2 rounded-md"
              >
                Edit
              </Button>
            </div>

            <!-- Component -->
            <div>
              <component :is="components[active].component" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>