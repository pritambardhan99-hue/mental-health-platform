/**
 * Mood Tracker Page
 * =================
 * Features:
 * 1. Emoji mood selector (8 moods)
 * 2. Optional text note
 * 3. Recharts line chart of past 30 days
 * 4. Mood distribution donut-style stats
 */

import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, XAxis, YAxis, Tooltip,
  ResponsiveContainer, CartesianGrid, Area, AreaChart,
} from 'recharts';
import { moodAPI } from '../services/api';

const MOODS = [
  { key: 'happy',       emoji: '😊', label: 'Happy',       color: '#2dd4bf' },
  { key: 'calm',        emoji: '😌', label: 'Calm',        color: '#a78bfa' },
  { key: 'hopeful',     emoji: '🌟', label: 'Hopeful',     color: '#fbbf24' },
  { key: 'numb',        emoji: '😶', label: 'Numb',        color: '#8b949e' },
  { key: 'anxious',     emoji: '😰', label: 'Anxious',     color: '#fb923c' },
  { key: 'sad',         emoji: '😢', label: 'Sad',         color: '#60a5fa' },
  { key: 'angry',       emoji: '😠', label: 'Angry',       color: '#f87171' },
  { key: 'overwhelmed', emoji: '😩', label: 'Overwhelmed', color: '#c084fc' },
];

const MOOD_SCORES = { happy: 5, hopeful: 4, calm: 4, numb: 3, anxious: 2, angry: 2, sad: 1, overwhelmed: 1 };

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  const entry = payload[0].payload;
  const mood  = MOODS.find(m => m.key === entry.mood);
  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border)',
      borderRadius: 10,
      padding: '10px 14px',
      fontSize: 13,
    }}>
      <div style={{ color: 'var(--text-muted)', marginBottom: 4 }}>{label}</div>
      <div style={{ fontSize: 20 }}>{mood?.emoji}</div>
      <div style={{ color: 'var(--text-primary)', textTransform: 'capitalize' }}>{entry.mood}</div>
      {entry.note && <div style={{ color: 'var(--text-muted)', fontStyle: 'italic', marginTop: 4, maxWidth: 180 }}>"{entry.note}"</div>}
    </div>
  );
}

