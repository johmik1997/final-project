import ApiService from "@/service/ApiService";
import { getQueryFormObject } from "@/utils/utils.js";

const api = new ApiService();
const TYPE_PATHS = {
  physical: "/material/physical-materials",
  digital: "/material/digital-materials",
};

function resolvePath(type = "physical") {
  const key = String(type || "physical").toLowerCase();
  return TYPE_PATHS[key] || TYPE_PATHS.physical;
}

export function CreateMaterial(data, type = "physical") {
  const path = resolvePath(type);
  return api.addAuthenticationHeader().post(`${path}/`, data);
}

export function createPhysicalMaterial(data) {
  return CreateMaterial(data, "physical");
}

export function createDigitalMaterial(data) {
  return CreateMaterial(data, "digital");
}

export function getAllMaterials(query = {}, type = "physical") {
  const path = resolvePath(type);
  const qr = getQueryFormObject(query);
  return api.addAuthenticationHeader().get(`${path}/${qr}`);
}

export function getMaterialById(id, type = "physical") {
  const path = resolvePath(type);
  return api.addAuthenticationHeader().get(`${path}/${id}/`);
}

export function updateMaterialById(id, data, type = "physical") {
  const path = resolvePath(type);
  return api.addAuthenticationHeader().put(`${path}/${id}/`, data);
}

export function removeMaterialById(id, type = "physical") {
  const path = resolvePath(type);
  return api.addAuthenticationHeader().delete(`${path}/${id}/`);
}

export function generateMaterialDescription(payload = {}) {
  return api.addAuthenticationHeader().post("/material/generate-description/", payload);
}

export function getMaterialInteractionStats(materialId, materialType = "physical") {
  const qr = getQueryFormObject({
    material_id: materialId,
    material_type: materialType,
  });
  return api.addAuthenticationHeader().get(`/material/interactions/stats/${qr}`);
}

export function getMaterialFeedback(query = {}) {
  const qr = getQueryFormObject(query || {});
  return api.addAuthenticationHeader().get(`/material/feedback/${qr}`);
}

export function createMaterialFeedback(payload = {}) {
  return api.addAuthenticationHeader().post("/material/feedback/", payload);
}

export function updateMaterialFeedback(id, payload = {}) {
  return api.addAuthenticationHeader().patch(`/material/feedback/${id}/`, payload);
}

export function getMaterialFavorites(query = {}) {
  const qr = getQueryFormObject(query || {});
  return api.addAuthenticationHeader().get(`/material/favorites/${qr}`);
}

export function createMaterialFavorite(payload = {}) {
  return api.addAuthenticationHeader().post("/material/favorites/", payload);
}

export function removeMaterialFavorite(id) {
  return api.addAuthenticationHeader().delete(`/material/favorites/${id}/`);
}

export function getMaterialBookmarks(query = {}) {
  const qr = getQueryFormObject(query || {});
  return api.addAuthenticationHeader().get(`/material/bookmarks/${qr}`);
}

export function createMaterialBookmark(payload = {}) {
  return api.addAuthenticationHeader().post("/material/bookmarks/", payload);
}

export function removeMaterialBookmark(id) {
  return api.addAuthenticationHeader().delete(`/material/bookmarks/${id}/`);
}
