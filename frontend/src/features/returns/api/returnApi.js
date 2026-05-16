import ApiService from '@/service/ApiService';
import { getQueryFormObject } from '@/utils/utils.js';

const api = new ApiService();
const path = '/transactions/return';

export function getAllReturns(query = {}) {
  const qr = getQueryFormObject(query || {});
  return api.addAuthenticationHeader().get(`${path}/${qr}`);
}

export function createReturn(data) {
  return api.addAuthenticationHeader().post(`${path}/`, data);
}

