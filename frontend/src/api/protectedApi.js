import { apiClient, unwrapResponse } from './client';

/**
 * @typedef {Object} ProtectedMessageResponse
 * @property {string} message
 */

export const protectedApi = {
  /** @returns {Promise<ProtectedMessageResponse>} */
  getProMessage: () => unwrapResponse(apiClient.get('/protected/pro')),
};
