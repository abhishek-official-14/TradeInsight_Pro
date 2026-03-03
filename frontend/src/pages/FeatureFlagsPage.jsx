import { useEffect, useState } from 'react';
import { adminApi } from '../api/adminApi';

const DATE_FORMATTER = new Intl.DateTimeFormat(undefined, {
  dateStyle: 'medium',
  timeStyle: 'short',
});

const formatDate = (value) => {
  if (!value) return '—';
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : DATE_FORMATTER.format(parsed);
};

export const FeatureFlagsPage = () => {
  const [flags, setFlags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadFlags = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await adminApi.getFeatureFlags({ page: 1, size: 50 });
        setFlags(response.items || []);
      } catch (err) {
        setError(err?.message || 'Unable to load feature flags.');
      } finally {
        setLoading(false);
      }
    };

    loadFlags();
  }, []);

  const toggleFlag = async (flag) => {
    setError('');
    const nextEnabled = !flag.enabled;

    setFlags((current) =>
      current.map((item) => (item.name === flag.name ? { ...item, enabled: nextEnabled } : item))
    );

    try {
      const updated = await adminApi.toggleFeatureFlag(flag.name, nextEnabled);
      setFlags((current) =>
        current.map((item) => (item.name === updated.name ? { ...item, ...updated } : item))
      );
    } catch (err) {
      setFlags((current) =>
        current.map((item) => (item.name === flag.name ? { ...item, enabled: flag.enabled } : item))
      );
      setError(err?.message || `Unable to update ${flag.name}.`);
    }
  };

  return (
    <section className="panel">
      <div className="panel-head">
        <h2>Feature Flags</h2>
        <span className="metric-hint">Admin controls</span>
      </div>

      {loading && <p className="metric-hint">Loading feature flags…</p>}
      {error && <p className="error-text">{error}</p>}

      {!loading && !error && (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Updated</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {flags.length === 0 ? (
                <tr>
                  <td colSpan={4} className="metric-hint">No feature flags configured.</td>
                </tr>
              ) : (
                flags.map((flag) => (
                  <tr key={flag.id}>
                    <td>{flag.name}</td>
                    <td className={flag.enabled ? 'success-text' : 'negative'}>
                      {flag.enabled ? 'Enabled' : 'Disabled'}
                    </td>
                    <td>{formatDate(flag.updated_at)}</td>
                    <td>
                      <button type="button" onClick={() => toggleFlag(flag)}>
                        {flag.enabled ? 'Disable' : 'Enable'}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
};
