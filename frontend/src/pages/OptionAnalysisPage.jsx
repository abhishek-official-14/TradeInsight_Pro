import { useEffect, useMemo, useState } from 'react';
import { optionsApi } from '../api/optionsApi';
import styles from './OptionAnalysisPage.module.css';

export const OptionAnalysisPage = () => {
  const [contracts, setContracts] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError('');

      try {
        const [latestResponse, analyticsResponse] = await Promise.all([
          optionsApi.getLatest({ limit: 30 }),
          optionsApi.getAnalytics({ symbol: 'NIFTY' }),
        ]);

        setContracts(latestResponse || []);
        setAnalytics(analyticsResponse || null);
      } catch (err) {
        setError(err?.message || 'Unable to load option analysis data.');
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  const rows = useMemo(
    () =>
      contracts.map((contract) => ({
        symbol: contract.symbol,
        strike: contract.strike_price,
        action: contract.option_type,
        premium: contract.premium,
      })),
    [contracts]
  );

  return (
    <section className="panel">
      <h2>Option Analysis</h2>
      {loading && <p className="metric-hint">Loading options data…</p>}
      {error && <p className="error-text">{error}</p>}

      {!loading && !error && (
        <>
          <div className={styles.summary}>
            <p>
              Put/Call Ratio: <strong>{analytics?.pcr ?? '—'}</strong>
            </p>
            <p>
              Strongest Support: <strong>{analytics?.strongest_support ?? '—'}</strong> · Strongest Resistance:{' '}
              <strong>{analytics?.strongest_resistance ?? '—'}</strong>
            </p>
          </div>

          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Symbol</th>
                  <th>Strike</th>
                  <th>Type</th>
                  <th>Premium</th>
                </tr>
              </thead>
              <tbody>
                {rows.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="metric-hint">
                      No option contracts available.
                    </td>
                  </tr>
                ) : (
                  rows.map((signal, idx) => (
                    <tr key={`${signal.symbol}-${idx}`}>
                      <td>{signal.symbol}</td>
                      <td>{signal.strike}</td>
                      <td>{signal.action}</td>
                      <td>{signal.premium}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </section>
  );
};
