import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';

import LandingPage    from './pages/LandingPage';
import Dashboard      from './pages/Dashboard';
import ChatPage       from './pages/ChatPage';
import MoodPage       from './pages/MoodPage';
import EmergencyPage  from './pages/EmergencyPage';
import AppLayout      from './components/layout/AppLayout';

import './index.css';

/** Protected route — redirects to landing if not authenticated */
function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen" style={{ background: 'var(--bg-primary)' }}>
        <div style={{ textAlign: 'center' }}>
          <div className="animate-pulse-soft" style={{ fontSize: 48, marginBottom: 16 }}>💙</div>
          <p style={{ color: 'var(--text-muted)', fontFamily: 'DM Sans' }}>Loading your safe space...</p>
        </div>
      </div>
    );
  }

  return isAuthenticated ? children : <Navigate to="/" replace />;
}

function AppRoutes() {
  return (
    <Routes>
      {/* Public route */}
      <Route path="/" element={<LandingPage />} />

      {/* Protected routes — wrapped in sidebar layout */}
      <Route path="/app" element={
        <ProtectedRoute>
          <AppLayout />
        </ProtectedRoute>
      }>
        <Route index        element={<Navigate to="/app/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="chat"      element={<ChatPage />} />
        <Route path="mood"      element={<MoodPage />} />
        <Route path="emergency" element={<EmergencyPage />} />
      </Route>

      {/* Catch-all */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AuthProvider>
  );
}
