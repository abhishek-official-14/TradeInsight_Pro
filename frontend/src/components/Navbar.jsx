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
        <NavLink to="/subscription">Subscription</NavLink>
        <NavLink to="/profile">Profile</NavLink>
        {user?.role === 'admin' && <NavLink to="/admin">Admin Panel</NavLink>}
      </nav>
      <button type="button" className="ghost-btn" onClick={logout}>
        Logout
      </button>
    </header>
  );
};
