import React, { useState } from 'react';
import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const NAV_ITEMS = [
  { to: '/app/dashboard', icon: '🏠', label: 'Dashboard' },
  { to: '/app/chat',      icon: '💬', label: 'Chat' },
  { to: '/app/mood',      icon: '📊', label: 'Mood Tracker' },
  { to: '/app/emergency', icon: '🆘', label: 'Get Help' },
];

export default function AppLayout() {
 const { logout } = useAuth();
  const navigate = useNavigate();
  const [showId, setShowId] = useState(false);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const userId = localStorage.getItem('user_id') || '';
  const shortId = userId.slice(0, 8);

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: 'var(--bg-primary)' }}>

      {/* ── Sidebar ─────────────────────────────────────────── */}
      <aside style={{
        width: 240,
        background: 'var(--bg-secondary)',
        borderRight: '1px solid var(--border)',
        display: 'flex',
        flexDirection: 'column',
        padding: '24px 16px',
        flexShrink: 0,
      }}>
        {/* Logo */}
        <div style={{ marginBottom: 40, paddingLeft: 8 }}>
          <div style={{ fontSize: 24, marginBottom: 4 }}>💙</div>
          <h1 style={{ fontSize: 20, fontFamily: 'DM Serif Display', color: 'var(--text-primary)' }}>
            Serene
          </h1>
          <p style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>
            Your safe space
          </p>
        </div>

        {/* Navigation */}
        <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 4 }}>
          {NAV_ITEMS.map(({ to, icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <span style={{ fontSize: 18 }}>{icon}</span>
              <span>{label}</span>
            </NavLink>
          ))}
        </nav>

        {/* User info & logout */}
        <div style={{ borderTop: '1px solid var(--border)', paddingTop: 16, marginTop: 16 }}>
          <div
            style={{
              background: 'var(--bg-card)',
              borderRadius: 10,
              padding: '10px 12px',
              marginBottom: 8,
              cursor: 'pointer',
            }}
            onClick={() => setShowId(!showId)}
          >
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 2 }}>
              Anonymous ID {showId ? '▲' : '▼'}
            </div>
            {showId ? (
              <>
                <div style={{ fontSize: 10, color: 'var(--accent-teal)', wordBreak: 'break-all', fontFamily: 'monospace' }}>
                  {userId}
                </div>
                <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 4 }}>
                  Save this to return to your account
                </div>
              </>
            ) : (
              <div style={{ fontSize: 12, color: 'var(--text-primary)', fontFamily: 'monospace' }}>
                Anon-{shortId}…
              </div>
            )}
          </div>

          <button
            onClick={handleLogout}
            style={{
              width: '100%',
              background: 'transparent',
              border: '1px solid var(--border)',
              borderRadius: 10,
              color: 'var(--text-muted)',
              padding: '8px 12px',
              cursor: 'pointer',
              fontSize: 13,
              transition: 'all 0.15s',
            }}
            onMouseEnter={e => e.target.style.borderColor = 'var(--accent-rose)'}
            onMouseLeave={e => e.target.style.borderColor = 'var(--border)'}
          >
            Sign Out
          </button>
        </div>
      </aside>

      {/* ── Main content ────────────────────────────────────── */}
      <main style={{ flex: 1, overflow: 'auto', display: 'flex', flexDirection: 'column' }}>
        <Outlet />
      </main>
    </div>
  );
}
