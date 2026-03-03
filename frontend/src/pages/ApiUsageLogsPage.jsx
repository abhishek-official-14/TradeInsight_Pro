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

export const ApiUsageLogsPage = () => {
  const [logs, setLogs] = useState([]);
  const [meta, setMeta] = useState({ page: 1, size: 20, total: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadLogs = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await adminApi.getApiUsageLogs({ page: 1, size: 20 });
        setLogs(response.items || []);
        setMeta({
          page: response.page ?? 1,
          size: response.size ?? 20,
          total: response.total ?? 0,
        });
      } catch (err) {
        setError(err?.message || 'Unable to load API usage logs right now.');
      } finally {
        setLoading(false);
      }
    };

    loadLogs();
  }, []);

  return (
    <section className="panel">
      <div className="panel-head">
        <h2>API Usage Logs</h2>
        {!loading && !error && <span className="metric-hint">{meta.total} total records</span>}
      </div>

      {loading && <p className="metric-hint">Loading API usage logs…</p>}
      {error && <p className="error-text">{error}</p>}

      {!loading && !error && (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Time</th>
                <th>User ID</th>
                <th>Method</th>
                <th>Path</th>
                <th>Status</th>
                <th>IP</th>
              </tr>
            </thead>
            <tbody>
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={6} className="metric-hint">No usage logs found.</td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id}>
                    <td>{formatDate(log.created_at)}</td>
                    <td>{log.user_id ?? 'Anonymous'}</td>
                    <td>{log.method}</td>
                    <td>{log.path}</td>
                    <td className={log.status_code >= 400 ? 'negative' : 'success-text'}>{log.status_code}</td>
                    <td>{log.ip_address || '—'}</td>
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
