import ApiService from '@/service/ApiService';
import { getQueryFormObject } from '@/utils/utils.js';

const api = new ApiService();
const path = '/transactions/reservations';

export function createReservation(data) {
  return api.addAuthenticationHeader().post(`${path}/`, data);
}

export function getAllReservation(query = {}) {
  const qr = getQueryFormObject(query || {});
  return api.addAuthenticationHeader().get(`${path}/${qr}`);
}

export function updateReservationById(id, data) {
  return api.addAuthenticationHeader().put(`${path}/${id}/`, data);
}

export function removeReservationById(id) {
  return api.addAuthenticationHeader().delete(`${path}/${id}/`);
}
