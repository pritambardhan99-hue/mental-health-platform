/**
 * API Service Layer
 * =================
 * Centralizes all HTTP calls to the Django backend.
 * 
 * WHY AXIOS INSTEAD OF FETCH?
 * - Automatic JSON parsing
 * - Request/response interceptors (for JWT injection)
 * - Better error handling
 * - Request cancellation
 * 
 * INTERCEPTORS:
 * - Request interceptor: Automatically adds JWT token to every request
 * - Response interceptor: Handles 401 errors (token expired → refresh)
 */

import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15000,  // 15 second timeout
});

// ─────────────────────────────────────────────────────────────────
// REQUEST INTERCEPTOR
// Automatically attaches JWT access token to every API request
// ─────────────────────────────────────────────────────────────────
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ─────────────────────────────────────────────────────────────────
// RESPONSE INTERCEPTOR
// Handles token expiration: tries to refresh, then logs out on failure
// ─────────────────────────────────────────────────────────────────
api.interceptors.response.use(
  (response) => response,  // Pass through successful responses
  async (error) => {
    const originalRequest = error.config;

    // If 401 Unauthorized and we haven't already tried to refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) throw new Error('No refresh token');

        const res = await axios.post(`${API_URL}/api/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const newAccessToken = res.data.access_token;
        localStorage.setItem('access_token', newAccessToken);

        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed — clear storage and redirect to home
        localStorage.clear();
        window.location.href = '/';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// ─────────────────────────────────────────────────────────────────
// AUTH API
// ─────────────────────────────────────────────────────────────────
export const authAPI = {
  /** Create a new anonymous session */
  register: () => api.post('/api/auth/register/'),

  /** Login with UUID from previous session */
  login: (userId) => api.post('/api/auth/login/', { user_id: userId }),

  /** Get current user info */
  me: () => api.get('/api/auth/me/'),
};

// ─────────────────────────────────────────────────────────────────
// CHAT API
// ─────────────────────────────────────────────────────────────────
export const chatAPI = {
  /** Get or create default "My Safe Space" room */
  getDefaultRoom: () => api.post('/api/chat/rooms/default/'),

  /** List all chat rooms for current user */
  listRooms: () => api.get('/api/chat/rooms/'),

  /** Get room details and messages */
  getRoomMessages: (roomId) => api.get(`/api/chat/rooms/${roomId}/`),
};

// ─────────────────────────────────────────────────────────────────
// CHATBOT API
// ─────────────────────────────────────────────────────────────────
export const chatbotAPI = {
  /**
   * Send message to AI chatbot
   * @param {string} message - User's message
   * @param {string} roomId - Chat room UUID
   * @param {Array} history - Recent conversation history for context
   */
  sendMessage: (message, roomId, history = []) =>
    api.post('/api/chatbot/message/', {
      message,
      room_id: roomId,
      conversation_history: history,
    }),

  /** Get full conversation history */
  getHistory: (roomId) =>
    api.get('/api/chatbot/history/', { params: { room_id: roomId } }),
};

// ─────────────────────────────────────────────────────────────────
// MOOD API
// ─────────────────────────────────────────────────────────────────
export const moodAPI = {
  /** Submit or update today's mood */
  logMood: (mood, note = '') => api.post('/api/mood/log/', { mood, note }),

  /** Get today's mood entry */
  getToday: () => api.get('/api/mood/today/'),

  /** Get mood history for past N days */
  getHistory: (days = 30) => api.get('/api/mood/history/', { params: { days } }),

  /** Get weekly stats for chart */
  getWeeklyStats: () => api.get('/api/mood/stats/weekly/'),

  /** Get monthly stats for chart */
  getMonthlyStats: () => api.get('/api/mood/stats/monthly/'),
};

// ─────────────────────────────────────────────────────────────────
// EMERGENCY API
// ─────────────────────────────────────────────────────────────────
export const emergencyAPI = {
  /** Check text for emergency keywords */
  checkText: (text, source = 'chat') =>
    api.post('/api/emergency/check/', { text, source }),

  /** Get helpline resources */
  getResources: () => api.get('/api/emergency/resources/'),
};

export default api;
