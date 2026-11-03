import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LanguageProvider, useLanguage } from './context/LanguageContext';
import Navbar from './components/Navbar';
import NovaAssistant from './components/NovaAssistant';

// Code-split heavy pages — loaded on demand, optimizes initial bundle size
const Login             = lazy(() => import('./pages/Login'));
const SubmitComplaint   = lazy(() => import('./pages/SubmitComplaint'));
const TrackComplaint    = lazy(() => import('./pages/TrackComplaint'));
const CustomerHistory   = lazy(() => import('./pages/CustomerHistory'));
const AdminDashboard    = lazy(() => import('./pages/AdminDashboard'));
const EmployeeDashboard = lazy(() => import('./pages/EmployeeDashboard'));

const PageLoader = () => (
  <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh', flexDirection: 'column', gap: '12px' }}>
    <div style={{ width: '40px', height: '40px', border: '3px solid #e2e8f0', borderTop: '3px solid #2563eb', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
    <span style={{ color: '#64748b', fontSize: '0.875rem' }}>Loading…</span>
    <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
  </div>
);

function AppContent() {
  const { t } = useLanguage();
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Navbar />
      <main style={{ flex: 1, paddingBottom: '40px' }}>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<Navigate to="/login" replace />} />
            <Route path="/login" element={<Login />} />
            <Route path="/submit" element={<SubmitComplaint />} />
            <Route path="/history" element={<CustomerHistory />} />
            <Route path="/track" element={<TrackComplaint />} />
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/employee" element={<EmployeeDashboard />} />
            <Route path="*" element={<Navigate to="/login" replace />} />
          </Routes>
        </Suspense>
      </main>
      <NovaAssistant />
      <footer style={{ background: '#0f172a', color: '#94a3b8', textAlign: 'center', padding: '16px', fontSize: '0.8rem', borderTop: '1px solid #1e293b' }}>
        {t('footer_text')}
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <LanguageProvider>
      <BrowserRouter>
        <AppContent />
      </BrowserRouter>
    </LanguageProvider>
  );
}
