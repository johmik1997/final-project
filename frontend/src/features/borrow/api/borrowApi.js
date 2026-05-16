import ApiService from '@/service/ApiService';
import { getQueryFormObject } from '@/utils/utils.js';

const api = new ApiService();
const path = '/transactions/borrow';

export function createBorrow(data) {
  return api.addAuthenticationHeader().post(`${path}/`, data); 
}

export function getAllBorrow(query = {}) {
  const qr = getQueryFormObject(query || {});
  return api.addAuthenticationHeader().get(`${path}/${qr}`);
}

// Keep pluralized name for existing imports
export function getAllBorrows(query = {}) {
  const qr = getQueryFormObject(query || {});
  return api.addAuthenticationHeader().get(`${path}/${qr}`);
}

export function getMyBorrows(query = {}) {
  const qr = getQueryFormObject(query || {});
  return api.addAuthenticationHeader().get(`${path}/my/${qr}`);
}

export function updateBorrowById(id, data) {
  return api.addAuthenticationHeader().put(`${path}/${id}/`, data);
}

export function removeBorrowById(id) {
  return api.addAuthenticationHeader().delete(`${path}/${id}/`);
}
