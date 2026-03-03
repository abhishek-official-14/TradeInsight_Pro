const RAZORPAY_SCRIPT_ID = 'razorpay-checkout-script';
const RAZORPAY_CHECKOUT_URL = 'https://checkout.razorpay.com/v1/checkout.js';

const getRazorpayConstructor = () => {
  if (typeof window === 'undefined') {
    return null;
  }

  return window.Razorpay || null;
};

export const loadRazorpayCheckout = () => {
  if (getRazorpayConstructor()) {
    return Promise.resolve();
  }

  if (typeof document === 'undefined') {
    return Promise.reject(new Error('Razorpay checkout can only be loaded in a browser.'));
  }

  const existingScript = document.getElementById(RAZORPAY_SCRIPT_ID);
  if (existingScript) {
    return new Promise((resolve, reject) => {
      existingScript.addEventListener('load', () => resolve(), { once: true });
      existingScript.addEventListener('error', () => reject(new Error('Failed to load Razorpay checkout.')), { once: true });
    });
  }

  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.id = RAZORPAY_SCRIPT_ID;
    script.src = RAZORPAY_CHECKOUT_URL;
    script.async = true;
    script.onload = () => resolve();
    script.onerror = () => reject(new Error('Failed to load Razorpay checkout.'));

    document.body.appendChild(script);
  });
};

/**
 * @param {Object} options
 * @returns {Promise<{razorpay_order_id: string, razorpay_payment_id: string, razorpay_signature: string}>}
 */
export const openRazorpayCheckout = async (options) => {
  await loadRazorpayCheckout();

  const Razorpay = getRazorpayConstructor();
  if (!Razorpay) {
    throw new Error('Razorpay SDK unavailable after loading script.');
  }

  return new Promise((resolve, reject) => {
    const checkout = new Razorpay({
      ...options,
      handler: (response) => resolve(response),
      modal: {
        ...options?.modal,
        ondismiss: () => reject(new Error('Payment checkout was dismissed.')),
      },
    });

    checkout.on('payment.failed', (event) => {
      const description = event?.error?.description || 'Payment failed. Please try again.';
      reject(new Error(description));
    });

    checkout.open();
  });
};
