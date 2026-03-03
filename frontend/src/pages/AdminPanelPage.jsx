import { useEffect, useState } from 'react';
import { adminApi } from '../api/adminApi';
import { protectedApi } from '../api/protectedApi';

const ROLES = ['free', 'pro', 'admin'];

export const AdminPanelPage = () => {
  const [overview, setOverview] = useState({ users: 0, activeSubscriptions: 0, apiCallsToday: 0 });
  const [adminMessage, setAdminMessage] = useState('');
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError('');

      try {
        const [usersResponse, subscriptionsResponse, logsResponse, messageResponse] = await Promise.all([
          adminApi.getUsers({ page: 1, size: 20 }),
          adminApi.getSubscriptions({ page: 1, size: 100 }),
          adminApi.getApiUsageLogs({ page: 1, size: 100 }),
          protectedApi.getAdminMessage(),
        ]);

        const activeSubscriptions = (subscriptionsResponse?.items || []).filter(
          (subscription) => subscription.status === 'active'
        ).length;

        setOverview({
          users: usersResponse?.total || 0,
          activeSubscriptions,
          apiCallsToday: logsResponse?.items?.length || 0,
        });
        setUsers(usersResponse?.items || []);
        setAdminMessage(messageResponse?.message || '');
      } catch (err) {
        setError(err?.message || 'Unable to load admin overview.');
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const handleRoleChange = async (userId, nextRole) => {
    setError('');
    const previousUsers = users;
    setUsers((current) => current.map((user) => (user.id === userId ? { ...user, role: nextRole } : user)));

    try {
      const updated = await adminApi.updateUserRole(userId, nextRole);
      setUsers((current) => current.map((user) => (user.id === updated.id ? { ...user, ...updated } : user)));
    } catch (err) {
      setUsers(previousUsers);
      setError(err?.message || 'Unable to update user role.');
    }
  };

  return (
    <section className="panel">
      <h2>Admin Panel</h2>
      {loading && <p className="metric-hint">Loading admin overview…</p>}
      {error && <p className="error-text">{error}</p>}
      {!loading && !error && (
        <>
          {adminMessage ? <p>{adminMessage}</p> : null}
          <p>
            Total Users: <strong>{overview.users}</strong>
          </p>
          <p>
            Active Subscriptions: <strong>{overview.activeSubscriptions}</strong>
          </p>
          <p>
            Recent API Calls (latest page): <strong>{overview.apiCallsToday}</strong>
          </p>

          <h3>Users</h3>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Update Role</th>
                </tr>
              </thead>
              <tbody>
                {users.length === 0 ? (
                  <tr>
                    <td colSpan={3} className="metric-hint">
                      No users found.
                    </td>
                  </tr>
                ) : (
                  users.map((user) => (
                    <tr key={user.id}>
                      <td>{user.email}</td>
                      <td>{user.role}</td>
                      <td>
                        <select value={user.role} onChange={(event) => handleRoleChange(user.id, event.target.value)}>
                          {ROLES.map((role) => (
                            <option key={role} value={role}>
                              {role}
                            </option>
                          ))}
                        </select>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
};