export default function MoodPage() {
  const [selectedMood, setSelectedMood] = useState('');
  const [note, setNote]                 = useState('');
  const [submitting, setSubmitting]     = useState(false);
  const [submitted, setSubmitted]       = useState(false);
  const [todayMood, setTodayMood]       = useState(null);
  const [chartData, setChartData]       = useState([]);
  const [stats, setStats]               = useState(null);
  const [period, setPeriod]             = useState('weekly');

  useEffect(() => {
    loadData();
  }, [period]);

  const loadData = async () => {
    try {
      const [todayRes, statsRes] = await Promise.all([
        moodAPI.getToday().catch(() => null),
        period === 'weekly'
          ? moodAPI.getWeeklyStats()
          : moodAPI.getMonthlyStats(),
      ]);

      if (todayRes?.data) {
        setTodayMood(todayRes.data);
        setSelectedMood(todayRes.data.mood);
        setNote(todayRes.data.note || '');
      }

      if (statsRes?.data) {
        setStats(statsRes.data);
        setChartData(statsRes.data.entries.map(e => ({
          date: new Date(e.date).toLocaleDateString('en', { month: 'short', day: 'numeric' }),
          score: e.mood_score,
          mood: e.mood,
          note: e.note,
        })));
      }
    } catch (e) {
      console.error('Failed to load mood data:', e);
    }
  };

  const handleSubmit = async () => {
    if (!selectedMood) return;
    setSubmitting(true);
    try {
      const res = await moodAPI.logMood(selectedMood, note);
      setTodayMood(res.data.data);
      setSubmitted(true);
      setTimeout(() => setSubmitted(false), 3000);
      await loadData();
    } catch (e) {
      alert('Failed to save mood. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div style={{ padding: '40px', maxWidth: 900, margin: '0 auto', width: '100%' }}>

      {/* Header */}
      <div className="animate-fade-in" style={{ marginBottom: 36 }}>
        <h1 style={{ fontFamily: 'DM Serif Display', fontSize: 32, color: 'var(--text-primary)', marginBottom: 6 }}>
          Mood Tracker 📊
        </h1>
        <p style={{ color: 'var(--text-muted)' }}>
          Track your emotional journey — one day at a time.
        </p>
      </div>

      {/* Mood selector card */}
      <div className="glass-card animate-fade-in" style={{ padding: '28px', marginBottom: 24 }}>
        <h3 style={{ fontFamily: 'DM Serif Display', fontSize: 20, marginBottom: 6, color: 'var(--text-primary)' }}>
          How are you feeling today?
        </h3>
        {todayMood && (
          <p style={{ fontSize: 12, color: 'var(--accent-teal)', marginBottom: 16 }}>
            ✓ You already logged today — you can update it below
          </p>
        )}

        {/* Emoji grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10, marginBottom: 20 }}>
          {MOODS.map(({ key, emoji, label, color }) => (
            <button
              key={key}
              className={`mood-btn ${selectedMood === key ? 'active' : ''}`}
              onClick={() => setSelectedMood(key)}
              style={{ borderColor: selectedMood === key ? color : 'transparent' }}
            >
              <div style={{ fontSize: 32, marginBottom: 6 }}>{emoji}</div>
              <div style={{ fontSize: 12, color: selectedMood === key ? color : 'var(--text-muted)' }}>
                {label}
              </div>
            </button>
          ))}
        </div>

        {/* Note input */}
        <textarea
          className="input-field"
          placeholder="Add a note (optional) — what's making you feel this way?"
          value={note}
          onChange={e => setNote(e.target.value)}
          rows={2}
          style={{ resize: 'none', marginBottom: 16 }}
          maxLength={500}
        />

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <button
            className="btn-primary"
            onClick={handleSubmit}
            disabled={!selectedMood || submitting}
            style={{ minWidth: 140 }}
          >
            {submitting ? 'Saving…' : todayMood ? 'Update Mood' : 'Log Mood'}
          </button>
          {submitted && (
            <span className="animate-fade-in" style={{ color: 'var(--accent-teal)', fontSize: 14 }}>
              ✓ Mood saved!
            </span>
          )}
        </div>
      </div>

      {/* Chart section */}
      {chartData.length > 0 && (
        <div className="glass-card animate-fade-in" style={{ padding: '28px', marginBottom: 24 }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
            <h3 style={{ fontFamily: 'DM Serif Display', fontSize: 20, color: 'var(--text-primary)' }}>
              Mood Over Time
            </h3>
            <div style={{ display: 'flex', gap: 8 }}>
              {['weekly', 'monthly'].map(p => (
                <button
                  key={p}
                  onClick={() => setPeriod(p)}
                  style={{
                    background: period === p ? 'rgba(45,212,191,0.15)' : 'var(--bg-card)',
                    border: `1px solid ${period === p ? 'var(--accent-teal)' : 'var(--border)'}`,
                    color: period === p ? 'var(--accent-teal)' : 'var(--text-muted)',
                    borderRadius: 8,
                    padding: '6px 14px',
                    cursor: 'pointer',
                    fontSize: 13,
                    textTransform: 'capitalize',
                  }}
                >
                  {p}
                </button>
              ))}
            </div>
          </div>

          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={chartData} margin={{ top: 5, right: 5, bottom: 5, left: -20 }}>
              <defs>
                <linearGradient id="moodGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="#2dd4bf" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#2dd4bf" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
              <XAxis
                dataKey="date"
                tick={{ fill: '#8b949e', fontSize: 11 }}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                domain={[1, 5]}
                ticks={[1, 2, 3, 4, 5]}
                tick={{ fill: '#8b949e', fontSize: 11 }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="score"
                stroke="#2dd4bf"
                strokeWidth={2.5}
                fill="url(#moodGrad)"
                dot={{ fill: '#2dd4bf', strokeWidth: 0, r: 4 }}
                activeDot={{ r: 6, fill: '#2dd4bf' }}
              />
            </AreaChart>
          </ResponsiveContainer>

          {/* Y-axis legend */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: 20, marginTop: 12 }}>
            {[{s:1,l:'Low'},{s:3,l:'Mid'},{s:5,l:'High'}].map(({s,l}) => (
              <span key={s} style={{ fontSize: 11, color: 'var(--text-muted)' }}>
                {s} = {l}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Stats summary */}
      {stats && stats.total_entries > 0 && (
        <div className="glass-card animate-fade-in" style={{ padding: '28px' }}>
          <h3 style={{ fontFamily: 'DM Serif Display', fontSize: 20, color: 'var(--text-primary)', marginBottom: 20 }}>
            {period === 'weekly' ? 'This Week' : 'This Month'}'s Summary
          </h3>
          <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', marginBottom: 20 }}>
            <StatCard label="Days Logged"   value={stats.total_entries} color="var(--accent-teal)" />
            <StatCard label="Average Score" value={`${stats.average_score}/5`} color="var(--accent-violet)" />
            <StatCard label="Top Mood"      value={stats.most_common_mood} color="var(--accent-amber)" capitalize />
          </div>

          {/* Mood distribution */}
          <div>
            <div style={{ fontSize: 13, color: 'var(--text-muted)', marginBottom: 10 }}>Mood Breakdown</div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {Object.entries(stats.mood_distribution).sort((a, b) => b[1] - a[1]).map(([mood, count]) => {
                const m    = MOODS.find(m => m.key === mood);
                const pct  = Math.round((count / stats.total_entries) * 100);
                return (
                  <div key={mood} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{ fontSize: 18, width: 24 }}>{m?.emoji}</span>
                    <span style={{ fontSize: 13, color: 'var(--text-muted)', width: 90, textTransform: 'capitalize' }}>{mood}</span>
                    <div style={{ flex: 1, height: 8, background: 'var(--bg-hover)', borderRadius: 4, overflow: 'hidden' }}>
                      <div style={{
                        height: '100%',
                        width: `${pct}%`,
                        background: m?.color || 'var(--accent-teal)',
                        borderRadius: 4,
                        transition: 'width 0.8s ease',
                      }} />
                    </div>
                    <span style={{ fontSize: 12, color: 'var(--text-muted)', width: 40, textAlign: 'right' }}>
                      {count}d ({pct}%)
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ label, value, color, capitalize }) {
  return (
    <div style={{ textAlign: 'center', minWidth: 100 }}>
      <div style={{
        fontSize: 28,
        fontFamily: 'DM Serif Display',
        color,
        textTransform: capitalize ? 'capitalize' : 'none',
        lineHeight: 1.2,
      }}>
        {value}
      </div>
      <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>{label}</div>
    </div>
  );
}
