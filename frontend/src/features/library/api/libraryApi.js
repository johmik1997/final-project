import ApiService from "@/service/ApiService";
import { getQueryFormObject } from "@/utils/utils.js";

const api = new ApiService();
const path = "/user/libraries";
export function CreateLibrary(data) {
  return api.addAuthenticationHeader().post(`${path}/`, data);
}

export function getAllLibrary(query = {}) {
  const qr = getQueryFormObject(query);
  return api.addAuthenticationHeader().get(`${path}/${qr}`);
}

export function getLibraryById(id) {
  return api.addAuthenticationHeader().get(`${path}/${id}/`);
}

export function updateLibraryById(id, data) {
  return api.addAuthenticationHeader().put(`${path}/${id}/`, data);
}

export function removeLibraryById(id) {
  return api.addAuthenticationHeader().delete(`${path}/${id}/`);
}

