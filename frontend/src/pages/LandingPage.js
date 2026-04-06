/**
 * Landing Page
 * ============
 * The first page users see. Design goals:
 * - Warm, non-clinical aesthetic
 * - Make anonymous login feel safe and easy
 * - Clear CTA: "Start Anonymous Session" OR "Return with ID"
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function LandingPage() {
  const { register, login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [showReturn, setShowReturn] = useState(false);
  const [returnId, setReturnId]     = useState('');
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState('');

  // Already logged in → go to app
  React.useEffect(() => {
    if (isAuthenticated) navigate('/app/dashboard');
  }, [isAuthenticated, navigate]);

  const handleNewSession = async () => {
    setLoading(true);
    setError('');
    try {
      await register();
      navigate('/app/dashboard');
    } catch (e) {
      setError('Could not create session. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleReturn = async (e) => {
    e.preventDefault();
    if (!returnId.trim()) return;
    setLoading(true);
    setError('');
    try {
      await login(returnId.trim());
      navigate('/app/dashboard');
    } catch (e) {
      setError('ID not found. Check your saved UUID and try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'var(--bg-primary)',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '40px 24px',
      position: 'relative',
      overflow: 'hidden',
    }}>

      {/* Background glow orbs */}
      <div style={{
        position: 'absolute', top: '10%', left: '15%',
        width: 400, height: 400, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(45,212,191,0.06) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />
      <div style={{
        position: 'absolute', bottom: '15%', right: '10%',
        width: 300, height: 300, borderRadius: '50%',
        background: 'radial-gradient(circle, rgba(167,139,250,0.06) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />

      {/* Main card */}
      <div className="glass-card animate-fade-in" style={{
        maxWidth: 480,
        width: '100%',
        padding: '48px 40px',
        textAlign: 'center',
      }}>

        {/* Logo & tagline */}
        <div style={{ marginBottom: 40 }}>
          <div style={{ fontSize: 52, marginBottom: 16 }}>💙</div>
          <h1 style={{
            fontSize: 42,
            fontFamily: 'DM Serif Display',
            color: 'var(--text-primary)',
            lineHeight: 1.1,
            marginBottom: 12,
          }}>
            Serene
          </h1>
          <p style={{
            fontSize: 16,
            color: 'var(--text-muted)',
            lineHeight: 1.6,
            maxWidth: 340,
            margin: '0 auto',
          }}>
            A safe, anonymous space to talk, track your mood,
            and find support. <em>No account required.</em>
          </p>
        </div>

        {/* Feature pills */}
        <div style={{ display: 'flex', gap: 8, justifyContent: 'center', flexWrap: 'wrap', marginBottom: 36 }}>
          {['🔒 Anonymous', '🤖 AI Support', '📊 Mood Tracker', '🆘 Crisis Help'].map(f => (
            <span key={f} style={{
              background: 'var(--bg-hover)',
              border: '1px solid var(--border)',
              borderRadius: 20,
              padding: '4px 12px',
              fontSize: 12,
              color: 'var(--text-muted)',
            }}>{f}</span>
          ))}
        </div>

        {/* Error message */}
        {error && (
          <div style={{
            background: 'rgba(251,113,133,0.1)',
            border: '1px solid rgba(251,113,133,0.3)',
            borderRadius: 10,
            padding: '10px 14px',
            marginBottom: 16,
            color: '#fb7185',
            fontSize: 13,
          }}>
            {error}
          </div>
        )}

        {!showReturn ? (
          <>
            {/* Primary CTA */}
            <button
              className="btn-primary"
              style={{ width: '100%', marginBottom: 12, fontSize: 15 }}
              onClick={handleNewSession}
              disabled={loading}
            >
              {loading ? 'Creating your space…' : '✨ Start Anonymous Session'}
            </button>

            {/* Return option */}
            <button
              onClick={() => setShowReturn(true)}
              style={{
                background: 'transparent',
                border: '1px solid var(--border)',
                borderRadius: 12,
                color: 'var(--text-muted)',
                padding: '11px 24px',
                cursor: 'pointer',
                fontSize: 14,
                width: '100%',
                transition: 'all 0.15s',
              }}
              onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--accent-violet)'}
              onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
            >
              Return with my ID →
            </button>
          </>
        ) : (
          /* Return form */
          <form onSubmit={handleReturn}>
            <div style={{ marginBottom: 12, textAlign: 'left' }}>
              <label style={{ fontSize: 13, color: 'var(--text-muted)', display: 'block', marginBottom: 6 }}>
                Your Anonymous ID (UUID)
              </label>
              <input
                className="input-field"
                type="text"
                placeholder="550e8400-e29b-41d4-a716-446655440000"
                value={returnId}
                onChange={e => setReturnId(e.target.value)}
                style={{ fontFamily: 'monospace', fontSize: 13 }}
              />
            </div>
            <button
              type="submit"
              className="btn-primary"
              style={{ width: '100%', marginBottom: 10 }}
              disabled={loading || !returnId.trim()}
            >
              {loading ? 'Signing in…' : 'Return to my space →'}
            </button>
            <button
              type="button"
              onClick={() => { setShowReturn(false); setError(''); }}
              style={{
                background: 'transparent', border: 'none',
                color: 'var(--text-muted)', cursor: 'pointer', fontSize: 13,
              }}
            >
              ← Back
            </button>
          </form>
        )}

        {/* Privacy note */}
        <p style={{ marginTop: 28, fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.7 }}>
          🔒 No email, no name, no tracking. Your UUID is your only identity.
          <br />Save it to return to your history.
        </p>
      </div>

      {/* Crisis footer */}
      <div style={{ marginTop: 24, textAlign: 'center' }}>
        <p style={{ fontSize: 12, color: 'var(--text-muted)' }}>
          In immediate danger? Call{' '}
          <a href="tel:9152987821" style={{ color: 'var(--accent-rose)', textDecoration: 'none' }}>
            iCall: 9152987821
          </a>
          {' '}· Vandrevala:{' '}
          <a href="tel:18602662345" style={{ color: 'var(--accent-rose)', textDecoration: 'none' }}>
            1860-2662-345
          </a>
        </p>
      </div>
    </div>
  );
}
