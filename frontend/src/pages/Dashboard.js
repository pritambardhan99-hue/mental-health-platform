import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { moodAPI } from '../services/api';

const MOOD_EMOJIS = {
  happy: '😊', calm: '😌', anxious: '😰', sad: '😢',
  angry: '😠', hopeful: '🌟', numb: '😶', overwhelmed: '😩',
};

const QUICK_ACTIONS = [
  { icon: '💬', label: 'Talk to AI', sub: 'Chat with Serene', to: '/app/chat', color: 'var(--accent-teal)' },
  { icon: '📊', label: 'Log Mood', sub: "How are you today?", to: '/app/mood', color: 'var(--accent-violet)' },
  { icon: '🆘', label: 'Get Help', sub: 'Crisis resources', to: '/app/emergency', color: 'var(--accent-rose)' },
];

export default function Dashboard() {
  const navigate = useNavigate();
  const [todayMood, setTodayMood]     = useState(null);
  const [weeklyData, setWeeklyData]   = useState(null);
  const [loadingMood, setLoadingMood] = useState(true);

  useEffect(() => {
    Promise.all([
      moodAPI.getToday().catch(() => null),
      moodAPI.getWeeklyStats().catch(() => null),
    ]).then(([today, weekly]) => {
      if (today?.data)  setTodayMood(today.data);
      if (weekly?.data) setWeeklyData(weekly.data);
      setLoadingMood(false);
    });
  }, []);

  const hour  = new Date().getHours();
  const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

  return (
    <div style={{ padding: '40px', maxWidth: 900, margin: '0 auto', width: '100%' }}>

      {/* Header */}
      <div className="animate-fade-in" style={{ marginBottom: 40 }}>
        <h1 style={{ fontFamily: 'DM Serif Display', fontSize: 34, color: 'var(--text-primary)', marginBottom: 6 }}>
          {greeting} 👋
        </h1>
        <p style={{ color: 'var(--text-muted)', fontSize: 15 }}>
          Welcome to your safe space. Take a breath — you're not alone.
        </p>
      </div>

      {/* Today's mood banner */}
      <div className="glass-card animate-fade-in" style={{
        padding: '24px 28px',
        marginBottom: 24,
        background: todayMood
          ? 'linear-gradient(135deg, rgba(45,212,191,0.06), rgba(167,139,250,0.06))'
          : 'var(--bg-card)',
      }}>
        {loadingMood ? (
          <div style={{ color: 'var(--text-muted)', fontSize: 14 }}>Loading today's mood…</div>
        ) : todayMood ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <span style={{ fontSize: 48 }}>{MOOD_EMOJIS[todayMood.mood]}</span>
            <div>
              <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 2 }}>Today you felt</div>
              <div style={{ fontSize: 22, color: 'var(--text-primary)', fontFamily: 'DM Serif Display', textTransform: 'capitalize' }}>
                {todayMood.mood}
              </div>
              {todayMood.note && (
                <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 4, fontStyle: 'italic' }}>
                  "{todayMood.note}"
                </div>
              )}
            </div>
          </div>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div>
              <div style={{ fontSize: 15, color: 'var(--text-primary)', marginBottom: 4 }}>
                How are you feeling today?
              </div>
              <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                Log your mood to track your emotional journey
              </div>
            </div>
            <button className="btn-primary" onClick={() => navigate('/app/mood')} style={{ flexShrink: 0 }}>
              Log Mood →
            </button>
          </div>
        )}
      </div>

      {/* Quick action cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 32 }}>
        {QUICK_ACTIONS.map(({ icon, label, sub, to, color }) => (
          <div
            key={to}
            className="glass-card animate-fade-in"
            onClick={() => navigate(to)}
            style={{
              padding: '24px 20px',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
              textAlign: 'center',
            }}
            onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.borderColor = color; }}
            onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.borderColor = 'var(--border)'; }}
          >
            <div style={{ fontSize: 36, marginBottom: 12 }}>{icon}</div>
            <div style={{ fontSize: 15, fontWeight: 600, color: 'var(--text-primary)', marginBottom: 4 }}>{label}</div>
            <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>{sub}</div>
          </div>
        ))}
      </div>

      {/* Weekly mood summary */}
      {weeklyData && weeklyData.total_entries > 0 && (
        <div className="glass-card animate-fade-in" style={{ padding: '24px 28px' }}>
          <h3 style={{ fontFamily: 'DM Serif Display', fontSize: 20, marginBottom: 20, color: 'var(--text-primary)' }}>
            This Week's Mood
          </h3>
          <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 32, color: 'var(--accent-teal)', fontFamily: 'DM Serif Display', fontWeight: 700 }}>
                {weeklyData.average_score.toFixed(1)}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Avg Score</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 32 }}>{MOOD_EMOJIS[weeklyData.most_common_mood]}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', textTransform: 'capitalize' }}>{weeklyData.most_common_mood}</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 32, color: 'var(--accent-violet)', fontFamily: 'DM Serif Display', fontWeight: 700 }}>
                {weeklyData.total_entries}
              </div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>Days Logged</div>
            </div>
          </div>

          {/* Mini mood bar chart */}
          <div style={{ marginTop: 20, display: 'flex', gap: 6, alignItems: 'flex-end', height: 60 }}>
            {weeklyData.entries.map((entry, i) => (
              <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 4 }}>
                <div style={{
                  width: '100%',
                  height: `${(entry.mood_score / 5) * 50}px`,
                  minHeight: 8,
                  background: `linear-gradient(to top, var(--accent-teal), var(--accent-violet))`,
                  borderRadius: 4,
                  opacity: 0.8,
                }} />
                <div style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                  {MOOD_EMOJIS[entry.mood]}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Affirmation */}
      <div style={{
        marginTop: 24,
        textAlign: 'center',
        padding: '20px',
        color: 'var(--text-muted)',
        fontSize: 14,
        fontStyle: 'italic',
      }}>
        "You don't have to be positive all the time. It's okay to feel sad, angry, annoyed,
        frustrated, scared, or anxious. Having feelings doesn't make you a negative person.
        It makes you human." 💙
      </div>
    </div>
  );
}
