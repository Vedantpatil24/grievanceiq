import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ShieldCheck, Search, LogIn, LogOut, LayoutDashboard, FileText, History, Briefcase, Building2, Globe, Bell } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export default function Navbar() {
  const { lang, changeLanguage, t } = useLanguage();
  const location = useLocation();
  const navigate = useNavigate();
  const token = localStorage.getItem('grievanceiq_token');
  const userStr = localStorage.getItem('grievanceiq_user');
  const user = userStr ? JSON.parse(userStr) : null;
  const role = (user?.role || '').toUpperCase();
  const [notifCount, setNotifCount] = React.useState(0);
  const [showNotifMenu, setShowNotifMenu] = React.useState(false);
  const [notifications, setNotifications] = React.useState([]);

  React.useEffect(() => {
    if (token) {
      fetch('http://localhost:8000/api/notifications?recipient_type=customer')
        .then(r => r.json())
        .then(data => {
          if (Array.isArray(data)) {
            setNotifications(data.slice(0, 5));
            setNotifCount(data.length);
          }
        })
        .catch(() => {});
    }
  }, [token, location.pathname]);
  const isAdmin = role === 'ADMIN';
  const isOfficer = role === 'OFFICER' || role === 'STAFF';
  const isCustomer = role === 'CUSTOMER';

  const handleLogout = () => {
    localStorage.removeItem('grievanceiq_token');
    localStorage.removeItem('grievanceiq_user');
    navigate('/login');
  };

  // Don't show navbar on login page (login has its own full-page design)
  if (location.pathname === '/login') return null;

  return (
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
            <option value="ta" style={{ background: '#0f172a', color: '#fff' }}>தமிழ் (Tamil)</option>
            <option value="gu" style={{ background: '#0f172a', color: '#fff' }}>ગુજરાતી (Gujarati)</option>
          </select>
        </div>

                {/* User Notifications */}
        {token && (
          <div style={{ position: 'relative', marginLeft: '8px' }}>
            <button 
              onClick={() => setShowNotifMenu(!showNotifMenu)}
              style={{ background: '#1e293b', border: '1px solid #334155', borderRadius: '6px', padding: '6px 10px', color: '#f8fafc', cursor: 'pointer', display: 'flex', alignItems: 'center', position: 'relative' }}
              title="Notifications"
            >
              <Bell size={16} />
              {notifCount > 0 && (
                <span style={{ position: 'absolute', top: '-4px', right: '-4px', background: '#ef4444', color: '#fff', fontSize: '0.65rem', fontWeight: '800', width: '16px', height: '16px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  {notifCount}
                </span>
              )}
            </button>
            {showNotifMenu && (
              <div style={{ position: 'absolute', right: 0, top: '38px', width: '320px', background: '#0f172a', border: '1px solid #334155', borderRadius: '8px', boxShadow: '0 10px 25px rgba(0,0,0,0.5)', zIndex: 1000, padding: '12px' }}>
                <div style={{ fontWeight: '700', fontSize: '0.85rem', color: '#f8fafc', borderBottom: '1px solid #1e293b', paddingBottom: '8px', marginBottom: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span>🔔 Grievance Notifications</span>
                  <span style={{ fontSize: '0.7rem', color: '#38bdf8' }}>{notifCount} Updates</span>
                </div>
                {notifications.length === 0 ? (
                  <div style={{ fontSize: '0.8rem', color: '#94a3b8', textAlign: 'center', padding: '12px 0' }}>No new notifications</div>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '240px', overflowY: 'auto' }}>
                    {notifications.map((n, idx) => (
                      <div key={idx} style={{ background: '#1e293b', padding: '8px 10px', borderRadius: '6px', fontSize: '0.78rem', color: '#e2e8f0', borderLeft: '3px solid #10b981' }}>
                        <div style={{ fontWeight: '700', color: '#10b981', marginBottom: '2px' }}>{n.title || 'Resolution Update'}</div>
                        <div style={{ fontSize: '0.75rem', color: '#cbd5e1' }}>{n.message || n.details || 'Complaint status updated.'}</div>
                      </div>
                    ))}
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
  );
}
