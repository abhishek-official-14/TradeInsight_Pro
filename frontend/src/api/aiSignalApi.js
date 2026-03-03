import { apiClient, unwrapResponse } from './client';

/**
 * @typedef {Object} AISignalEngineResponse
 * @property {number} score
 * @property {string} classification
 */

export const aiSignalApi = {
  /** @returns {Promise<AISignalEngineResponse>} */
  getLatest: () => unwrapResponse(apiClient.get('/ai-signal/latest')),
};
