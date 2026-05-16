import ApiService from '@/service/ApiService';

const api = new ApiService();

export function getRecommendedMaterials(query = {}) {
  const params = new URLSearchParams();
  Object.entries(query || {}).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return;
    params.set(key, value);
  });

  const suffix = params.toString() ? `?${params.toString()}` : '';
  return api.addAuthenticationHeader().get(`/recommendations/for-you/${suffix}`);
}

