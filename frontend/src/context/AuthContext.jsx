import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { authApi } from '../api/authApi';
import { clearStoredAuth, getStoredAuth, setStoredAuth } from '../utils/storage';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [auth, setAuth] = useState(() => getStoredAuth());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const hydrate = async () => {
      if (!auth?.token) {
        setLoading(false);
        return;
      }

      try {
        const profile = await authApi.me();
        const updated = { ...auth, user: profile };
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
  }, []);

  const login = async (payload) => {
    const result = await authApi.login(payload);
    const normalized = {
      token: result.access_token || result.token,
      user: result.user || { email: payload.email, role: result.role || 'user' },
    };
    setAuth(normalized);
    setStoredAuth(normalized);
  };

  const register = async (payload) => {
    const result = await authApi.register(payload);
    return result;
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
      isAuthenticated: Boolean(auth?.token),
      login,
      register,
      logout,
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
