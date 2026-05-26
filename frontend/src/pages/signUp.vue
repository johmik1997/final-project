<script setup>
import Input from '@/components/new_form_elements/Input.vue';
import InputPassword from '@/components/new_form_elements/InputPassword.vue';
import Form from '@/components/new_form_builder/Form.vue';
import { useForm } from '@/components/new_form_builder/useForm';
import { useApiRequest } from '@/composables/useApiRequest';
import { toasted } from '@/utils/utils';
import { useRouter } from 'vue-router';
import { registerStudent } from '@/features/users/Api/UserApi';

const { submit } = useForm('student-signup-form');
const router = useRouter();
const signupReq = useApiRequest();

function handleSignup({ values }) {
  const payload = {
    id_number: String(values.id_number || '').trim(),
    full_name: String(values.full_name || '').trim(),
    phone: String(values.phone || '').trim(),
    email: String(values.email || '').trim(),
    password: values.password,
    confirm_password: values.confirm_password,
  };

  signupReq.send(
    () => registerStudent(payload),
    (res) => {
      if (res.success) {
        toasted(true, res.data?.detail || 'Registration successful. You can sign in now.');
        router.push('/login');
        return;
      }
      toasted(false, '', res.error || 'Registration failed.');
    }
  );
}
</script>

<template>
  <div
    class="min-h-screen grid place-items-center p-6 transition-all duration-300"
    :class="
      isDarkTheme
        ? 'bg-gradient-to-br from-slate-950 via-slate-900 to-slate-800'
        : 'bg-gradient-to-br from-orange-50 via-slate-50 to-blue-50'
    "
  >
    <div
      class="w-full max-w-3xl rounded-3xl border backdrop-blur-sm p-7 shadow-2xl transition-all duration-300"
      :class="
        isDarkTheme
          ? 'bg-slate-900/70 border-white/10'
          : 'bg-white/90 border-slate-200'
      "
    >
      <header class="mb-7">
        <h1
          class="text-3xl font-bold"
          :class="isDarkTheme ? 'text-white' : 'text-slate-900'"
        >
          Student Registration
        </h1>

        <p
          class="mt-3 text-sm leading-6"
          :class="isDarkTheme ? 'text-slate-400' : 'text-slate-600'"
        >
          Create your library account using your university student ID.
          Your details are verified against the campus student registry
          before registration is approved.
        </p>
      </header>

      <Form id="student-signup-form" :inner="false">
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <Input
            name="id_number"
            label="Student ID Number"
            validation="required"
            :theme="isDarkTheme ? 'dark' : 'light'"
            :attributes="{ placeholder: 'e.g. STU10001' }"
          />

          <Input
            name="full_name"
            label="Full Name"
            validation="required"
            :theme="isDarkTheme ? 'dark' : 'light'"
            :attributes="{ placeholder: 'As shown on your university ID' }"
          />

          <Input
            name="phone"
            label="Phone Number"
            validation="required"
            :theme="isDarkTheme ? 'dark' : 'light'"
            :attributes="{ placeholder: '09xxxxxxxx' }"
          />

          <Input
            name="email"
            label="Personal Email"
            validation="required|email"
            :theme="isDarkTheme ? 'dark' : 'light'"
            :attributes="{ placeholder: 'you@example.com', type: 'email' }"
          />

          <InputPassword
            name="password"
            label="Password"
            validation="required|min:8"
            :theme="isDarkTheme ? 'dark' : 'light'"
            :attributes="{ placeholder: 'At least 8 characters' }"
          />

          <InputPassword
            name="confirm_password"
            label="Confirm Password"
            validation="required|min:8"
            :theme="isDarkTheme ? 'dark' : 'light'"
            :attributes="{ placeholder: 'Repeat password' }"
          />
        </div>

        <p
          class="mt-5 text-sm leading-6"
          :class="isDarkTheme ? 'text-amber-300' : 'text-amber-700'"
        >
          Registration is allowed only when your student ID exists in the
          campus registry, your campus status is active, and your university
          ID has not expired.
        </p>

        <div class="flex justify-between items-center mt-7 gap-4 flex-wrap">
          <button
            type="button"
            class="px-5 py-2.5 rounded-xl font-semibold transition-all"
            :class="
              isDarkTheme
                ? 'bg-slate-800 text-slate-200 hover:bg-slate-700'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            "
            @click="router.push('/login')"
          >
            Back to login
          </button>

          <button
            type="button"
            class="px-6 py-2.5 rounded-xl font-semibold text-white bg-gradient-to-r from-amber-500 to-red-500 hover:shadow-lg hover:shadow-amber-500/20 transition-all"
            :disabled="signupReq.pending.value"
            @click.prevent="submit(handleSignup)"
          >
            {{ signupReq.pending.value ? 'Registering…' : 'Register' }}
          </button>
        </div>
      </Form>
    </div>
  </div>
</template>

<style scoped>
.signup-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 1.5rem;
  background: linear-gradient(160deg, #fff7ed 0%, #f8fafc 45%, #eff6ff 100%);
}

.signup-card {
  width: 100%;
  max-width: 42rem;
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(203, 213, 225, 0.7);
  border-radius: 1.25rem;
  padding: 1.75rem;
  box-shadow: 0 24px 48px -24px rgba(15, 23, 42, 0.35);
}

.signup-header h1 {
  margin: 0;
  font-size: 1.6rem;
  color: #0f172a;
}

.signup-header p {
  margin: 0.5rem 0 1.25rem;
  color: #64748b;
  font-size: 0.9rem;
  line-height: 1.5;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

@media (min-width: 640px) {
  .form-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

.hint {
  margin: 1rem 0 0;
  font-size: 0.8rem;
  color: #92400e;
  line-height: 1.45;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.25rem;
}

.btn-primary,
.btn-secondary {
  border-radius: 0.75rem;
  padding: 0.55rem 1.1rem;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, #f59e0b, #ef4444);
  color: white;
}

.btn-primary:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f1f5f9;
  color: #334155;
}
</style>
