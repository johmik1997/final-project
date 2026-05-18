import ApiService from '@/service/ApiService';
import { getQueryFormObject } from '@/utils/utils.js';

const api = new ApiService();
const path = '/transactions/circulation';

export function createCirculation(data) {
  return api.addAuthenticationHeader().post(`${path}/`, data); 
}

export function getAllCirculation(query = {}) {
  const qr = getQueryFormObject(query || {});
  return api.addAuthenticationHeader().get(`${path}/${qr}`);
}

export function updateCirculationById(id, payload) {
  return api.addAuthenticationHeader().patch(`${path}/${id}/`, payload);
}

export function returnCirculation(id) {
  return api.addAuthenticationHeader().post(`${path}/${id}/return_material/`);
}

export function removeCirculationById(id) {
  return api.addAuthenticationHeader().delete(`${path}/${id}/`);
}
