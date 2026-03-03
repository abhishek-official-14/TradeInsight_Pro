import { apiClient, unwrapResponse } from './client';

/**
 * @typedef {Object} NiftySnapshotRead
 * @property {number} id
 * @property {string} symbol
 * @property {number} price
 * @property {string} captured_at
 */

/**
 * @typedef {Object} NiftyConstituentImpact
 * @property {string} symbol
 * @property {string} company_name
 * @property {number} weight
 * @property {number} last_price
 * @property {number} percent_change
 * @property {number} impact
 */

/**
 * @typedef {Object} NiftyImpactResponse
 * @property {string} index
 * @property {number} total_impact
 * @property {NiftyConstituentImpact[]} top_draggers
 * @property {NiftyConstituentImpact[]} constituents
 */

export const niftyApi = {
  /** @returns {Promise<NiftySnapshotRead>} */
  getLatest: () => unwrapResponse(apiClient.get('/nifty/latest')),

  /** @returns {Promise<NiftyImpactResponse>} */
  getImpact: () => unwrapResponse(apiClient.get('/nifty/impact')),

  /** @returns {Promise<Record<string, number>>} */
  getSectorHeatmap: () => unwrapResponse(apiClient.get('/nifty/impact/sector-heatmap')),
};
