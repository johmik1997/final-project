import ApiService from "@/service/ApiService";
import { getQueryFormObject } from "@/utils/utils.js";

const api = new ApiService();
const path = "/role";
export function getCategoriesByInsurance(insuranceUuid, query = {}) {
  const qr = getQueryFormObject(query);
  return api.addAuthenticationHeader().get(
    `/allPremium/${insuranceUuid}?page=1&limit=25`
  );
}
export function getAllRole(query = {}) {
  const qr = getQueryFormObject(query);
  return api.addAuthenticationHeader().get(`${path}/getAll${qr}`);
}
export function getAllInsurances(query = {}) {
  const qr = getQueryFormObject(query);
  return api.addAuthenticationHeader().get(`/insurance/all${qr}`);
}
export function craeteRole(data) {
  return api.addAuthenticationHeader().post(`${path}`, data);
}
export function getRoleById(id) {
  return api.addAuthenticationHeader().get(`${path}/${id}`);
}
export function updateRolebyId(id, data) {
  return api.addAuthenticationHeader().put(`${path}/${id}`, data);
}
export function removeRoleById(id) {
  return api.addAuthenticationHeader().delete(`${path}/${id}`);
}
