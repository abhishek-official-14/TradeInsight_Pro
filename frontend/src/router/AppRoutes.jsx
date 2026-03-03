import { Navigate, Route, Routes } from 'react-router-dom';
import { AppLayout } from '../layouts/AppLayout';
import { AdminPanelPage } from '../pages/AdminPanelPage';
import { AdminSubscriptionsPage } from '../pages/AdminSubscriptionsPage';
import { ApiUsageLogsPage } from '../pages/ApiUsageLogsPage';
import { DashboardPage } from '../pages/DashboardPage';
import { DesignSystemPage } from '../pages/DesignSystemPage';
import { FeatureFlagsPage } from '../pages/FeatureFlagsPage';
import { LoginPage } from '../pages/LoginPage';
import { OptionAnalysisPage } from '../pages/OptionAnalysisPage';
import { ProfilePage } from '../pages/ProfilePage';
import { ProAnalyticsPage } from '../pages/ProAnalyticsPage';
import { RegisterPage } from '../pages/RegisterPage';
import { SubscriptionPage } from '../pages/SubscriptionPage';
import { TelegramSettingsPage } from '../pages/TelegramSettingsPage';
import { ProtectedRoute } from './ProtectedRoute';

export const AppRoutes = () => (
  <Routes>
    <Route path="/" element={<Navigate to="/dashboard" replace />} />
    <Route path="/login" element={<LoginPage />} />
    <Route path="/register" element={<RegisterPage />} />
    <Route path="/design-system" element={<DesignSystemPage />} />

    <Route element={<ProtectedRoute />}>
      <Route element={<AppLayout />}>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/option-analysis" element={<OptionAnalysisPage />} />
        <Route path="/subscription" element={<SubscriptionPage />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/settings/telegram" element={<TelegramSettingsPage />} />
      </Route>
    </Route>

    <Route element={<ProtectedRoute roles={['pro', 'admin']} />}>
      <Route element={<AppLayout />}>
        <Route path="/pro-analytics" element={<ProAnalyticsPage />} />
      </Route>
    </Route>

    <Route element={<ProtectedRoute roles={['admin']} />}>
      <Route element={<AppLayout />}>
        <Route path="/admin" element={<AdminPanelPage />} />
        <Route path="/admin/subscriptions" element={<AdminSubscriptionsPage />} />
        <Route path="/admin/api-usage-logs" element={<ApiUsageLogsPage />} />
        <Route path="/admin/feature-flags" element={<FeatureFlagsPage />} />
      </Route>
    </Route>

    <Route path="*" element={<Navigate to="/dashboard" replace />} />
  </Routes>
);
