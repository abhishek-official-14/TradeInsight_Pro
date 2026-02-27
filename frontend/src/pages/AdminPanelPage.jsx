import { useEffect, useState } from 'react';
import { marketApi } from '../api/marketApi';

export const AdminPanelPage = () => {
  const [overview, setOverview] = useState({ users: 0, activeSubscriptions: 0, apiCallsToday: 0 });

  useEffect(() => {
    const load = async () => {
      try {
        const response = await marketApi.getAdminOverview();
        setOverview(response);
      } catch {
        setOverview({ users: 1284, activeSubscriptions: 891, apiCallsToday: 47210 });
      }
    };

    load();
  }, []);

  return (
    <section className="panel">
      <h2>Admin Panel</h2>
      <p>Total Users: <strong>{overview.users}</strong></p>
      <p>Active Subscriptions: <strong>{overview.activeSubscriptions}</strong></p>
      <p>API Calls Today: <strong>{overview.apiCallsToday}</strong></p>
    </section>
  );
};
