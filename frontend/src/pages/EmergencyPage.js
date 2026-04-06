import React, { useEffect, useState } from 'react';
import { emergencyAPI } from '../services/api';

const STATIC_RESOURCES = [
  { name: 'iCall (India)', number: '9152987821', desc: 'Professional psychological counseling', available: 'Mon–Sat, 8am–10pm IST', emoji: '📞' },
  { name: 'Vandrevala Foundation', number: '1860-2662-345', desc: 'Free mental health support', available: '24/7', emoji: '🌙' },
  { name: 'NIMHANS Helpline', number: '080-46110007', desc: 'National mental health helpline', available: '24/7', emoji: '🏥' },
  { name: 'Snehi India', number: '+91-44-24640050', desc: 'Emotional support helpline', available: '24/7', emoji: '💛' },
];

const COPING_TIPS = [
  { emoji: '🌬️', title: '4-7-8 Breathing', desc: 'Inhale for 4s, hold for 7s, exhale for 8s. Repeat 4 times. Activates your parasympathetic nervous system.' },
  { emoji: '🖐️', title: '5-4-3-2-1 Grounding', desc: 'Name 5 things you see, 4 you can touch, 3 you hear, 2 you smell, 1 you taste. Anchors you to the present.' },
  { emoji: '🚶', title: 'Mindful Walk', desc: 'Take a 10-minute walk and focus only on your surroundings. Movement helps regulate mood.' },
  { emoji: '📓', title: 'Journal It Out', desc: 'Write "I feel ___ because ___". Naming emotions reduces their intensity by up to 50%.' },
  { emoji: '🧊', title: 'Cold Water Reset', desc: 'Splash cold water on your face or hold ice. It triggers the dive reflex, slowing your heart rate.' },
  { emoji: '📱', title: 'Reach Out', desc: "Text someone you trust, even just 'hey'. Connection is one of the most powerful antidotes to distress." },
];

