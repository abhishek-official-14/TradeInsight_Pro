import { useEffect, useState } from 'react';
import { aiSignalApi } from '../api/aiSignalApi';
import { optionsApi } from '../api/optionsApi';
import { protectedApi } from '../api/protectedApi';
import { MetricCard } from '../components/MetricCard';

export const ProAnalyticsPage = () => {
  const [data, setData] = useState({
    message: '',
    signal: null,
    analytics: null,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const loadAnalytics = async () => {
      setLoading(true);
      setError('');
      try {
        const [messageResponse, signalResponse, analyticsResponse] = await Promise.all([
          protectedApi.getProMessage(),
          aiSignalApi.getLatest(),
          optionsApi.getAnalytics({ symbol: 'NIFTY' }),
        ]);

        setData({
          message: messageResponse.message,
          signal: signalResponse,
          analytics: analyticsResponse,
        });
      } catch (err) {
        setError(err?.message || 'Unable to load pro analytics.');
      } finally {
        setLoading(false);
      }
    };

    loadAnalytics();
  }, []);

  return (
    <section className="dashboard-grid">
      <div className="panel" style={{ gridColumn: 'span 12' }}>
        <div className="panel-head">
          <h2>Pro Analytics</h2>
          <span className="metric-hint">Advanced options intelligence</span>
        </div>
        {loading && <p className="metric-hint">Loading pro analytics…</p>}
        {error && <p className="error-text">{error}</p>}
        {!loading && !error && <p>{data.message}</p>}
      </div>

      {!loading && !error && (
        <>
          <MetricCard
            title="AI Signal Score"
            value={data.signal?.score ?? '—'}
            tone={(data.signal?.score ?? 0) >= 60 ? 'positive' : 'negative'}
            hint={data.signal?.classification || 'No classification'}
          />
          <MetricCard
            title="Put/Call Ratio"
            value={data.analytics?.pcr ?? '—'}
            tone={(data.analytics?.pcr ?? 0) >= 1 ? 'positive' : 'negative'}
            hint="Live OI ratio"
          />
          <MetricCard
            title="Max Pain"
            value={data.analytics?.max_pain ?? '—'}
            tone="neutral"
            hint={`Expiry ${data.analytics?.expiry_date || 'N/A'}`}
          />

          <div className="panel" style={{ gridColumn: 'span 6' }}>
            <h3>Support vs Resistance</h3>
            <p>
              Strongest Support: <strong>{data.analytics?.strongest_support ?? '—'}</strong>
            </p>
            <p>
              Strongest Resistance: <strong>{data.analytics?.strongest_resistance ?? '—'}</strong>
            </p>
          </div>

          <div className="panel" style={{ gridColumn: 'span 6' }}>
            <h3>Open Interest Change</h3>
            <p>
              Call OI Change: <strong>{data.analytics?.change_in_call_oi ?? '—'}</strong>
            </p>
            <p>
              Put OI Change: <strong>{data.analytics?.change_in_put_oi ?? '—'}</strong>
            </p>
          </div>
        </>
      )}
    </section>
  );
};
