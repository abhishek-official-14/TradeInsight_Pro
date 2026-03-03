import axios from 'axios';
import { ENV } from '../utils/env';
import { clearStoredAuth, getStoredAuth } from '../utils/storage';

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
  (error) => {
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
