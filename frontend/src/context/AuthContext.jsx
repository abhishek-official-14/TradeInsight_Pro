import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { authApi } from '../api/authApi';
import { clearStoredAuth, getStoredAuth, setStoredAuth } from '../utils/storage';

const AuthContext = createContext(null);

const ROLE_FALLBACK = 'free';
const ROLE_PRIORITY = {
  free: 0,
  pro: 1,
  admin: 2,
};

const decodeTokenPayload = (token) => {
  if (!token || typeof token !== 'string') {
    return null;
  }

  try {
    const [, payload] = token.split('.');
    if (!payload) {
      return null;
    }

    const normalizedPayload = payload.replace(/-/g, '+').replace(/_/g, '/');
    const paddedPayload = normalizedPayload.padEnd(normalizedPayload.length + ((4 - (normalizedPayload.length % 4)) % 4), '=');
    const decodedPayload = atob(paddedPayload);
    return JSON.parse(decodedPayload);
  } catch {
    return null;
  }
};

const normalizeRole = (role) => (ROLE_PRIORITY[role] !== undefined ? role : ROLE_FALLBACK);

const resolveRole = (userRole, token) => {
  const tokenPayload = decodeTokenPayload(token);
  const tokenRole = tokenPayload?.role || tokenPayload?.user_role || tokenPayload?.permissions?.role;
  return normalizeRole(userRole || tokenRole);
};

const withResolvedRole = (authPayload) => {
  if (!authPayload?.token) {
    return authPayload;
  }

  const resolvedRole = resolveRole(authPayload?.user?.role, authPayload.token);

  return {
    ...authPayload,
    user: {
      ...(authPayload.user || {}),
      role: resolvedRole,
    },
  };
};

export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState(() => withResolvedRole(getStoredAuth()));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const hydrate = async () => {
      if (!auth?.token) {
        setLoading(false);
        return;
      }

      try {
        const profile = await authApi.me();
        const updated = withResolvedRole({ ...auth, user: { ...profile, role: resolveRole(profile?.role, auth.token) } });
        setAuth(updated);
        setStoredAuth(updated);
      } catch {
        clearStoredAuth();
        setAuth(null);
      } finally {
        setLoading(false);
      }
    };

    hydrate();

    const handleAutoLogout = () => {
      setAuth(null);
      clearStoredAuth();
    };

    window.addEventListener('auth:logout', handleAutoLogout);
    return () => {
      window.removeEventListener('auth:logout', handleAutoLogout);
    };
  }, []);

  const login = async (payload) => {
    const result = await authApi.login(payload);
    const normalized = withResolvedRole({
      token: result.access_token || result.token,
      refreshToken: result.refresh_token || null,
      user: result.user || { email: payload.email, role: result.role || ROLE_FALLBACK },
    });

    setAuth(normalized);
    setStoredAuth(normalized);
  };

  const register = async (payload) => {
    const result = await authApi.register(payload);
    return result;
  };


  const refreshUser = async () => {
    if (!auth?.token) {
      return null;
    }

    const profile = await authApi.me();
    const updated = withResolvedRole({ ...auth, user: { ...profile, role: resolveRole(profile?.role, auth.token) } });
    setAuth(updated);
    setStoredAuth(updated);
    return updated.user;
  };

  const logout = () => {
    setAuth(null);
    clearStoredAuth();
  };

  const value = useMemo(
    () => ({
      auth,
      user: auth?.user,
      token: auth?.token,
      loading,
      role: auth?.user?.role || ROLE_FALLBACK,
      isAuthenticated: Boolean(auth?.token),
      hasRole: (requiredRoles = []) => {
        if (!requiredRoles.length) {
          return true;
        }

        const currentRole = auth?.user?.role || ROLE_FALLBACK;
        return requiredRoles.includes(currentRole);
      },
      login,
      register,
      logout,
      refreshUser,
    }),
    [auth, loading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
