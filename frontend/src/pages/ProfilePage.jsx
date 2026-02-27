import { useAuth } from '../context/AuthContext';

export const ProfilePage = () => {
  const { user } = useAuth();

  return (
    <section className="panel">
      <h2>Profile</h2>
      <p>Name: <strong>{user?.name || 'Trader'}</strong></p>
      <p>Email: <strong>{user?.email || 'Not available'}</strong></p>
      <p>Role: <strong>{user?.role || 'user'}</strong></p>
    </section>
  );
};
