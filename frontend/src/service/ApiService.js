import axios from "axios";
import { responseHandler } from "./ApiResponseHandler";
import { useAuth } from "@/stores/auth";

const backendApiUrl = import.meta.env.VITE_API_URL || import.meta.env.v_API_URL;
const authApiUrl = import.meta.env.VITE_AUTH_API || import.meta.env.v_AUTH_API;

export default class ApiService {
  api;
  static refreshPromise = null;

  _initApi(baseURL) {
    this.api = axios.create({
      baseURL,
      validateStatus: (status) => status >= 200 && status < 300,
    });
  }

  constructor(baseURL) {
    this._initApi(baseURL || backendApiUrl);
    this._setupInterceptors();
  }

  /**
   * Adds bearer token from auth store to headers
   */
  addAuthenticationHeader() {
    const authStore = useAuth();
    const stored = this._getStoredAuth();
    const accessToken = authStore.auth?.accessToken || stored?.accessToken;

    if (accessToken) {
      this.api.defaults.headers.common.Authorization = `Bearer ${accessToken}`;
    } else {
      delete this.api.defaults.headers.common.Authorization;
    }
    return this;
  }

  _setupInterceptors() {
    this.api.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error?.config || {};
        const status = error?.response?.status;
        const data = error?.response?.data;

        const tokenInvalid =
          data?.code === "token_not_valid" ||
          (Array.isArray(data?.messages) &&
            data.messages.some((m) =>
              String(m?.message || "")
                .toLowerCase()
                .includes("token is expired")
            )) ||
          status === 401;
        const hadAuthHeader =
          !!originalRequest?.headers?.Authorization ||
          !!this.api.defaults.headers.common.Authorization;

        if (!tokenInvalid || originalRequest._retry || !hadAuthHeader) {
          return Promise.reject(error);
        }

        originalRequest._retry = true;
        const newAccessToken = await this._refreshAccessToken();

        if (!newAccessToken) {
          this._clearAuth();
          return Promise.reject(error);
        }

        originalRequest.headers = {
          ...(originalRequest.headers || {}),
          Authorization: `Bearer ${newAccessToken}`,
        };

        return this.api(originalRequest);
      }
    );
  }

  _getStoredAuth() {
    try {
      const detail = JSON.parse(localStorage.getItem("userDetail") || "{}");
      return {
        user: detail?.user || null,
        accessToken: detail?.access || detail?.accessToken || detail?.token,
        refreshToken: detail?.refresh || detail?.refreshToken,
      };
    } catch {
      return {
        user: null,
        accessToken: null,
        refreshToken: null,
      };
    }
  }

  _persistAuth(payload = {}) {
    const authStore = useAuth();
    authStore.setAuth(payload);
    localStorage.setItem(
      "userDetail",
      JSON.stringify({
        user: payload?.user || null,
        access: payload?.accessToken || null,
        refresh: payload?.refreshToken || null,
      })
    );
  }

  _clearAuth() {
    const authStore = useAuth();
    authStore.setAuth(undefined);
    localStorage.removeItem("userDetail");
  }

  _getRefreshEndpoints() {
    const strip = (v) => String(v || "").replace(/\/+$/, "");
    const apiBase = strip(backendApiUrl);
    const authBase = strip(authApiUrl);

    const endpoints = [
     
      `${authBase}/user/auth/token/refresh/`,
      `${authBase}/user/auth/token/refresh`,
    ].filter((url) => {
      if (!url || url.startsWith("/")) return false;
      if (url.startsWith("undefined")) return false;
      if (url.startsWith("null")) return false;
      return true;
    });

    return [...new Set(endpoints)];
  }

  async _refreshAccessToken() {
    const authStore = useAuth();
    const stored = this._getStoredAuth();
    const currentAuth = authStore.auth || {};
    const refreshToken = currentAuth?.refreshToken || stored?.refreshToken;

    if (!refreshToken) {
      console.warn("[ApiService] no refresh token found in auth store/localStorage");
      return null;
    }

    if (ApiService.refreshPromise) {
      return ApiService.refreshPromise;
    }

    ApiService.refreshPromise = (async () => {
      const endpoints = this._getRefreshEndpoints();
      const payloads = [{ refresh: refreshToken }, { refreshToken }];

      for (const endpoint of endpoints) {
        for (const payload of payloads) {
          try {
            console.log("[ApiService] trying token refresh:", endpoint);
            const res = await axios.post(endpoint, payload, {
              headers: { "Content-Type": "application/json" },
            });

            const accessToken = res?.data?.access || res?.data?.token;
            const nextRefreshToken = res?.data?.refresh || refreshToken;
            if (!accessToken) continue;

            const authPayload = {
              user: currentAuth?.user || stored?.user || null,
              accessToken,
              refreshToken: nextRefreshToken,
            };

            this._persistAuth(authPayload);
            this.api.defaults.headers.common.Authorization = `Bearer ${accessToken}`;
            return accessToken;
          } catch (e) {
            console.warn("[ApiService] token refresh failed:", endpoint, e?.response?.status || e?.message);
            // try next endpoint/payload combination
          }
        }
      }

      return null;
    })().finally(() => {
      ApiService.refreshPromise = null;
    });

    return ApiService.refreshPromise;
  }

  /**
   * Helper to conditionally set Content-Type
   */
  _getHeaders(data, configHeaders = {}) {
    const isFormData = data instanceof FormData;

    return {
      ...configHeaders,
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
    };
  }

  async get(url, config = {}) {
    return await responseHandler(
      this.api({
        ...config,
        url,
        method: "get",
      })
    );
  }

  async post(url, data, config = {}) {
    return await responseHandler(
      this.api({
        ...config,
        url,
        data,
        method: "post",
        headers: this._getHeaders(data, config.headers),
      })
    );
  }

async put(url, data, config = {}) {
  const headers = this._getHeaders(data, config.headers);

  return await responseHandler(
    this.api({
      ...config,
      url,
      data,
      method: "put",
      headers,
    })
  );
}


  async patch(url, data, config = {}) {
    return await responseHandler(
      this.api({
        ...config,
        url,
        data,
        method: "patch",
        headers: this._getHeaders(data, config.headers),
      })
    );
  }

  async delete(url, config = {}) {
    return await responseHandler(
      this.api({
        ...config,
        url,
        method: "delete",
      })
    );
  }
}
