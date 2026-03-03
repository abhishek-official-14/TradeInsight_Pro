import { Link, NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const Navbar = () => {
  const { user, logout } = useAuth();

  return (
    <header className="nav-shell">
      <Link to="/dashboard" className="brand">
        TradeInsight <span>Pro</span>
      </Link>
      <nav>
        <NavLink to="/dashboard">Dashboard</NavLink>
        <NavLink to="/option-analysis">Option Analysis</NavLink>
        {(user?.role === 'pro' || user?.role === 'admin') && (
          <NavLink to="/pro-analytics">Pro Analytics</NavLink>
        )}
        <NavLink to="/subscription">Subscription</NavLink>
        <NavLink to="/profile">Profile</NavLink>
        <NavLink to="/settings/telegram">Telegram Settings</NavLink>
        {user?.role === 'admin' && <NavLink to="/admin">Admin Panel</NavLink>}
        {user?.role === 'admin' && <NavLink to="/admin/api-usage-logs">API Logs</NavLink>}
        {user?.role === 'admin' && <NavLink to="/admin/feature-flags">Feature Flags</NavLink>}
      </nav>
      <button type="button" className="ghost-btn" onClick={logout}>
        Logout
      </button>
    </header>
  );
};
