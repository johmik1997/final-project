import ApiService from "@/service/ApiService";

const api = new ApiService(import.meta.env?.VITE_AUTH_API || import.meta.env?.v_AUTH_API);
const path = "user/auth";

// export function signup(data, config = {}) {
//   return api.post(`${path}/signUp`, data, config);
// }

export function login(data, config = {}) {
  return api.post(`${path}/login/`, data, config);
}

export function forgotPassword(data, config = {}) {
  return api.post(`${path}/forgot-password/`, data, config);
}

export function verifyOtpCode(email, otp) {
  return api.post(`${path}/confirm-reset-otp/`, { email, otp });
}

export function resendOtpCode(email) {
  return api.post(`${path}/resend-otp/`, { email });
}

export function resetPassword(data) {
  return api.post(`${path}/reset-password`, data);
}