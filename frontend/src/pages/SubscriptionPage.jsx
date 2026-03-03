import { useMemo, useState } from 'react';
import { subscriptionApi } from '../api/subscriptionApi';
import { useAuth } from '../context/AuthContext';
import { openRazorpayCheckout } from '../utils/razorpay';
import styles from './SubscriptionPage.module.css';

const PRO_PLAN = {
  id: 'pro-monthly',
  name: 'Pro Plan',
  description: 'Unlock pro analytics, premium indicators, and advanced trading insights.',
  amountInPaise: 49900,
  currency: 'INR',
  interval: 'Monthly',
};

const formatPrice = (amountInPaise, currency) =>
  new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
  }).format(amountInPaise / 100);

export const SubscriptionPage = () => {
  const { user, refreshUser } = useAuth();
  const [isPaying, setIsPaying] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const isProOrAbove = useMemo(() => user?.role === 'pro' || user?.role === 'admin', [user?.role]);

  const handleSubscribe = async () => {
    setIsPaying(true);
    setError('');
    setMessage('Creating payment order...');

    try {
      const order = await subscriptionApi.createOrder({
        amount: PRO_PLAN.amountInPaise,
        currency: PRO_PLAN.currency,
      });

      setMessage('Opening Razorpay checkout...');

      const paymentResponse = await openRazorpayCheckout({
        key: order.key_id,
        order_id: order.order_id,
        amount: order.amount,
        currency: order.currency,
        name: 'TradeInsight Pro',
        description: `${PRO_PLAN.name} (${PRO_PLAN.interval})`,
        prefill: {
          email: user?.email || '',
          name: user?.full_name || '',
        },
        notes: {
          planId: PRO_PLAN.id,
        },
        theme: {
          color: '#1f7aec',
        },
      });

      setMessage('Verifying payment...');

      await subscriptionApi.verifyPayment(paymentResponse);
      await refreshUser();

      setMessage('Payment verified. Your role has been updated successfully.');
    } catch (checkoutError) {
      setError(checkoutError?.response?.data?.detail || checkoutError?.message || 'Unable to complete subscription payment.');
      setMessage('');
    } finally {
      setIsPaying(false);
    }
  };

  return (
    <section className="panel">
      <h2>Subscription</h2>
      <p>
        Current role: <strong>{user?.role || 'free'}</strong>
      </p>

      <div className={styles.planCard}>
        <h3>{PRO_PLAN.name}</h3>
        <p>{PRO_PLAN.description}</p>
        <p>
          Price: <strong>{formatPrice(PRO_PLAN.amountInPaise, PRO_PLAN.currency)}</strong> / {PRO_PLAN.interval}
        </p>

        <button type="button" onClick={handleSubscribe} disabled={isPaying || isProOrAbove}>
          {isProOrAbove ? 'Already Active' : isPaying ? 'Processing...' : 'Subscribe with Razorpay'}
        </button>
      </div>

      {message ? <p className={styles.status}>{message}</p> : null}
      {error ? (
        <p className={styles.error}>
          <strong>Error:</strong> {error}
        </p>
      ) : null}
    </section>
  );
};
