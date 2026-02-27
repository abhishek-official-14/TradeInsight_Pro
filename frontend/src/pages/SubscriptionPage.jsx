import { useEffect, useState } from 'react';
import { marketApi } from '../api/marketApi';

export const SubscriptionPage = () => {
  const [plan, setPlan] = useState({ tier: 'Pro', status: 'Active', renewalDate: '2026-01-12' });

  useEffect(() => {
    const load = async () => {
      try {
        const response = await marketApi.getSubscription();
        setPlan(response);
      } catch {
        setPlan({ tier: 'Pro', status: 'Active', renewalDate: '2026-01-12' });
      }
    };

    load();
  }, []);

  return (
    <section className="panel">
      <h2>Subscription</h2>
      <p>Tier: <strong>{plan.tier}</strong></p>
      <p>Status: <strong>{plan.status}</strong></p>
      <p>Renewal Date: <strong>{plan.renewalDate}</strong></p>
      <button type="button">Manage Billing</button>
    </section>
  );
};
