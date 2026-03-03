import { useEffect, useState } from 'react';
import { adminApi } from '../api/adminApi';

const DATE_FORMATTER = new Intl.DateTimeFormat(undefined, {
  dateStyle: 'medium',
  timeStyle: 'short',
});

const formatDate = (value) => {
  if (!value) return '—';
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : DATE_FORMATTER.format(parsed);
};

export const AdminSubscriptionsPage = () => {
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError('');

      try {
        const response = await adminApi.getSubscriptions({ page: 1, size: 50 });
        setSubscriptions(response.items || []);
      } catch (err) {
        setError(err?.message || 'Unable to load subscriptions.');
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Subscription Management</h2>
        <span className="metric-hint">Admin overview</span>
      </div>

      {loading && <p className="metric-hint">Loading subscriptions…</p>}
      {error && <p className="error-text">{error}</p>}

      {!loading && !error && (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>User</th>
                <th>Status</th>
                <th>Order ID</th>
                <th>Payment ID</th>
                <th>Expiry</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {subscriptions.length === 0 ? (
                <tr>
                  <td colSpan={6} className="metric-hint">
                    No subscriptions found.
                  </td>
                </tr>
              ) : (
                subscriptions.map((subscription) => (
                  <tr key={subscription.id}>
                    <td>{subscription.user_email}</td>
                    <td className={subscription.status === 'active' ? 'success-text' : 'negative'}>{subscription.status}</td>
                    <td>{subscription.razorpay_order_id}</td>
                    <td>{subscription.razorpay_payment_id || '—'}</td>
                    <td>{formatDate(subscription.expiry_date)}</td>
                    <td>{formatDate(subscription.created_at)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
};