export default function EmergencyPage() {
  const [, setResources] = useState([]);
  const [checkText, setCheckText] = useState('');
  const [checkResult, setCheckResult] = useState(null);
  const [checking, setChecking] = useState(false);

  useEffect(() => {
    emergencyAPI.getResources().then(res => {
      if (res.data?.resources?.length > 0) setResources(res.data.resources);
    }).catch(() => {});
  }, []);

  const handleCheck = async () => {
    if (!checkText.trim()) return;
    setChecking(true);
    try {
      const res = await emergencyAPI.checkText(checkText, 'mood_note');
      setCheckResult(res.data);
    } catch (e) {
      setCheckResult({ is_emergency: false });
    } finally {
      setChecking(false);
    }
  };

  return (
    <div style={{ padding: '40px', maxWidth: 860, margin: '0 auto', width: '100%' }}>

      {/* Header */}
      <div className="animate-fade-in" style={{ marginBottom: 36 }}>
        <h1 style={{ fontFamily: 'DM Serif Display', fontSize: 32, color: 'var(--text-primary)', marginBottom: 8 }}>
          You Are Not Alone 💙
        </h1>
        <p style={{ color: 'var(--text-muted)', lineHeight: 1.7 }}>
          If you are in crisis or need support right now, please reach out to one of these resources.
          Help is available 24/7 — you deserve support.
        </p>
      </div>

      {/* Emergency banner */}
      <div className="emergency-banner animate-fade-in" style={{ marginBottom: 32 }}>
        <div style={{ display: 'flex', gap: 12, alignItems: 'flex-start' }}>
          <span style={{ fontSize: 32 }}>🚨</span>
          <div>
            <div style={{ fontWeight: 600, color: '#fb7185', fontSize: 16, marginBottom: 4 }}>
              Immediate Danger?
            </div>
            <div style={{ color: 'var(--text-muted)', fontSize: 14, lineHeight: 1.6 }}>
              If you or someone else is in immediate danger, call emergency services (112 in India).
              For mental health crises, call any helpline below — they are free and confidential.
            </div>
          </div>
        </div>
      </div>

      {/* Helpline cards */}
      <div style={{ marginBottom: 36 }}>
        <h2 style={{ fontFamily: 'DM Serif Display', fontSize: 22, color: 'var(--text-primary)', marginBottom: 16 }}>
          Crisis Helplines
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 14 }}>
          {STATIC_RESOURCES.map((r) => (
            <div
              key={r.name}
              className="glass-card animate-fade-in"
              style={{ padding: '20px 22px', display: 'flex', gap: 14, alignItems: 'flex-start' }}
            >
              <span style={{ fontSize: 28, flexShrink: 0 }}>{r.emoji}</span>
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>{r.name}</div>
                <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 8 }}>{r.desc}</div>
                <a
                  href={`tel:${r.number.replace(/[-\s]/g, '')}`}
                  style={{
                    display: 'inline-block',
                    background: 'rgba(251,113,133,0.12)',
                    border: '1px solid rgba(251,113,133,0.3)',
                    borderRadius: 8,
                    padding: '6px 12px',
                    color: '#fb7185',
                    textDecoration: 'none',
                    fontSize: 14,
                    fontWeight: 600,
                    letterSpacing: '0.02em',
                  }}
                >
                  📞 {r.number}
                </a>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 6 }}>{r.available}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Coping strategies */}
      <div style={{ marginBottom: 36 }}>
        <h2 style={{ fontFamily: 'DM Serif Display', fontSize: 22, color: 'var(--text-primary)', marginBottom: 16 }}>
          Immediate Coping Strategies
        </h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 14 }}>
          {COPING_TIPS.map((tip) => (
            <div key={tip.title} className="glass-card animate-fade-in" style={{ padding: '18px 20px' }}>
              <div style={{ fontSize: 28, marginBottom: 10 }}>{tip.emoji}</div>
              <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: 6, fontSize: 14 }}>{tip.title}</div>
              <div style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6 }}>{tip.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Text checker tool */}
      <div className="glass-card animate-fade-in" style={{ padding: '28px' }}>
        <h3 style={{ fontFamily: 'DM Serif Display', fontSize: 20, color: 'var(--text-primary)', marginBottom: 8 }}>
          Check-In Tool
        </h3>
        <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 16, lineHeight: 1.6 }}>
          Not sure if what you're feeling warrants reaching out? Describe how you feel and we'll let you know if crisis support might help.
        </p>
        <textarea
          className="input-field"
          placeholder="Type how you're feeling right now…"
          value={checkText}
          onChange={e => { setCheckText(e.target.value); setCheckResult(null); }}
          rows={3}
          style={{ resize: 'none', marginBottom: 12 }}
        />
        <button
          className="btn-primary"
          onClick={handleCheck}
          disabled={!checkText.trim() || checking}
        >
          {checking ? 'Checking…' : 'Check In'}
        </button>

        {checkResult && (
          <div className="animate-fade-in" style={{
            marginTop: 16,
            padding: '14px 18px',
            borderRadius: 12,
            background: checkResult.is_emergency
              ? 'rgba(251,113,133,0.08)' : 'rgba(45,212,191,0.08)',
            border: `1px solid ${checkResult.is_emergency ? 'rgba(251,113,133,0.3)' : 'rgba(45,212,191,0.3)'}`,
          }}>
            {checkResult.is_emergency ? (
              <div>
                <div style={{ color: '#fb7185', fontWeight: 600, marginBottom: 6 }}>
                  🚨 We noticed some concerning words.
                </div>
                <p style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 8 }}>
                  What you're feeling sounds really difficult. Please consider reaching out to one of the helplines above.
                  You matter, and support is available right now.
                </p>
                <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                  Detected: {checkResult.keywords_found?.join(', ')}
                </div>
              </div>
            ) : (
              <div>
                <div style={{ color: 'var(--accent-teal)', fontWeight: 600, marginBottom: 4 }}>
                  💙 Thank you for checking in.
                </div>
                <p style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                  We didn't detect immediate crisis words, but your feelings are always valid.
                  Feel free to chat with Serene or try a coping strategy above.
                </p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Affirmation footer */}
      <div style={{ textAlign: 'center', marginTop: 32, padding: '20px', color: 'var(--text-muted)', fontSize: 14 }}>
        💙 Seeking help is a sign of strength, not weakness. Every step forward counts.
      </div>
    </div>
  );
}
