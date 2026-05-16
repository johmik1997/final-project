import ApiService from "@/service/ApiService";
import { getQueryFormObject } from "@/utils/utils.js";

const api = new ApiService();
const path = "/user/library-policies";

export function getAllLibraryPolicies(query = {}) {
  const qr = getQueryFormObject(query || {});
  return api.addAuthenticationHeader().get(`${path}/${qr}`);
}

export function createLibraryPolicy(data) {
  return api.addAuthenticationHeader().post(`${path}/`, data);
}

export function updateLibraryPolicyById(id, data) {
  return api.addAuthenticationHeader().put(`${path}/${id}/`, data);
}

export function removeLibraryPolicyById(id) {
  return api.addAuthenticationHeader().delete(`${path}/${id}/`);
}
