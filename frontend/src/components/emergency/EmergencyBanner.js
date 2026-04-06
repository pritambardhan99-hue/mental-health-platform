import React from 'react';

export default function EmergencyBanner({ resources, onDismiss }) {
  return (
    <div className="emergency-banner animate-fade-in" style={{ margin: '0 28px 0' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
        <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
          <span style={{ fontSize: 24 }}>🚨</span>
          <div>
            <div style={{ fontWeight: 600, color: '#fb7185', fontSize: 15 }}>
              We noticed some concerning words
            </div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 2 }}>
              You matter. Help is available right now — you don't have to face this alone.
            </div>
          </div>
        </div>
        <button
          onClick={onDismiss}
          style={{
            background: 'transparent', border: 'none',
            color: 'var(--text-muted)', cursor: 'pointer', fontSize: 18,
            padding: '0 4px', lineHeight: 1,
          }}
        >×</button>
      </div>

      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
        {(resources || []).slice(0, 3).map((r, i) => (
          <a
            key={i}
            href={r.number ? `tel:${r.number.replace(/[-\s]/g, '')}` : r.website}
            target={r.number ? '_self' : '_blank'}
            rel="noopener noreferrer"
            style={{
              background: 'rgba(251,113,133,0.1)',
              border: '1px solid rgba(251,113,133,0.25)',
              borderRadius: 8,
              padding: '6px 12px',
              textDecoration: 'none',
              color: '#fb7185',
              fontSize: 13,
              fontWeight: 500,
            }}
          >
            📞 {r.name}: {r.number || 'Website →'}
          </a>
        ))}
      </div>
    </div>
  );
}
