import ApiService from '@/service/ApiService';

const api = new ApiService();

export function initializeFinePayment(data) {
  return api.addAuthenticationHeader().post('/payment/chapa/initialize/', data);
}

export function verifyFinePayment(txRef) {
  return api.addAuthenticationHeader().post(`/payment/chapa/verify/${txRef}/`, {});
}

