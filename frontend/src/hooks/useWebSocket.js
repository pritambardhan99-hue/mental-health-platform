/**
 * useWebSocket Hook (HTTP version)
 * =================================
 * Replaced WebSocket with HTTP API calls for Render free plan compatibility.
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { chatbotAPI } from '../services/api';

export function useWebSocket(roomId) {
  const [messages, setMessages]       = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [emergency, setEmergency]     = useState(null);
  const pollingRef = useRef(null);

  useEffect(() => {
    if (!roomId) return;
    setIsConnected(true);

    // Load history once on connect
    chatbotAPI.getHistory(roomId).then(res => {
      if (res?.data?.messages) {
        setMessages(res.data.messages.map(m => ({
          type: 'message',
          message: m.content,
          sender: m.role === 'user' ? 'user' : 'bot',
          id: m.id,
        })));
      }
    }).catch(() => {});

    return () => {
      clearInterval(pollingRef.current);
      setIsConnected(false);
    };
  }, [roomId]);

  const sendMessage = useCallback(async (text) => {
    if (!roomId) return false;

    // Add user message immediately to UI
    const userMsg = {
      type: 'message',
      message: text,
      sender: 'user',
      id: Date.now(),
    };
    setMessages(prev => [...prev, userMsg]);

    try {
      const res = await chatbotAPI.sendMessage(text, roomId, []);
      const botMsg = {
        type: 'message',
        message: res.data.response || res.data.message,
        sender: 'bot',
        id: Date.now() + 1,
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (e) {
      setMessages(prev => [...prev, {
        type: 'message',
        message: 'Sorry, I could not respond right now. Please try again.',
        sender: 'bot',
        id: Date.now() + 1,
      }]);
    }

    return true;
  }, [roomId]);

  const dismissEmergency = useCallback(() => setEmergency(null), []);

  return { messages, sendMessage, isConnected, emergency, dismissEmergency };
}