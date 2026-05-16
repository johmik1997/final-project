import ApiService from "@/service/ApiService";
import { getQueryFormObject } from "@/utils/utils.js";

const api = new ApiService();
const path = "";

export function getAllPrivilege(query = {}) {
  const qr = getQueryFormObject(query);
  return api.addAuthenticationHeader().get(`${path}/privilege/list${qr}`);
}
export function createPrivilege(data) {
  return api
    .addAuthenticationHeader()
    .post(`${path}/privilege/createPrivilege`, data);
}
export function removePrivilege(id) {
  return api.addAuthenticationHeader().delete(`${path}/privilege/${id}`);
}
export function getPrivilegeById(id) {
  return api.addAuthenticationHeader().get(`${path}/privilege/${id}`);
}
export function updatePrivilege(id, data) {
  return api.addAuthenticationHeader().put(`${path}/privilege/${id}`, data);
}
