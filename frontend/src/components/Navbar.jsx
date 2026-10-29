import React, { useRef, useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  ShieldCheck, Search, LogIn, LogOut, LayoutDashboard, FileText, 
  History, Briefcase, Building2, Globe, Bell, X, ExternalLink, Info, CheckCircle2, AlertTriangle 
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export default function Navbar() {
  const { lang, changeLanguage, t } = useLanguage();
  const location = useLocation();
  const navigate = useNavigate();
  const token = localStorage.getItem('grievanceiq_token');
  const userStr = localStorage.getItem('grievanceiq_user');
  const user = userStr ? JSON.parse(userStr) : null;
  const role = (user?.role || '').toUpperCase();
  const [notifCount, setNotifCount] = useState(0);
  const [showNotifMenu, setShowNotifMenu] = useState(false);
  const [notifications, setNotifications] = useState([]);
  
  // Floating Toast notification for real-time alerts
  const [activeToast, setActiveToast] = useState(null);
  const previousNotifIds = useRef(new Set());
  const notifMenuRef = useRef(null);

  // Close notification popover when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (notifMenuRef.current && !notifMenuRef.current.contains(event.target)) {
        setShowNotifMenu(false);
      }
    }
    if (showNotifMenu) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showNotifMenu]);

  // Fetch notifications periodically
  useEffect(() => {
    let intervalId;
    const fetchNotifs = () => {
      if (token) {
        const recipientType = role === 'ADMIN' ? 'admin' : (role === 'OFFICER' || role === 'STAFF') ? 'staff' : 'customer';
        fetch(`/api/notifications?recipient_type=${recipientType}`)
          .then(r => r.json())
          .then(data => {
            if (Array.isArray(data)) {
              setNotifications(data.slice(0, 8));
              setNotifCount(data.length);

              // Check if there is a new incoming notification to pop up as a Toast banner
              if (data.length > 0) {
                const latest = data[0];
                if (previousNotifIds.current.size > 0 && !previousNotifIds.current.has(latest.notification_id)) {
                  // Trigger interactive Popup Toast
                  setActiveToast(latest);
                }
                // Save current IDs
                previousNotifIds.current = new Set(data.map(n => n.notification_id));
              }
            }
          })
          .catch(() => {});
      }
    };

    fetchNotifs();
    intervalId = setInterval(fetchNotifs, 10000); // check every 10s

    return () => clearInterval(intervalId);
  }, [token, role, location.pathname]);

  // Auto-dismiss toast banner after 7 seconds
  useEffect(() => {
    if (activeToast) {
      const timer = setTimeout(() => {
        setActiveToast(null);
      }, 7000);
      return () => clearTimeout(timer);
    }
  }, [activeToast]);

  const isAdmin = role === 'ADMIN';
  const isOfficer = role === 'OFFICER' || role === 'STAFF';
  const isCustomer = role === 'CUSTOMER';

  const handleLogout = () => {
    localStorage.removeItem('grievanceiq_token');
    localStorage.removeItem('grievanceiq_user');
    navigate('/login');
  };

  const handleNotificationClick = (n) => {
    setShowNotifMenu(false);
    setActiveToast(null);
    if (n.token) {
      navigate(`/track?token=${n.token}`);
    } else {
      navigate('/history');
    }
  };

  // Don't show navbar on login page
  if (location.pathname === '/login') return null;

  return (
    <>
      <nav className="navbar">
        <div className="nav-brand">
          <Link to={isAdmin ? '/admin' : isOfficer ? '/employee' : '/submit'} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Building2 size={26} color="#c8a04a" />
            <span>Grievance<strong style={{ color: '#c8a04a' }}>IQ</strong></span>
          </Link>
          <span style={{ fontSize: '0.72rem', background: '#1e3a8a', color: '#bfdbfe', padding: '2px 8px', borderRadius: '4px', marginLeft: '6px', fontWeight: '600' }}>
            {isAdmin ? t('portal_admin') : isOfficer ? t('portal_officer') : t('portal_customer')}
          </span>
        </div>

        <div className="nav-links">
          {/* Customer Links */}
          {(isCustomer || !token) && (
            <>
              <Link to="/submit" className={`nav-link ${location.pathname === '/submit' ? 'active' : ''}`}>
                <FileText size={15} style={{ marginRight: '6px' }} />
                {t('nav_submit')}
              </Link>
              <Link to="/track" className={`nav-link ${location.pathname === '/track' ? 'active' : ''}`}>
                <Search size={15} style={{ marginRight: '6px' }} />
                {t('nav_track')}
              </Link>
              <Link to="/history" className={`nav-link ${location.pathname === '/history' ? 'active' : ''}`}>
                <History size={15} style={{ marginRight: '6px' }} />
                {t('nav_history')}
              </Link>
            </>
          )}

          {/* Officer Links */}
          {isOfficer && (
            <Link to="/employee" className={`nav-link ${location.pathname === '/employee' ? 'active' : ''}`} style={{ color: '#c8a04a' }}>
              <Briefcase size={15} style={{ marginRight: '6px' }} />
              {t('nav_officer_workspace')}
            </Link>
          )}

          {/* Admin Links */}
          {isAdmin && (
            <Link to="/admin" className={`nav-link ${location.pathname === '/admin' ? 'active' : ''}`} style={{ color: '#38bdf8' }}>
              <LayoutDashboard size={15} style={{ marginRight: '6px' }} />
              {t('nav_admin_console')}
            </Link>
          )}

          {/* Language Switcher Dropdown */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginLeft: '12px', background: '#1e293b', padding: '4px 8px', borderRadius: '6px', border: '1px solid #334155' }}>
            <Globe size={14} color="#94a3b8" />
            <select
              value={lang}
              onChange={(e) => changeLanguage(e.target.value)}
              style={{
                background: 'transparent',
                color: '#f8fafc',
                border: 'none',
                fontSize: '0.78rem',
                fontWeight: '600',
                cursor: 'pointer',
                outline: 'none'
              }}
            >
              <option value="en" style={{ background: '#0f172a', color: '#fff' }}>English</option>
              <option value="hi" style={{ background: '#0f172a', color: '#fff' }}>हिंदी (Hindi)</option>
              <option value="mr" style={{ background: '#0f172a', color: '#fff' }}>मराठी (Marathi)</option>
            </select>
          </div>

          {/* User Notifications */}
          {token && (
            <div ref={notifMenuRef} style={{ position: 'relative', marginLeft: '8px' }}>
              <button 
                onClick={() => setShowNotifMenu(!showNotifMenu)}
                style={{ 
                  background: showNotifMenu ? '#2563eb' : '#1e293b', 
                  border: '1px solid #334155', 
                  borderRadius: '6px', 
                  padding: '6px 10px', 
                  color: '#f8fafc', 
                  cursor: 'pointer', 
                  display: 'flex', 
                  alignItems: 'center', 
                  position: 'relative',
                  transition: 'background 0.2s'
                }}
                title="Notifications"
              >
                <Bell size={16} />
                {notifCount > 0 && (
                  <span style={{ position: 'absolute', top: '-4px', right: '-4px', background: '#ef4444', color: '#fff', fontSize: '0.65rem', fontWeight: '800', width: '16px', height: '16px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 6px rgba(239, 68, 68, 0.8)' }}>
                    {notifCount}
                  </span>
                )}
              </button>

              {/* DROPDOWN MENU */}
              {showNotifMenu && (
                <div style={{ 
                  position: 'absolute', 
                  right: 0, 
                  top: '42px', 
                  width: '360px', 
                  background: '#0f172a', 
                  border: '1px solid #334155', 
                  borderRadius: '10px', 
                  boxShadow: '0 15px 35px rgba(0,0,0,0.6)', 
                  zIndex: 1000, 
                  padding: '14px',
                  animation: 'fadeIn 0.2s ease-out'
                }}>
                  <div style={{ fontWeight: '700', fontSize: '0.88rem', color: '#f8fafc', borderBottom: '1px solid #1e293b', paddingBottom: '10px', marginBottom: '10px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <Bell size={15} color="#38bdf8" />
                      <span>Grievance Notifications</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '0.7rem', background: '#1e3a8a', color: '#93c5fd', padding: '2px 8px', borderRadius: '12px' }}>
                        {notifCount} Updates
                      </span>
                      <button 
                        onClick={() => setShowNotifMenu(false)}
                        style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '2px', display: 'flex' }}
                        title="Close"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  </div>

                  {notifications.length === 0 ? (
                    <div style={{ fontSize: '0.85rem', color: '#94a3b8', textAlign: 'center', padding: '24px 0' }}>
                      No new notifications
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '320px', overflowY: 'auto' }}>
                      {notifications.map((n, idx) => {
                        const isRejected = (n.title || '').includes('Rejected') || (n.body || '').includes('rejected') || n.notification_type === 'EVIDENCE_REJECTED';
                        const isResolved = (n.title || '').includes('Resolved') || (n.status || '') === 'resolved';
                        const isEscalated = (n.title || '').includes('Escalated') || (n.status || '') === 'escalated';
                        
                        const borderColor = isRejected ? '#ef4444' : isResolved ? '#10b981' : isEscalated ? '#f59e0b' : '#38bdf8';
                        const titleColor = isRejected ? '#fca5a5' : isResolved ? '#6ee7b7' : isEscalated ? '#fcd34d' : '#38bdf8';
                        const badgeBg = isRejected ? 'rgba(239, 68, 68, 0.15)' : isResolved ? 'rgba(16, 185, 129, 0.15)' : isEscalated ? 'rgba(245, 158, 11, 0.15)' : 'rgba(56, 189, 248, 0.15)';
                        const badgeColor = isRejected ? '#f87171' : isResolved ? '#34d399' : isEscalated ? '#fbbf24' : '#38bdf8';
                        const badgeLabel = isRejected ? 'Action Needed' : isResolved ? 'Resolved' : isEscalated ? 'Escalated' : 'Status Update';

                        return (
                          <div 
                            key={idx} 
                            onClick={() => handleNotificationClick(n)}
                            style={{ 
                              background: '#1e293b', 
                              padding: '11px 13px', 
                              borderRadius: '8px', 
                              fontSize: '0.8rem', 
                              color: '#e2e8f0', 
                              borderLeft: `4px solid ${borderColor}`,
                              cursor: 'pointer',
                              transition: 'background 0.15s, transform 0.1s',
                              position: 'relative'
                            }}
                            onMouseEnter={(e) => e.currentTarget.style.background = '#273549'}
                            onMouseLeave={(e) => e.currentTarget.style.background = '#1e293b'}
                          >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                              <span style={{ fontWeight: '700', color: titleColor, fontSize: '0.82rem' }}>
                                {n.title || 'Resolution Update'}
                              </span>
                              <span style={{ fontSize: '0.65rem', background: badgeBg, color: badgeColor, padding: '2px 6px', borderRadius: '4px', fontWeight: '700' }}>
                                {badgeLabel}
                              </span>
                            </div>

                            <div style={{ fontSize: '0.78rem', color: '#cbd5e1', lineHeight: '1.45', marginBottom: '6px' }}>
                              {n.body || n.message || n.details || 'Complaint details updated.'}
                            </div>

                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.72rem', color: '#64748b', borderTop: '1px solid #334155', paddingTop: '6px' }}>
                              <span style={{ color: '#93c5fd', fontWeight: '600' }}>
                                {n.token ? `#${n.token}` : ''} {n.service_type ? `• ${n.service_type}` : ''}
                              </span>
                              <span style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#38bdf8', fontWeight: '600' }}>
                                Open Ticket <ExternalLink size={11} />
                              </span>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {token ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginLeft: '10px', borderLeft: '1px solid #334155', paddingLeft: '14px' }}>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.85rem', color: '#f8fafc', fontWeight: '600' }}>
                  {user?.full_name || user?.username}
                </div>
                <div style={{ fontSize: '0.72rem', color: '#94a3b8' }}>
                  {user?.role}
                </div>
              </div>
              <button 
                onClick={handleLogout} 
                className="btn btn-outline" 
                style={{ padding: '6px 12px', fontSize: '0.8rem', color: '#f87171', borderColor: '#ef4444' }}
              >
                <LogOut size={13} /> {t('nav_sign_out')}
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: '8px', marginLeft: '8px' }}>
              <Link to="/login" className="btn btn-primary" style={{ padding: '6px 14px', fontSize: '0.85rem' }}>
                <LogIn size={14} /> {t('nav_sign_in')}
              </Link>
            </div>
          )}
        </div>
      </nav>

      {/* FLOATING REAL-TIME NOTIFICATION POPUP TOAST (Auto-dismisses & Clickable) */}
      {activeToast && (
        <div style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          zIndex: 9999,
          maxWidth: '380px',
          width: '90%',
          background: '#0f172a',
          color: '#f8fafc',
          borderRadius: '12px',
          border: '1px solid #38bdf8',
          boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
          padding: '16px',
          animation: 'slideUp 0.3s ease-out',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ background: '#0284c7', color: 'white', borderRadius: '50%', padding: '4px', display: 'flex' }}>
                <Bell size={14} />
              </span>
              <strong style={{ fontSize: '0.9rem', color: '#38bdf8' }}>{activeToast.title}</strong>
            </div>
            <button 
              onClick={() => setActiveToast(null)} 
              style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', padding: '2px' }}
            >
              <X size={16} />
            </button>
          </div>

          <div style={{ fontSize: '0.82rem', color: '#cbd5e1', lineHeight: '1.4' }}>
            {activeToast.body || activeToast.message}
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px', marginTop: '4px' }}>
            {activeToast.token && (
              <button 
                onClick={() => handleNotificationClick(activeToast)}
                style={{
                  background: '#2563eb',
                  color: 'white',
                  border: 'none',
                  borderRadius: '6px',
                  padding: '6px 12px',
                  fontSize: '0.78rem',
                  fontWeight: '700',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                View Complaint #{activeToast.token} <ExternalLink size={12} />
              </button>
            )}
            <button 
              onClick={() => setActiveToast(null)}
              style={{
                background: '#334155',
                color: '#cbd5e1',
                border: 'none',
                borderRadius: '6px',
                padding: '6px 10px',
                fontSize: '0.78rem',
                cursor: 'pointer'
              }}
            >
              Dismiss
            </button>
          </div>
        </div>
      )}
    </>
  );
}
