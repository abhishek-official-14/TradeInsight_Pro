import { apiClient, unwrapResponse } from './client';

/**
 * @typedef {Object} SubscriptionOrderCreateRequest
 * @property {number} amount
 * @property {'INR'} [currency]
 */

/**
 * @typedef {Object} SubscriptionOrderCreateResponse
 * @property {string} order_id
 * @property {number} amount
 * @property {string} currency
 * @property {string} key_id
 */

/**
 * @typedef {Object} PaymentVerifyRequest
 * @property {string} razorpay_order_id
 * @property {string} razorpay_payment_id
 * @property {string} razorpay_signature
 */

export const subscriptionApi = {
  /**
   * @param {SubscriptionOrderCreateRequest} payload
   * @returns {Promise<SubscriptionOrderCreateResponse>}
   */
  createOrder: (payload) => unwrapResponse(apiClient.post('/subscription/create-order', payload)),

  /**
   * @param {PaymentVerifyRequest} payload
   * @returns {Promise<{message: string}>}
   */
  verifyPayment: (payload) => unwrapResponse(apiClient.post('/subscription/verify-payment', payload)),

  /**
   * @param {unknown} payload
   * @param {string} [signature]
   * @returns {Promise<{message: string}>}
   */
  webhook: (payload, signature) =>
    unwrapResponse(
      apiClient.post('/subscription/webhook', payload, {
        headers: signature ? { 'x-razorpay-signature': signature } : undefined,
      })
    ),
};
