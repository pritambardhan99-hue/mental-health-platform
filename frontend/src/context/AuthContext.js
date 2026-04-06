/**
 * Authentication Context
 * ======================
 * React Context provides global state without prop drilling.
 * 
 * Any component can call useAuth() to access:
 *   - user: current user object (or null)
 *   - isAuthenticated: boolean
 *   - login(userId): login with UUID
 *   - register(): create new anonymous session
 *   - logout(): clear session
 *   - loading: true while checking auth status
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { authAPI } from '../services/api';

// Create the context (initially undefined — wrapped by Provider)
const AuthContext = createContext(undefined);

export function AuthProvider({ children }) {
  const [user, setUser]           = useState(null);
  const [loading, setLoading]     = useState(true);  // true = checking auth on page load

  // ── Check if user is already logged in (page reload) ──────────
  useEffect(() => {
    const checkAuth = async () => {
      const token  = localStorage.getItem('access_token');
      const userId = localStorage.getItem('user_id');

      if (token && userId) {
        try {
          const res = await authAPI.me();
          setUser(res.data);
        } catch {
          // Token invalid or expired — clear and start fresh
          localStorage.clear();
        }
      }
      setLoading(false);
    };

    checkAuth();
  }, []);

  // ── Register new anonymous user ────────────────────────────────
  const register = useCallback(async () => {
    const res  = await authAPI.register();
    const data = res.data;

    localStorage.setItem('access_token',  data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    localStorage.setItem('user_id',       data.user_id);

    setUser({ id: data.user_id });
    return data;
  }, []);

  // ── Login with existing UUID ───────────────────────────────────
  const login = useCallback(async (userId) => {
    const res  = await authAPI.login(userId);
    const data = res.data;

    localStorage.setItem('access_token',  data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);
    localStorage.setItem('user_id',       data.user_id);

    setUser({ id: data.user_id });
    return data;
  }, []);

  // ── Logout ─────────────────────────────────────────────────────
  const logout = useCallback(() => {
    localStorage.clear();
    setUser(null);
  }, []);

  const value = {
    user,
    isAuthenticated: !!user,
    loading,
    register,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Custom hook — components call useAuth() instead of useContext(AuthContext)
export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
