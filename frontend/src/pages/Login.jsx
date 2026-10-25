import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import {
  Building2, Lock, Mail, Eye, EyeOff, UserPlus, LogIn,
  AlertCircle, CheckCircle, ChevronRight, Shield, Landmark, Globe
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export default function Login() {
  const navigate = useNavigate();
  const { lang, changeLanguage, t } = useLanguage();

  const [loginRole, setLoginRole] = useState('customer');
  const [customerMode, setCustomerMode] = useState('signin');

  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [showConfirmPass, setShowConfirmPass] = useState(false);

  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const handleRoleChange = (role) => {
    setLoginRole(role);
    setErrorMsg(null);
    setSuccessMsg(null);
    setEmail('');
    setPassword('');
    setConfirmPassword('');
    setFullName('');
  };

  const handleSignIn = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    const formData = new URLSearchParams();
    formData.append('username', email.trim());
    formData.append('password', password);

    try {
      const res = await axios.post('/api/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      const user = res.data.user;
      localStorage.setItem('grievanceiq_token', res.data.access_token);
      localStorage.setItem('grievanceiq_user', JSON.stringify(user));

      const role = (user.role || '').toUpperCase();

      if (loginRole === 'admin') {
        if (role !== 'ADMIN' && role !== 'OFFICER' && role !== 'STAFF') {
          setErrorMsg(lang === 'hi' ? 'पहुंच अस्वीकृत। यह खाता बैंक स्टाफ विशेषाधिकार नहीं रखता।' : 'Access denied. This account does not have staff privileges.');
          localStorage.removeItem('grievanceiq_token');
          localStorage.removeItem('grievanceiq_user');
          return;
        }
        navigate(role === 'ADMIN' ? '/admin' : '/employee');
      } else {
        if (role !== 'CUSTOMER') {
          setErrorMsg(lang === 'hi' ? 'यह ईमेल स्टाफ खाते से संबद्ध है। कृपया "स्टाफ लॉगिन" टैब का उपयोग करें।' : 'This email belongs to a staff account. Please use the "Staff Login" tab.');
          localStorage.removeItem('grievanceiq_token');
          localStorage.removeItem('grievanceiq_user');
          return;
        }
        navigate('/submit');
      }
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || (lang === 'hi' ? 'अमान्य क्रेडेंशियल। कृपया ईमेल और पासवर्ड की जांच करें।' : 'Invalid credentials. Please check your email and password.'));
    } finally {
      setLoading(false);
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);

    if (password !== confirmPassword) {
      setErrorMsg(lang === 'hi' ? 'पासवर्ड मेल नहीं खा रहे हैं। कृपया पुनः दर्ज करें।' : 'Passwords do not match. Please re-enter.');
      setLoading(false);
      return;
    }
    if (password.length < 6) {
      setErrorMsg(lang === 'hi' ? 'पासवर्ड कम से कम 6 अक्षरों का होना चाहिए।' : 'Password must be at least 6 characters.');
      setLoading(false);
      return;
    }

    try {
      await axios.post('/api/auth/register', {
        email: email.trim().toLowerCase(),
        password,
        full_name: fullName.trim() || undefined,
      });

      setSuccessMsg(lang === 'hi' ? 'खाता बन गया! लॉगिन किया जा रहा है...' : 'Account created! Signing you in...');
      const formData = new URLSearchParams();
      formData.append('username', email.trim().toLowerCase());
      formData.append('password', password);

      const loginRes = await axios.post('/api/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      localStorage.setItem('grievanceiq_token', loginRes.data.access_token);
      localStorage.setItem('grievanceiq_user', JSON.stringify(loginRes.data.user));
      navigate('/submit');
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || (lang === 'hi' ? 'पंजीकरण विफल। यह ईमेल पहले से पंजीकृत हो सकता है।' : 'Registration failed. Email may already be registered.'));
    } finally {
      setLoading(false);
    }
  };

  // ─── Styles ──────────────────────────────────────────────────────────────
  const pageStyle = {
    minHeight: '100vh',
    display: 'flex',
    background: 'linear-gradient(135deg, #091e33 0%, #0a2540 50%, #0f3460 100%)',
    fontFamily: "'Inter', system-ui, sans-serif",
    position: 'relative'
  };

  const leftPanelStyle = {
    flex: '1 1 0%',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    padding: '60px 64px',
    color: 'white',
  };

  const rightPanelStyle = {
    flex: '0 0 460px',
    background: '#ffffff',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    padding: '48px 44px',
    boxShadow: '-8px 0 40px rgba(0,0,0,0.25)',
    position: 'relative'
  };

  const inputStyle = {
    width: '100%',
    padding: '11px 14px 11px 40px',
    border: '1.5px solid #d1d5db',
    borderRadius: '8px',
    fontSize: '0.9rem',
    outline: 'none',
    transition: 'border-color 0.2s',
    boxSizing: 'border-box',
    background: '#fafafa',
  };

  const labelStyle = {
    display: 'block',
    fontWeight: '600',
    fontSize: '0.82rem',
    color: '#374151',
    marginBottom: '5px',
    textTransform: 'uppercase',
    letterSpacing: '0.04em',
  };

  const btnPrimary = {
    width: '100%',
    padding: '13px',
    background: 'linear-gradient(135deg, #1e40af, #2563eb)',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontWeight: '700',
    fontSize: '0.95rem',
    cursor: loading ? 'not-allowed' : 'pointer',
    opacity: loading ? 0.7 : 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    letterSpacing: '0.01em',
    transition: 'all 0.2s',
    marginTop: '6px',
  };

  const tabBtnStyle = (active) => ({
    flex: 1,
    padding: '10px',
    border: 'none',
    borderBottom: active ? '2px solid #1e40af' : '2px solid transparent',
    background: 'transparent',
    fontWeight: active ? '700' : '500',
    color: active ? '#1e40af' : '#6b7280',
    fontSize: '0.875rem',
    cursor: 'pointer',
    transition: 'all 0.15s',
  });

  return (
    <div style={pageStyle}>
      {/* ── Top-Right Language Switcher Floating Badge ────────────────────── */}
      <div style={{ position: 'absolute', top: '20px', right: '20px', zIndex: 10, display: 'flex', alignItems: 'center', gap: '8px', background: 'rgba(15, 23, 42, 0.85)', backdropFilter: 'blur(8px)', padding: '6px 12px', borderRadius: '20px', border: '1px solid rgba(255,255,255,0.2)' }}>
        <Globe size={16} color="#c8a04a" />
        <select
          value={lang}
          onChange={(e) => changeLanguage(e.target.value)}
          style={{
            background: 'transparent',
            color: '#f8fafc',
            border: 'none',
            fontSize: '0.82rem',
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

      {/* ── LEFT: Branding Panel ───────────────────────────────────────── */}
      <div style={leftPanelStyle}>
        {/* Logo */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', marginBottom: '56px' }}>
          <div style={{ background: '#c8a04a', borderRadius: '12px', padding: '12px' }}>
            <Building2 size={28} color="white" />
          </div>
          <div>
            <div style={{ fontSize: '1.6rem', fontWeight: '800', letterSpacing: '-0.02em' }}>
              Grievance<span style={{ color: '#c8a04a' }}>IQ</span>
            </div>
            <div style={{ fontSize: '0.72rem', color: '#94a3b8', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.1em' }}>
              {t('login_portal_title')}
            </div>
          </div>
        </div>

        {/* Headline */}
        <div style={{ maxWidth: '460px' }}>
          <div style={{ fontSize: '0.8rem', fontWeight: '700', color: '#c8a04a', textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Landmark size={14} /> {t('login_rbi_badge')}
          </div>
          <h1 style={{ fontSize: '2.6rem', fontWeight: '800', lineHeight: '1.2', margin: '0 0 18px 0', letterSpacing: '-0.03em' }}>
            {t('login_hero_line1')}<br />
            <span style={{ color: '#93c5fd' }}>{t('login_hero_line2')}</span>
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '1rem', lineHeight: '1.65', margin: '0 0 40px 0' }}>
            {t('login_hero_desc')}
          </p>

          {/* Feature pills */}
          {[
            { icon: '🔒', text: t('login_feat_1') },
            { icon: '⚡', text: t('login_feat_2') },
            { icon: '📄', text: t('login_feat_3') },
            { icon: '🌐', text: t('login_feat_4') },
          ].map((f, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '10px 16px', background: 'rgba(255,255,255,0.06)', borderRadius: '8px', marginBottom: '10px', border: '1px solid rgba(255,255,255,0.08)' }}>
              <span style={{ fontSize: '1.1rem' }}>{f.icon}</span>
              <span style={{ color: '#cbd5e1', fontSize: '0.875rem', fontWeight: '500' }}>{f.text}</span>
            </div>
          ))}
        </div>

        {/* Bottom notice */}
        <div style={{ marginTop: '48px', paddingTop: '24px', borderTop: '1px solid rgba(255,255,255,0.1)', color: '#94a3b8', fontSize: '0.78rem' }}>
          <Shield size={12} style={{ verticalAlign: 'middle', marginRight: '6px' }} />
          {t('login_rbi_scheme')}
        </div>
      </div>

      {/* ── RIGHT: Auth Panel ─────────────────────────────────────────────── */}
      <div style={rightPanelStyle}>
        {/* Header */}
        <div style={{ marginBottom: '28px' }}>
          <h2 style={{ fontSize: '1.45rem', fontWeight: '800', color: '#0f172a', margin: '0 0 6px 0' }}>
            {loginRole === 'customer'
              ? (customerMode === 'signup' ? t('login_create_acc') : t('login_welcome_back'))
              : t('login_staff_title')}
          </h2>
          <p style={{ color: '#6b7280', fontSize: '0.875rem', margin: 0 }}>
            {loginRole === 'customer'
              ? (customerMode === 'signup'
                ? t('login_register_subtitle')
                : t('login_cust_subtitle'))
              : t('login_staff_subtitle')}
          </p>
        </div>

        {/* Role Toggle */}
        <div style={{ display: 'flex', background: '#f1f5f9', borderRadius: '10px', padding: '4px', marginBottom: '22px' }}>
          {[
            { id: 'customer', label: t('login_cust_tab') },
            { id: 'admin', label: t('login_staff_tab') },
          ].map(tab => (
            <button
              key={tab.id}
              type="button"
              onClick={() => handleRoleChange(tab.id)}
              style={{
                flex: 1, padding: '9px 6px', border: 'none', borderRadius: '7px', cursor: 'pointer',
                background: loginRole === tab.id ? 'white' : 'transparent',
                fontWeight: loginRole === tab.id ? '700' : '500',
                color: loginRole === tab.id ? '#1e40af' : '#6b7280',
                fontSize: '0.83rem',
                boxShadow: loginRole === tab.id ? '0 1px 4px rgba(0,0,0,0.12)' : 'none',
                transition: 'all 0.2s',
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Customer mode tabs */}
        {loginRole === 'customer' && (
          <div style={{ display: 'flex', borderBottom: '1px solid #e5e7eb', marginBottom: '20px' }}>
            <button style={tabBtnStyle(customerMode === 'signin')} onClick={() => { setCustomerMode('signin'); setErrorMsg(null); }}>
              {t('login_tab_signin')}
            </button>
            <button style={tabBtnStyle(customerMode === 'signup')} onClick={() => { setCustomerMode('signup'); setErrorMsg(null); }}>
              {t('login_tab_signup')}
            </button>
          </div>
        )}

        {/* Alerts */}
        {errorMsg && (
          <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-start', background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', padding: '12px 14px', marginBottom: '16px' }}>
            <AlertCircle size={16} color="#dc2626" style={{ marginTop: '1px', flexShrink: 0 }} />
            <span style={{ color: '#991b1b', fontSize: '0.85rem', lineHeight: '1.4' }}>{errorMsg}</span>
          </div>
        )}
        {successMsg && (
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center', background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '12px 14px', marginBottom: '16px' }}>
            <CheckCircle size={16} color="#16a34a" />
            <span style={{ color: '#166534', fontSize: '0.85rem' }}>{successMsg}</span>
          </div>
        )}

        {/* ── ADMIN FORM ── */}
        {loginRole === 'admin' && (
          <form onSubmit={handleSignIn}>
            <div style={{ marginBottom: '16px' }}>
              <label style={labelStyle}>{t('login_official_email')}</label>
              <div style={{ position: 'relative' }}>
                <Mail size={15} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} />
                <input
                  type="email"
                  style={inputStyle}
                  placeholder="your.name@bank.org"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                />
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={labelStyle}>{t('login_password_label')}</label>
              <div style={{ position: 'relative' }}>
                <Lock size={15} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} />
                <input
                  type={showPass ? 'text' : 'password'}
                  style={{ ...inputStyle, paddingRight: '40px' }}
                  placeholder="••••••••"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                />
                <button type="button" onClick={() => setShowPass(p => !p)}
                  style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: '#9ca3af', padding: 0 }}>
                  {showPass ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>

            <button type="submit" style={btnPrimary} disabled={loading}>
              {loading ? t('login_verifying') : <><LogIn size={16} /> {t('login_btn_staff_signin')}</>}
            </button>

            <div style={{ marginTop: '18px', padding: '12px 14px', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e5e7eb' }}>
              <div style={{ fontSize: '0.75rem', color: '#6b7280', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Shield size={12} color="#6b7280" />
                <span>{t('login_staff_disclaimer')}</span>
              </div>
            </div>
          </form>
        )}

        {/* ── CUSTOMER SIGN IN ── */}
        {loginRole === 'customer' && customerMode === 'signin' && (
          <form onSubmit={handleSignIn}>
            <div style={{ marginBottom: '16px' }}>
              <label style={labelStyle}>{t('login_email_label')}</label>
              <div style={{ position: 'relative' }}>
                <Mail size={15} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} />
                <input
                  type="email"
                  style={inputStyle}
                  placeholder="you@gmail.com"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                />
              </div>
            </div>

            <div style={{ marginBottom: '22px' }}>
              <label style={labelStyle}>{t('login_password_label')}</label>
              <div style={{ position: 'relative' }}>
                <Lock size={15} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} />
                <input
                  type={showPass ? 'text' : 'password'}
                  style={{ ...inputStyle, paddingRight: '40px' }}
                  placeholder="••••••••"
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                />
                <button type="button" onClick={() => setShowPass(p => !p)}
                  style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: '#9ca3af', padding: 0 }}>
                  {showPass ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>

            <button type="submit" style={btnPrimary} disabled={loading}>
              {loading ? t('login_signing_in') : <><LogIn size={16} /> {t('login_btn_signin')} <ChevronRight size={15} /></>}
            </button>

            <p style={{ textAlign: 'center', marginTop: '18px', fontSize: '0.875rem', color: '#6b7280' }}>
              {t('login_no_acc')}{' '}
              <button type="button" onClick={() => { setCustomerMode('signup'); setErrorMsg(null); }}
                style={{ background: 'none', border: 'none', color: '#1e40af', fontWeight: '700', cursor: 'pointer', fontSize: '0.875rem' }}>
                {t('login_register_here')}
              </button>
            </p>
          </form>
        )}

        {/* ── CUSTOMER SIGN UP ── */}
        {loginRole === 'customer' && customerMode === 'signup' && (
          <form onSubmit={handleSignUp}>
            <div style={{ marginBottom: '14px' }}>
              <label style={labelStyle}>{t('login_fullname_label')}</label>
              <div style={{ position: 'relative' }}>
                <UserPlus size={15} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} />
                <input
                  type="text"
                  style={inputStyle}
                  placeholder={lang === 'hi' ? 'उदा. राहुल शर्मा' : 'e.g. Rahul Sharma'}
                  value={fullName}
                  onChange={e => setFullName(e.target.value)}
                  autoComplete="name"
                />
              </div>
            </div>

            <div style={{ marginBottom: '14px' }}>
              <label style={labelStyle}>{t('login_email_label')}</label>
              <div style={{ position: 'relative' }}>
                <Mail size={15} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} />
                <input
                  type="email"
                  style={inputStyle}
                  placeholder="you@gmail.com"
                  value={email}
                  onChange={e => setEmail(e.target.value)}
                  required
                  autoComplete="email"
                />
              </div>
            </div>

            <div style={{ marginBottom: '14px' }}>
              <label style={labelStyle}>{t('login_password_label')}</label>
              <div style={{ position: 'relative' }}>
                <Lock size={15} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} />
                <input
                  type={showPass ? 'text' : 'password'}
                  style={{ ...inputStyle, paddingRight: '40px' }}
                  placeholder={lang === 'hi' ? 'कम से कम 6 अक्षर' : 'Minimum 6 characters'}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  required
                  autoComplete="new-password"
                />
                <button type="button" onClick={() => setShowPass(p => !p)}
                  style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: '#9ca3af', padding: 0 }}>
                  {showPass ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>

            <div style={{ marginBottom: '20px' }}>
              <label style={labelStyle}>{t('login_confirm_password')}</label>
              <div style={{ position: 'relative' }}>
                <Lock size={15} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} />
                <input
                  type={showConfirmPass ? 'text' : 'password'}
                  style={{ ...inputStyle, paddingRight: '40px' }}
                  placeholder={lang === 'hi' ? 'पासवर्ड पुनः दर्ज करें' : 'Re-enter your password'}
                  value={confirmPassword}
                  onChange={e => setConfirmPassword(e.target.value)}
                  required
                  autoComplete="new-password"
                />
                <button type="button" onClick={() => setShowConfirmPass(p => !p)}
                  style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: '#9ca3af', padding: 0 }}>
                  {showConfirmPass ? <EyeOff size={15} /> : <Eye size={15} />}
                </button>
              </div>
            </div>

            <button type="submit" style={{ ...btnPrimary, background: 'linear-gradient(135deg, #166534, #16a34a)' }} disabled={loading}>
              {loading ? t('login_creating') : <><UserPlus size={16} /> {t('login_btn_create')}</>}
            </button>

            <p style={{ textAlign: 'center', marginTop: '18px', fontSize: '0.875rem', color: '#6b7280' }}>
              {t('login_already_acc')}{' '}
              <button type="button" onClick={() => { setCustomerMode('signin'); setErrorMsg(null); }}
                style={{ background: 'none', border: 'none', color: '#1e40af', fontWeight: '700', cursor: 'pointer', fontSize: '0.875rem' }}>
                {t('login_signin_here')}
              </button>
            </p>
          </form>
        )}

        {/* Footer */}
        <div style={{ marginTop: '28px', paddingTop: '20px', borderTop: '1px solid #f1f5f9', textAlign: 'center', fontSize: '0.75rem', color: '#9ca3af' }}>
          GrievanceIQ © 2026 &bull; {lang === 'hi' ? 'सुरक्षित बैंकिंग शिकायत पोर्टल • संपूर्ण डेटा एन्क्रिप्टेड' : 'Secured Banking Complaint Portal • All data encrypted'}
        </div>
      </div>
    </div>
  );
}
