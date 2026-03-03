import { useEffect, useState } from 'react';
import { userApi } from '../api/userApi';

export const TelegramSettingsPage = () => {
  const [telegramId, setTelegramId] = useState('');
  const [currentTelegramId, setCurrentTelegramId] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    const loadUser = async () => {
      setLoading(true);
      setError('');
      try {
        const user = await userApi.getMe();
        setCurrentTelegramId(user.telegram_id || '');
        setTelegramId(user.telegram_id || '');
      } catch (err) {
        setError(err?.message || 'Unable to load Telegram settings.');
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setError('');
    setSuccess('');

    try {
      const updated = await userApi.linkTelegram({ telegram_id: telegramId.trim() });
      const nextId = updated.telegram_id || '';
      setCurrentTelegramId(nextId);
      setTelegramId(nextId);
      setSuccess('Telegram settings updated successfully.');
    } catch (err) {
      setError(err?.message || 'Unable to update Telegram settings.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="panel" style={{ maxWidth: 680 }}>
      <div className="panel-head">
        <h2>Telegram Settings</h2>
        <span className="metric-hint">Alert delivery</span>
      </div>

      {loading && <p className="metric-hint">Loading Telegram settings…</p>}
      {error && <p className="error-text">{error}</p>}
      {success && <p className="success-text">{success}</p>}

      {!loading && (
        <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '0.8rem', marginTop: '1rem' }}>
          <label htmlFor="telegram-id" className="metric-hint">Telegram Chat ID</label>
          <input
            id="telegram-id"
            type="text"
            placeholder="e.g. 123456789"
            value={telegramId}
            onChange={(event) => setTelegramId(event.target.value)}
            required
            style={{ background: '#0f1a2d', color: 'var(--text)', borderColor: '#1b355f' }}
          />
          <small className="metric-hint">
            Current linked ID: <strong>{currentTelegramId || 'Not linked'}</strong>
          </small>
          <button type="submit" disabled={submitting}>
            {submitting ? 'Saving…' : 'Save Telegram ID'}
          </button>
        </form>
      )}
    </section>
  );
};
