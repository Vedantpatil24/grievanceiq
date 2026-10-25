import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { ShieldCheck, Search, LogIn, LogOut, LayoutDashboard, FileText, History, Briefcase, Building2, Globe } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export default function Navbar() {
  const { lang, changeLanguage, t } = useLanguage();
  const location = useLocation();
  const navigate = useNavigate();
  const token = localStorage.getItem('grievanceiq_token');
  const userStr = localStorage.getItem('grievanceiq_user');
  const user = userStr ? JSON.parse(userStr) : null;
  const role = (user?.role || '').toUpperCase();
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
