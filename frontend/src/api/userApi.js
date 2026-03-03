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
 * @typedef {Object} TelegramLinkRequest
 * @property {string} telegram_id
 */

export const userApi = {
  /** @returns {Promise<UserRead>} */
  getMe: () => unwrapResponse(apiClient.get('/users/me')),

  /**
   * @param {TelegramLinkRequest} payload
   * @returns {Promise<UserRead>}
   */
  linkTelegram: (payload) => unwrapResponse(apiClient.put('/users/me/telegram-link', payload)),
};
