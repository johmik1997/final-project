import ApiService from "@/service/ApiService";

const api = new ApiService();

export const getAllTransferRequests = async (params) => {
  return await api.addAuthenticationHeader().get("/material/transfer-requests/", { params });
};

export const createTransferRequest = async (data) => {
  return await api.addAuthenticationHeader().post("/material/transfer-requests/", data);
};

export const fulfillTransferRequest = async (id) => {
  return await api.addAuthenticationHeader().post(`/material/transfer-requests/${id}/fulfill/`);
};

export const cancelTransferRequest = async (id) => {
  return await api.addAuthenticationHeader().post(`/material/transfer-requests/${id}/cancel/`);
};
