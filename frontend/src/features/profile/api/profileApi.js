import ApiService from "@/service/ApiService";

const api = new ApiService();
const basePath = "/users";

export function getPersonalDetails(userId) {
  return api
    .addAuthenticationHeader()
    .get(`${basePath}/${userId}/details`);
}
export function getProfilePicture(userId) {
  return api
    .addAuthenticationHeader()
    .get(`${basePath}/getProfile/${userId}`);
}

export function uploadProfilePicture(file, userUuid) {
  const formData = new FormData();
  formData.append("profilePicture", file);

  return api
    .addAuthenticationHeader()
    .put(`${basePath}/editProfile/${userUuid}`, formData, {
      headers: {
        // ✅ DO NOT set 'Content-Type' manually
        // Let the browser set the correct 'multipart/form-data; boundary=...'
        // 'Content-Type': 'multipart/form-data', <-- REMOVE THIS!
      },
    });
}



export function changePassword(id,data) {
  return api
    .addAuthenticationHeader()
    .put(`${basePath}/changePassword/${id}`, data);
}
export function updateProfileData(id,data) {
  return api
    .addAuthenticationHeader()
    .put(`${basePath}/update/${id}`, data);
}
