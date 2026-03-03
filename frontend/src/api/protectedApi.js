import { apiClient, unwrapResponse } from './client';

/**
 * @typedef {Object} ProtectedMessageResponse
 * @property {string} message
 */

export const protectedApi = {
  /** @returns {Promise<ProtectedMessageResponse>} */
  getFreeMessage: () => unwrapResponse(apiClient.get('/protected/free')),

  /** @returns {Promise<ProtectedMessageResponse>} */
  getProMessage: () => unwrapResponse(apiClient.get('/protected/pro')),

  /** @returns {Promise<ProtectedMessageResponse>} */
  getAdminMessage: () => unwrapResponse(apiClient.get('/protected/admin')),
};
