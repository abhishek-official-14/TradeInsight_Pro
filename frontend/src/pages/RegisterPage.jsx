import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const RegisterPage = () => {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: '', email: '', password: '' });
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setError('');

    try {
      await register(form);
      setMessage('Registration successful. You can now login.');
      setTimeout(() => navigate('/login'), 1000);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="auth-card">
      <h1>Create account</h1>
      <p>Join TradeInsight Pro and unlock AI-driven option signals.</p>
      <form onSubmit={handleSubmit}>
        <input type="text" placeholder="Full name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        <input type="email" placeholder="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
        <input type="password" placeholder="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
        {error && <span className="error-text">{error}</span>}
        {message && <span className="success-text">{message}</span>}
        <button type="submit" disabled={busy}>{busy ? 'Creating...' : 'Register'}</button>
      </form>
      <small>
        Already registered? <Link to="/login">Login</Link>
      </small>
    </section>
  );
};
