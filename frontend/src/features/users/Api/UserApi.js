import ApiService from "@/service/ApiService";
import { getQueryFormObject } from "@/utils/utils.js";

const api = new ApiService();
const path = "/user/users";

// ----------------- EXISTING -----------------
export function CreateUser(data) {
  return api.addAuthenticationHeader().post(`${path}/create/`, data);
}

export const verifyUser = (phoneNumber, code) => {
  return api.addAuthenticationHeader().post(`${path}/EnterVerificationCode?phoneNumber=${phoneNumber}&code=${code}`);
};

export const sendVerificationCode = (phoneNumber) => {
  return api.addAuthenticationHeader().post(`${path}/send?phoneNumber=${phoneNumber}`);
};

export function getAllUser(query = {}) {
  const normalizedQuery = { ...(query || {}) };

  // Handle pagination parameters
  const page = Number(normalizedQuery.page);
  normalizedQuery.page = Number.isFinite(page) && page > 0 ? page : 1;

  const size = Number(normalizedQuery.size);
  normalizedQuery.size = Number.isFinite(size) && size > 0 ? size : 25;

  // Handle search parameter
  const qr = getQueryFormObject(normalizedQuery);
  return api.addAuthenticationHeader().get(`${path}/all${qr}`);
}

export function getUserById(id) {
  return api.addAuthenticationHeader().get(`${path}/${id}`);
}

export function updateUserById(id, data) {
  return api.addAuthenticationHeader().put(`${path}/update/${id}/`, data);
}

export function removeUserById(id) {
  return api.addAuthenticationHeader().delete(`${path}/${id}/delete/`);
}

export function fetchUserFilesView() {
  return api.addAuthenticationHeader().get(`${path}`);
}

export function fetchUserFiles() {
  return api.addAuthenticationHeader().get(`${path}`);
}

// 1️⃣ Forgot Password (send OTP to phone number)
export function forgotPassword(phoneNumber) {
  return api.addAuthenticationHeader().put(
    `${path}/password/forgotPassword/${phoneNumber}`
  );
}

// 2️⃣ Enter Verification Code (verify OTP)
export function enterVerificationCode(phoneNumber, code) {
  return api.addAuthenticationHeader().post(
    `${path}/password/checkResetCode?userName=${phoneNumber}&verificationCode=${code}`
  );
}

// 3️⃣ Reset Password (submit new password with OTP)
export function resetPassword(data) {
  return api.addAuthenticationHeader().put(
    `${path}/resetPassword`,
    data
  );
}
