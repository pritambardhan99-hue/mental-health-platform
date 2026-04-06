/**
 * useWebSocket Hook
 * =================
 * Custom React hook that manages a WebSocket connection.
 * 
 * USAGE:
 *   const { messages, sendMessage, isConnected } = useWebSocket(roomId);
 * 
 * FEATURES:
 * - Auto-connects on mount
 * - Auto-reconnects on disconnect (with exponential backoff)
 * - Handles emergency alerts from server
 * - Returns parsed message objects
 */

import { useState, useEffect, useRef, useCallback } from 'react';

const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
const MAX_RETRIES = 5;

export function useWebSocket(roomId) {
  const [messages, setMessages]       = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const [emergency, setEmergency]     = useState(null);
  const wsRef      = useRef(null);
  const retriesRef = useRef(0);
  const timerRef   = useRef(null);

  const connect = useCallback(() => {
    if (!roomId) return;

    const token = localStorage.getItem('access_token');
    if (!token) return;

    // Build WebSocket URL with JWT token as query param
    const url = `${WS_URL}/ws/chat/${roomId}/?token=${token}`;
    const ws  = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      retriesRef.current = 0;  // Reset retry counter on success
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'emergency') {
          // Emergency alert — don't add to messages, show banner
          setEmergency(data);
          return;
        }

        if (data.type === 'system') {
          setMessages(prev => [...prev, { ...data, id: Date.now() }]);
          return;
        }

        if (data.type === 'message') {
          setMessages(prev => [...prev, { ...data, id: data.message_id }]);
        }
      } catch (e) {
        console.error('WebSocket message parse error:', e);
      }
    };

    ws.onclose = (event) => {
      setIsConnected(false);
      wsRef.current = null;

      // Auto-reconnect with exponential backoff (unless intentional close)
      if (event.code !== 1000 && retriesRef.current < MAX_RETRIES) {
        const delay = Math.min(1000 * Math.pow(2, retriesRef.current), 30000);
        retriesRef.current += 1;
        timerRef.current = setTimeout(connect, delay);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };
  }, [roomId]);

  useEffect(() => {
    connect();

    // Cleanup on unmount or roomId change
    return () => {
      clearTimeout(timerRef.current);
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounted');
      }
    };
  }, [connect]);

  const sendMessage = useCallback((text) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ message: text }));
      return true;
    }
    return false;
  }, []);

  const dismissEmergency = useCallback(() => setEmergency(null), []);

  return { messages, sendMessage, isConnected, emergency, dismissEmergency };
}
