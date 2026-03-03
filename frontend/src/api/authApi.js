import { apiClient, unwrapResponse } from './client';

/**
 * @typedef {Object} RegisterRequest
 * @property {string} email
 * @property {string} password
 * @property {string | null} [full_name]
 */

/**
 * @typedef {Object} LoginRequest
 * @property {string} email
 * @property {string} password
 */

/**
 * @typedef {Object} RefreshTokenRequest
 * @property {string} refresh_token
 */

/**
 * @typedef {Object} TokenResponse
 * @property {string} access_token
 * @property {string} refresh_token
 * @property {string} token_type
 */

/**
 * @typedef {Object} UserRead
 * @property {number} id
 * @property {string} email
 * @property {string | null} full_name
 * @property {string | null} telegram_id
 * @property {'free' | 'pro' | 'admin'} role
 * @property {boolean} is_active
 * @property {string} created_at
 */

export const authApi = {
  /** @param {RegisterRequest} payload */
  register: (payload) => unwrapResponse(apiClient.post('/auth/register', payload)),

  /** @param {LoginRequest} payload */
  login: (payload) => unwrapResponse(apiClient.post('/auth/login', payload)),

  /** @param {RefreshTokenRequest} payload */
  refresh: (payload) => unwrapResponse(apiClient.post('/auth/refresh', payload)),

  /** @returns {Promise<UserRead>} */
  me: () => unwrapResponse(apiClient.get('/users/me')),
};
