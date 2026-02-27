const AUTH_KEY = 'tradeinsight_auth';

export const getStoredAuth = () => {
  const raw = localStorage.getItem(AUTH_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw);
  } catch {
    localStorage.removeItem(AUTH_KEY);
    return null;
  }
};

export const setStoredAuth = (payload) => {
  localStorage.setItem(AUTH_KEY, JSON.stringify(payload));
};

export const clearStoredAuth = () => {
  localStorage.removeItem(AUTH_KEY);
};
