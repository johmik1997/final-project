<script setup>
import Input from '@/components/new_form_elements/Input.vue';
import InputPassword from '@/components/new_form_elements/InputPassword.vue';
import Select from '@/components/new_form_elements/Select.vue';
import Form from '@/components/new_form_builder/Form.vue';
import { useForm } from '@/components/new_form_builder/useForm';

import { useApiRequest } from '@/composables/useApiRequest';
import { toasted, allRequest } from '@/utils/utils';
import { useRouter } from 'vue-router';
import { ref, watch } from 'vue';
import { getAllRole } from '@/features/roles/Api/RoleApi';
import { CreateUser, verifyUser, sendVerificationCode } from '@/features/users/Api/UserApi';

const { submit } = useForm('signup-form');

const router = useRouter();
const signupReq = useApiRequest();
const verifyReq = useApiRequest();
const rolereq = useApiRequest();
const clientRoleUuid = ref(null);

// Verification modal state
const showVerificationModal = ref(false);
const verificationCode = ref("");
const userPhoneNumber = ref("");

rolereq.send(() =>
  allRequest({
    roles: getAllRole({ page: 1, limit: 500 }),
  })
);

watch(
  () => rolereq.response.value?.roles?.content,
  (roles) => {
    if (roles?.length) {
      const client = roles.find((r) => r.roleName?.toLowerCase() === 'client');
      if (client) {
        clientRoleUuid.value = client.roleUuid;
      }
    }
  },
  { immediate: true }
);

function handleSignup({ values }) {
  values.userType = 'CLIENT';
  values.roleUuid = clientRoleUuid.value;

  signupReq.send(
    () => CreateUser(values),
    (res) => {
      if (res.success) {
        toasted(true, 'Signup successful');
        // Show verification modal
        userPhoneNumber.value = values.mobilePhone;
        showVerificationModal.value = true;
      } else {
        toasted(false, "", res.error || 'Signup failed');
      }
    }
  );
}

function submitVerification() {
  if (!verificationCode.value.trim()) {
    toasted(false, "", "Please enter verification code");
    return;
  }

  verifyReq.send(
    () => verifyUser(userPhoneNumber.value, verificationCode.value),
    (res) => {
      if (res.success) {
        toasted(true, "Account verified successfully");
        closeVerificationModal();
        router.push('/login');
      } else {
        toasted(false, "", res.error || "Verification failed");
      }
    }
  );
}

function sendVerification() {
 
  verifyReq.send(
    () => sendVerificationCode(userPhoneNumber.value),
    (res) => {
      if (res.success) {
        toasted(res.success, "Verification Code Sent successfully",res.error);
      } else {
        toasted(false, "", res.error || "Verification failed");
      }
    }
  );
}
function skipVerification() {
  toasted(true, "You can verify your account later from the login page");
  closeVerificationModal();
  router.push('/login');
}

function closeVerificationModal() {
  showVerificationModal.value = false;
  verificationCode.value = "";
  userPhoneNumber.value = "";
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-[#3C3C9E] to-[#5A5AB2] py-10 px-5">
    <div class="bg-white shadow-2xl rounded-xl p-10 max-w-5xl w-full">
      <!-- Header -->
      <div class="mb-6 text-center">
        <h2 class="text-3xl font-bold text-[#3C3C9E]">Create an Account</h2>
        <p class="text-gray-600 mt-2">Sign up to get started with your insurance management</p>
      </div>

      <!-- Form -->
      <Form id="signup-form" :inner="false"  class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Input name="email"  label="Email" :attributes="{ placeholder: 'Enter your email' }" />
        <InputPassword name="password" validation="required|min:6" label="Password" :attributes="{ placeholder: 'Secure password', required: true }" />
        <Select name="title" label="Title" validation="required" :options="['Mr.', 'Ms.', 'Dr.', 'Prof.']" :attributes="{ placeholder: 'Select your title', required: true }" />

        <Input name="firstName" validation="required|alpha" label="First Name" :attributes="{ placeholder: 'First name' , required: true }" />
        <Input name="fatherName" validation="required|alpha" label="Father Name" :attributes="{ placeholder: 'Father name', required: true }" />
        <Input name="grandFatherName"  label="Grandfather Name" :attributes="{ placeholder: 'Grandfather name' }" />

        <Select name="gender" label="Gender" validation="required" :options="['Male', 'Female']" :attributes="{ placeholder: 'Select your gender', required: true }" />
        <Input name="mobilePhone" label="Mobile Phone" validation="required|phone" :attributes="{ placeholder: '09XXXXXXXX', required: true }" />

        <!-- Hidden fields -->
        <input type="hidden" name="userType" value="CLIENT" />
        <input type="hidden" name="roleUuid" :value="clientRoleUuid" />

        <!-- Submit Button -->
        <div class="col-span-full mt-4 flex justify-end">
          <button
            type="button"
            @click.prevent="submit(handleSignup)"
            class="bg-[#3C3C9E] hover:bg-[#2a2a82] text-white font-semibold px-8 py-3 rounded-lg shadow transition"
            :disabled="!clientRoleUuid || signupReq.pending.value"
          >
            <span v-if="signupReq.pending.value">Signing Up...</span>
            <span v-else>Sign Up</span>
          </button>
        </div>
      </Form>

      <!-- Already have an account -->
      <div class="text-center mt-6 text-sm text-gray-600">
        Already have an account?
        <router-link to="/login" class="text-[#3C3C9E] font-medium hover:underline">
          Login here
        </router-link>
      </div>
    </div>

    <!-- Verification Modal -->
    <div v-if="showVerificationModal" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-xl w-full max-w-md shadow-lg p-6">
        <!-- Close Button -->
        <button
          @click="closeVerificationModal"
          class="absolute top-4 right-4 text-gray-600 hover:text-gray-900"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <!-- Title -->
        <h3 class="text-lg font-bold text-gray-800 mb-4 py-2 border-b">
          Verify Your Account
        </h3>

        <!-- Message -->
        <p class="text-gray-600 text-sm leading-relaxed mb-4">
          Account created successfully! Please enter the verification code sent to your phone number: <strong>{{ userPhoneNumber }}</strong>
        </p>

        <!-- Verification Code Input -->
        <div class="mb-5">
          <label class="block text-sm font-medium text-gray-700 mb-1">
            Verification Code
          </label>
          <input
            type="text"
            v-model="verificationCode"
            placeholder="Enter verification code"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            @keyup.enter="submitVerification"
          />
        </div>

        <!-- Buttons -->
        <div class="flex justify-end gap-4 mt-2 pb-2">
          <button
            @click="skipVerification"
            class="bg-gray-500 text-white px-6 py-2 text-sm font-medium hover:bg-gray-600 rounded-md"
          >
            Skip for Now
          </button>
           <button
            @click="sendVerification"
            class="bg-blue-300 text-gray px-6 py-2 text-sm font-medium hover:bg-blue-400 rounded-md"
          >
            Send Code Again
          </button>
          <button
            @click="submitVerification"
            :disabled="!verificationCode.trim() || verifyReq.pending.value"
            :class="{'bg-blue-400 cursor-not-allowed': !verificationCode.trim(), 'bg-[#2E3365] hover:bg-[#1E224D]': verificationCode.trim()}"
            class="text-white px-6 py-2 text-sm font-medium rounded-md transition-colors"
          >
            <span v-if="verifyReq.pending.value">Verifying...</span>
            <span v-else>Verify</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
