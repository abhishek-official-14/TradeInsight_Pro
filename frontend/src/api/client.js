import axios from 'axios';
import { ENV } from '../utils/env';
import { clearStoredAuth, getStoredAuth, setStoredAuth } from '../utils/storage';

/**
 * Normalized API error with useful metadata.
 */
export class ApiError extends Error {
  /**
   * @param {string} message
   * @param {number | undefined} status
   * @param {unknown} details
   */
  constructor(message, status, details) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

/**
 * @param {unknown} error
 * @returns {ApiError}
 */
export const normalizeApiError = (error) => {
  const status = error?.response?.status;
  const details = error?.response?.data;
  const message =
    details?.detail ||
    details?.message ||
    error?.message ||
    'An unexpected API error occurred';

  return new ApiError(message, status, details);
};

/**
 * Shared Axios instance for all API modules.
 */
export const apiClient = axios.create({
  baseURL: ENV.API_BASE_URL,
  timeout: 15000,
});

const refreshClient = axios.create({
  baseURL: ENV.API_BASE_URL,
  timeout: 15000,
});

let refreshPromise = null;

const refreshAccessToken = async () => {
  const auth = getStoredAuth();
  const refreshToken = auth?.refreshToken || auth?.refresh_token;

  if (!refreshToken) {
    throw new Error('Missing refresh token');
  }

  const response = await refreshClient.post('/auth/refresh', { refresh_token: refreshToken });
  const tokenPayload = response.data;

  const updatedAuth = {
    ...auth,
    token: tokenPayload?.access_token || auth?.token,
    refreshToken: tokenPayload?.refresh_token || refreshToken,
  };

  setStoredAuth(updatedAuth);
  return updatedAuth;
};

apiClient.interceptors.request.use((config) => {
  const auth = getStoredAuth();
  const token = auth?.token || auth?.access_token;

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error?.config;

    if (error?.response?.status === 401 && !originalRequest?._retry) {
      originalRequest._retry = true;

      try {
        refreshPromise = refreshPromise || refreshAccessToken();
        const updatedAuth = await refreshPromise;
        refreshPromise = null;

        originalRequest.headers = {
          ...(originalRequest.headers || {}),
          Authorization: `Bearer ${updatedAuth.token}`,
        };

        return apiClient(originalRequest);
      } catch {
        refreshPromise = null;
        clearStoredAuth();
        window.dispatchEvent(new CustomEvent('auth:logout'));
      }
    }

    if (error?.response?.status === 401) {
      clearStoredAuth();
      window.dispatchEvent(new CustomEvent('auth:logout'));
    }

    return Promise.reject(normalizeApiError(error));
  }
);

/**
 * @template T
 * @param {Promise<import('axios').AxiosResponse<T>>} requestPromise
 * @returns {Promise<T>}
 */
export const unwrapResponse = async (requestPromise) => {
  try {
    const response = await requestPromise;
    return response.data;
  } catch (error) {
    throw normalizeApiError(error);
  }
};
