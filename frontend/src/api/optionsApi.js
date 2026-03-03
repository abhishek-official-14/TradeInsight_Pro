import { apiClient, unwrapResponse } from './client';

/**
 * @typedef {Object} OptionContractRead
 * @property {number} id
 * @property {string} symbol
 * @property {number} strike_price
 * @property {number} premium
 * @property {string} option_type
 * @property {string | null} updated_at
 */

/**
 * @typedef {Object} OptionsAnalyticsResponse
 * @property {string} symbol
 * @property {string} expiry_date
 * @property {number | null} underlying_value
 * @property {string} timestamp
 * @property {number} total_call_oi
 * @property {number} total_put_oi
 * @property {number | null} pcr
 * @property {number} change_in_call_oi
 * @property {number} change_in_put_oi
 * @property {number | null} change_oi_pcr
 * @property {number | null} strongest_support
 * @property {number | null} strongest_resistance
 * @property {number | null} max_pain
 */

export const optionsApi = {
  /**
   * @param {{limit?: number}} [params]
   * @returns {Promise<OptionContractRead[]>}
   */
  getLatest: (params = {}) => unwrapResponse(apiClient.get('/options/latest', { params })),

  /**
   * @param {{symbol?: string, expiry_date?: string | null}} [params]
   * @returns {Promise<OptionsAnalyticsResponse>}
   */
  getAnalytics: (params = {}) => unwrapResponse(apiClient.get('/options/analytics', { params })),
};
