import { apiClient } from './client';

export const authApi = {
  login: async (payload) => {
    const response = await apiClient.post('/auth/login', payload);
    return response.data;
  },
  register: async (payload) => {
    const response = await apiClient.post('/auth/register', payload);
    return response.data;
  },
  me: async () => {
    const response = await apiClient.get('/users/me');
    return response.data;
  },
};
