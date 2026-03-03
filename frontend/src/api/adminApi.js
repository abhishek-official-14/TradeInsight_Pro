import { apiClient, unwrapResponse } from './client';

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

/**
 * @typedef {Object} SubscriptionAdminRead
 * @property {number} id
 * @property {number} user_id
 * @property {string} user_email
 * @property {string} status
 * @property {string} razorpay_order_id
 * @property {string | null} razorpay_payment_id
 * @property {string | null} expiry_date
 * @property {string} created_at
 */

/**
 * @typedef {Object} APIUsageLogRead
 * @property {number} id
 * @property {number | null} user_id
 * @property {string} method
 * @property {string} path
 * @property {number} status_code
 * @property {string | null} ip_address
 * @property {string} created_at
 */

/**
 * @typedef {Object} FeatureFlagRead
 * @property {number} id
 * @property {string} name
 * @property {boolean} enabled
 * @property {string} updated_at
 */

export const adminApi = {
  /** @returns {Promise<{items: UserRead[], total: number, page: number, size: number}>} */
  getUsers: (params = {}) => unwrapResponse(apiClient.get('/admin/users', { params })),

  /** @returns {Promise<UserRead>} */
  updateUserRole: (userId, role) =>
    unwrapResponse(apiClient.patch(`/admin/users/${userId}/role`, { role })),

  /** @returns {Promise<{items: SubscriptionAdminRead[], total: number, page: number, size: number}>} */
  getSubscriptions: (params = {}) => unwrapResponse(apiClient.get('/admin/subscriptions', { params })),

  /** @returns {Promise<{items: APIUsageLogRead[], total: number, page: number, size: number}>} */
  getApiUsageLogs: (params = {}) => unwrapResponse(apiClient.get('/admin/api-usage-logs', { params })),

  /** @returns {Promise<{items: FeatureFlagRead[], total: number, page: number, size: number}>} */
  getFeatureFlags: (params = {}) => unwrapResponse(apiClient.get('/admin/feature-flags', { params })),

  /** @returns {Promise<FeatureFlagRead>} */
  toggleFeatureFlag: (name, enabled) =>
    unwrapResponse(apiClient.patch(`/admin/feature-flags/${name}`, { enabled })),
};
