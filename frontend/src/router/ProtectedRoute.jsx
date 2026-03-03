import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const getDefaultRouteByRole = (role) => {
  if (role === 'admin') {
    return '/admin';
  }

  if (role === 'pro') {
    return '/pro-analytics';
  }

  return '/dashboard';
};

export const ProtectedRoute = ({ roles = [] }) => {
  const { isAuthenticated, role, loading, hasRole } = useAuth();
  const location = useLocation();

  if (loading) {
    return <div className="page-center">Loading session...</div>;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (!hasRole(roles)) {
    return <Navigate to={getDefaultRouteByRole(role)} replace />;
  }

  return <Outlet />;
};
