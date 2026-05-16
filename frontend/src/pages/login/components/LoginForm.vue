<template>
  <div class="rounded-2xl backdrop-blur-sm p-6 sm:p-8 w-full max-w-md shadow-2xl transition-all duration-300" :class="isDarkTheme ? 'bg-slate-800/60 border-white/10' : 'bg-white/90 border-gray-200 shadow-xl'">
    <div class="flex justify-center mb-6">
      <div class="flex items-center space-x-2">
        <img 
          src="@/assets/logolib.jpg" 
          alt="Logo" 
          class="w-16 h-16 rounded-full object-cover border-2 border-amber-500 shadow-lg shadow-amber-500/30"
        >
        <span class="font-bold text-xl" :class="isDarkTheme ? 'text-white' : 'text-slate-800'">HU<span class="text-amber-500">-DLRBS</span></span>
      </div>
    </div>

    <div class="text-center mb-6">
      <h2 class="text-2xl font-bold" :class="isDarkTheme ? 'text-white' : 'text-slate-800'">Welcome Back</h2>
      <p class="text-sm mt-1" :class="isDarkTheme ? 'text-slate-400' : 'text-slate-500'">Sign in to access your library account</p>
    </div>

    <NewFormLayout v-slot="{ submit }" id="login-form">
      <div class="flex flex-col gap-5">
      
        <Input
          label="ID Number"
          name="id_number"
          validation="required"
          :attributes="{ placeholder: 'Enter ID Number' }"
          :theme="isDarkTheme ? 'dark' : 'light'"
        />

        <InputPassword
          label="Password"
          name="password"
          validation="required"
          :attributes="{ placeholder: 'Password' }"
          :theme="isDarkTheme ? 'dark' : 'light'"
        />

        <!-- Options Row -->
        <div class="flex flex-col sm:flex-row justify-between text-sm gap-3">
          <label class="flex gap-2 items-center cursor-pointer transition" :class="isDarkTheme ? 'text-slate-400 hover:text-slate-300' : 'text-slate-500 hover:text-slate-700'">
            <input type="checkbox" class="w-4 h-4 rounded transition-colors" :class="isDarkTheme ? 'border-white/20 bg-slate-800 text-amber-500 focus:ring-amber-500 focus:ring-offset-0 focus:ring-offset-slate-900' : 'border-gray-300 bg-white text-amber-500 focus:ring-amber-500'">
            <span>Keep me logged in</span>
          </label>
          <span
            @click="router.push({ path: '/forgot-password', query: {} })"
            class="text-amber-500 font-medium cursor-pointer hover:text-amber-400 transition-colors"
          >
            Forgot Password?
          </span>
        </div>

        <!-- Submit Button -->
        <FormSubmitButton
          class="w-full mt-2"
          @click.prevent="submit(handleLogin)"
          btn-text="Sign In"
          :pending="loginReq.pending.value"
          :class="{
            'bg-gradient-to-r from-amber-500 to-red-500 text-white font-semibold py-3 rounded-xl hover:shadow-lg hover:shadow-amber-500/25 transition-all duration-300': true
          }"
        />
        
        <!-- Sign Up Link -->
        <div class="text-center mt-4">
          <p :class="isDarkTheme ? 'text-slate-400' : 'text-slate-500'" class="text-sm">
            Don't have an account?
            <span
              @click="router.push('/signUp')"
              class="text-amber-500 font-medium cursor-pointer hover:text-amber-400 transition-colors ml-1"
            >
              Sign Up
            </span>
          </p>
        </div>
      </div>
    </NewFormLayout>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from "vue-router";
import { useApiRequest } from "@/composables/useApiRequest";
import { useAuth } from "@/stores/auth";
import { toasted } from "@/utils/utils";
import { login } from "../api/LoginApi";

// Components
import FormSubmitButton from "@/components/FormSubmitButton.vue";
import Input from "@/components/new_form_elements/Input.vue";
import InputPassword from "@/components/new_form_elements/InputPassword.vue";
import NewFormLayout from "@/components/NewFormLayout.vue";

const props = defineProps({
  isDarkTheme: {
    type: Boolean,
    default: true
  }
});

const router = useRouter();
const route = useRoute();
const auth = useAuth();
const loginReq = useApiRequest();

function handleLogin({ values }) {
  loginReq.send(() => login(values), (res) => {
    if (res.success) {
      const data = res?.data || {};
      const authPayload = {
        user: data?.user || data,
        accessToken: data?.access || data?.token,
        refreshToken: data?.refresh,
      };
      
      auth.setAuth(authPayload);
      localStorage.setItem("userDetail", JSON.stringify(authPayload));
      
      const redirect = route.query.redirect || "/app/dashboard";
      router.replace(redirect);
      toasted(true, "Welcome back!");
    } else {
      if (res.status === 404 && res?.error?.toLowerCase().includes("not active")) {
        router.push("/verify-account");
        return;
      }
      toasted(false, "Login failed", res.error || "Invalid credentials");
    }
  });
}
</script>

<style scoped>
/* Additional styling if needed */
</style>