import { apiClient } from './client';

export const marketApi = {
  getDashboard: async () => {
    const response = await apiClient.get('/nifty/dashboard');
    return response.data;
  },
  getOptionAnalysis: async () => {
    const response = await apiClient.get('/options/analysis');
    return response.data;
  },
  getSubscription: async () => {
    const response = await apiClient.get('/subscription/current');
    return response.data;
  },
  getAdminOverview: async () => {
    const response = await apiClient.get('/admin/overview');
    return response.data;
  },
};
