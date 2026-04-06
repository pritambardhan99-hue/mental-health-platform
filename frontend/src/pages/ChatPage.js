/**
 * Chat Page
 * =========
 * Combines:
 * 1. REST API to load history (chatbotAPI.getHistory)
 * 2. REST API to send messages (chatbotAPI.sendMessage) — AI replies via HTTP
 * 3. WebSocket for real-time delivery (useWebSocket hook)
 * 
 * Design: WhatsApp-style chat bubbles, typing indicator, emergency banner
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { chatbotAPI, chatAPI } from '../services/api';
import EmergencyBanner from '../components/emergency/EmergencyBanner';

const WELCOME_MSG = {
  id: 'welcome',
  role: 'assistant',
  content: "Hello 💙 I'm Serene, your mental wellness companion. This is a safe, judgment-free space. How are you feeling today?",
  sender_type: 'ai',
  timestamp: new Date().toISOString(),
};

function TypingIndicator() {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '8px 0' }}>
      <div style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border)',
        borderRadius: '18px 18px 18px 4px',
        padding: '12px 16px',
        display: 'flex',
        gap: 4,
        alignItems: 'center',
      }}>
        {[0, 150, 300].map(delay => (
          <div key={delay} style={{
            width: 7, height: 7,
            borderRadius: '50%',
            background: 'var(--text-muted)',
            animation: 'pulse-soft 1.4s ease-in-out infinite',
            animationDelay: `${delay}ms`,
          }} />
        ))}
      </div>
    </div>
  );
}

function ChatBubble({ msg }) {
  const isUser   = msg.role === 'user' || msg.sender_type === 'user';
  const isSystem = msg.sender_type === 'system' || msg.type === 'system';

  if (isSystem) {
    return (
      <div className="bubble-system animate-fade-in" style={{ margin: '8px 40px', padding: '8px 16px' }}>
        <span style={{ fontSize: 13, color: 'var(--text-muted)' }}>{msg.content || msg.message}</span>
      </div>
    );
  }

  return (
    <div className="animate-fade-in" style={{
      display: 'flex',
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      marginBottom: 12,
    }}>
      {!isUser && (
        <div style={{
          width: 32, height: 32, borderRadius: '50%',
          background: 'linear-gradient(135deg, var(--accent-teal), var(--accent-violet))',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 14, flexShrink: 0, marginRight: 8, alignSelf: 'flex-end',
        }}>💙</div>
      )}
      <div style={{ maxWidth: '70%' }}>
        <div className={isUser ? 'bubble-user' : 'bubble-ai'} style={{
          padding: '12px 16px',
          fontSize: 14,
          lineHeight: 1.6,
          color: 'var(--text-primary)',
          whiteSpace: 'pre-wrap',
        }}>
          {msg.content || msg.message}
        </div>
        <div style={{
          fontSize: 11,
          color: 'var(--text-muted)',
          marginTop: 4,
          textAlign: isUser ? 'right' : 'left',
          paddingLeft: isUser ? 0 : 4,
          paddingRight: isUser ? 4 : 0,
        }}>
          {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
    </div>
  );
}

export default function ChatPage() {
  const [messages, setMessages]     = useState([WELCOME_MSG]);
  const [input, setInput]           = useState('');
  const [loading, setLoading]       = useState(false);
  const [roomId, setRoomId]         = useState(null);
  const [emergency, setEmergency]   = useState(null);
  const [histLoaded, setHistLoaded] = useState(false);
  const bottomRef = useRef(null);
  const inputRef  = useRef(null);

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  // Load room and conversation history
  useEffect(() => {
    async function init() {
      try {
        const roomRes = await chatAPI.getDefaultRoom();
        const rid = roomRes.data.id;
        setRoomId(rid);

        const histRes = await chatbotAPI.getHistory(rid);
        if (histRes.data.messages?.length > 0) {
          setMessages(histRes.data.messages);
        }
        setHistLoaded(true);
      } catch (e) {
        setHistLoaded(true);  // Still show welcome msg on error
      }
    }
    init();
  }, []);

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || loading) return;

    setInput('');
    setLoading(true);

    // Optimistically add user message
    const userMsg = {
      id: `u-${Date.now()}`,
      role: 'user',
      sender_type: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMsg]);

    // Build history for context (last 10 messages)
    const history = messages.slice(-10).map(m => ({
      role: m.role || (m.sender_type === 'ai' ? 'assistant' : 'user'),
      content: m.content || m.message,
    }));

    try {
      const res = await chatbotAPI.sendMessage(text, roomId, history);
      const data = res.data;

      // Add AI response
      const aiMsg = {
        id: data.ai_message_id,
        role: 'assistant',
        sender_type: 'ai',
        content: data.response,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, aiMsg]);

      // Show emergency banner if triggered
      if (data.is_emergency) {
        setEmergency(data.emergency_resources);
      }
    } catch (e) {
      setMessages(prev => [...prev, {
        id: `err-${Date.now()}`,
        role: 'assistant',
        sender_type: 'ai',
        content: "I'm having trouble connecting right now. If you need immediate help, please call iCall: 9152987821.",
        timestamp: new Date().toISOString(),
      }]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }, [input, loading, roomId, messages]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>

      {/* Header */}
      <div style={{
        padding: '20px 28px',
        borderBottom: '1px solid var(--border)',
        background: 'var(--bg-secondary)',
        display: 'flex',
        alignItems: 'center',
        gap: 14,
      }}>
        <div style={{
          width: 40, height: 40, borderRadius: '50%',
          background: 'linear-gradient(135deg, var(--accent-teal), var(--accent-violet))',
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18,
        }}>💙</div>
        <div>
          <div style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Serene</div>
          <div style={{ fontSize: 12, color: 'var(--accent-teal)' }}>● Online · AI Mental Wellness Companion</div>
        </div>
      </div>

      {/* Emergency banner */}
      {emergency && (
        <EmergencyBanner
          resources={emergency}
          onDismiss={() => setEmergency(null)}
        />
      )}

      {/* Messages area */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '24px 28px',
        display: 'flex',
        flexDirection: 'column',
      }}>
        {messages.map(msg => <ChatBubble key={msg.id} msg={msg} />)}
        {loading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>

      {/* Disclaimer */}
      <div style={{
        padding: '6px 28px',
        fontSize: 11,
        color: 'var(--text-muted)',
        textAlign: 'center',
        background: 'var(--bg-secondary)',
        borderTop: '1px solid var(--border)',
      }}>
        Serene is an AI companion, not a therapist. In crisis? Call iCall: 9152987821
      </div>

      {/* Input area */}
      <div style={{
        padding: '16px 28px',
        borderTop: '1px solid var(--border)',
        background: 'var(--bg-secondary)',
        display: 'flex',
        gap: 12,
        alignItems: 'flex-end',
      }}>
        <textarea
          ref={inputRef}
          className="input-field"
          placeholder="Share what's on your mind… (Shift+Enter for new line)"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          rows={2}
          style={{ resize: 'none', flex: 1 }}
        />
        <button
          className="btn-primary"
          onClick={sendMessage}
          disabled={!input.trim() || loading}
          style={{ padding: '12px 20px', flexShrink: 0, alignSelf: 'flex-end' }}
        >
          {loading ? '…' : 'Send →'}
        </button>
      </div>
    </div>
  );
}
