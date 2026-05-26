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

export function getVeryOverdueLetters() {
  return api.addAuthenticationHeader().get(`${path}/very-overdue/`);
}

async function parseBlobError(blob) {
  const text = await blob.text();
  try {
    const parsed = JSON.parse(text);
    return parsed.detail || parsed.error || text;
  } catch {
    return text || 'Could not download PDF.';
  }
}

export async function downloadWarningLetterPdf(borrowId) {
  const client = new ApiService();
  client.addAuthenticationHeader();

  try {
    const response = await client.api.get(`${path}/${borrowId}/warning-letter/`, {
      responseType: 'blob',
    });

    const blob = response?.data;
    if (!(blob instanceof Blob)) {
      throw new Error('Invalid PDF response from server.');
    }

    if (blob.type?.includes('json') || blob.type?.includes('text')) {
      throw new Error(await parseBlobError(blob));
    }

    if (blob.size === 0) {
      throw new Error('Server returned an empty PDF file.');
    }

    return blob;
  } catch (error) {
    const errBlob = error?.response?.data;
    if (errBlob instanceof Blob) {
      throw new Error(await parseBlobError(errBlob));
    }
    throw error;
  }
}

export function savePdfBlob(blob, filename) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.rel = 'noopener';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}
