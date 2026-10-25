import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import {
  ClipboardList, CheckCircle2, AlertTriangle, Clock, ChevronDown, ChevronUp,
  User, FileText, MessageSquare, Shield, XCircle, Send, RefreshCw,
  TrendingUp, Briefcase, FileBadge, Lock, LogOut, AlertCircle, Upload, Eye, Globe
} from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

const API = axios.create({ baseURL: '' });

const getAuthHeaders = () => {
  const token = localStorage.getItem('grievanceiq_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const PRIORITY_COLORS = {
  High: { bg: '#fef2f2', text: '#b91c1c', border: '#fca5a5', dot: '#ef4444' },
  Medium: { bg: '#fffbeb', text: '#92400e', border: '#fcd34d', dot: '#f59e0b' },
  Low: { bg: '#f0fdf4', text: '#166534', border: '#86efac', dot: '#22c55e' },
};

const STATUS_COLORS = {
  open: { color: '#6366f1', bg: '#eef2ff' },
  in_progress: { color: '#0284c7', bg: '#e0f2fe' },
  escalated: { color: '#dc2626', bg: '#fee2e2' },
  resolved: { color: '#16a34a', bg: '#dcfce7' },
  resolution_proposed: { color: '#7c3aed', bg: '#ede9fe' },
  closed: { color: '#475569', bg: '#f1f5f9' },
  reopened: { color: '#c2410c', bg: '#fff7ed' },
};

export default function EmployeeDashboard() {
  const { lang, changeLanguage, t, tStatus, tPriority, tDept } = useLanguage();

  const [user, setUser] = useState(null);
  const [stats, setStats] = useState(null);
  const [complaints, setComplaints] = useState([]);
  const [filteredComplaints, setFilteredComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterPriority, setFilterPriority] = useState('all');
  const [searchText, setSearchText] = useState('');
  const [activeTab, setActiveTab] = useState('details'); // details | notes | resolve | messages
  const [noteText, setNoteText] = useState('');
  const [resolutionForm, setResolutionForm] = useState({
    resolution_details: '',
    resolution_type: 'FULL_REFUND',
    transaction_reference: '',
    resolved_amount: '',
  });
  const [resolutionFile, setResolutionFile] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [notes, setNotes] = useState([]);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionMsg, setActionMsg] = useState(null);
  const [evidenceAnalysis, setEvidenceAnalysis] = useState(null);
  const [evidenceAnalysisLoading, setEvidenceAnalysisLoading] = useState(false);

  useEffect(() => {
    const stored = localStorage.getItem('grievanceiq_user');
    if (stored) setUser(JSON.parse(stored));
  }, []);

  const fetchData = useCallback(async () => {
    setLoading(true);
    try {
      const [statsRes, complaintsRes] = await Promise.all([
        API.get('/api/officer/stats', { headers: getAuthHeaders() }),
        API.get('/api/officer/complaints', { headers: getAuthHeaders() }),
      ]);
      setStats(statsRes.data);
      setComplaints(complaintsRes.data);
      setFilteredComplaints(complaintsRes.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  useEffect(() => {
    let result = [...complaints];
    if (filterStatus !== 'all') result = result.filter(c => c.status === filterStatus);
    if (filterPriority !== 'all') result = result.filter(c => c.priority === filterPriority);
    if (searchText.trim()) {
      const s = searchText.toLowerCase();
      result = result.filter(c =>
        c.token?.toLowerCase().includes(s) ||
        c.description?.toLowerCase().includes(s) ||
        c.customer_name?.toLowerCase().includes(s) ||
        c.service_type?.toLowerCase().includes(s)
      );
    }
    setFilteredComplaints(result);
  }, [complaints, filterStatus, filterPriority, searchText]);

  const openComplaint = async (complaint) => {
    setSelectedComplaint(complaint);
    setActiveTab('details');
    setActionMsg(null);
    setEvidenceAnalysis(null);
    try {
      const [notesRes, msgsRes] = await Promise.all([
        API.get(`/api/worker/complaints/${complaint.token}/notes`, { headers: getAuthHeaders() }),
        API.get(`/api/complaints/${complaint.token}/messages`),
      ]);
      setNotes(notesRes.data);
      setMessages(msgsRes.data);
    } catch (err) {
      console.error('Failed to load notes/messages', err);
    }
  };

  const handleVerifyEvidence = async (status) => {
    setActionLoading(true);
    try {
      await API.put(
        `/api/worker/complaints/${selectedComplaint.token}/verify-evidence`,
        { status, reason: status === 'REJECTED' ? (lang === 'hi' ? 'दस्तावेज़ अस्पष्ट या शिकायत श्रेणी से असंबद्ध है।' : 'Document unclear or irrelevant to category.') : null },
        { headers: getAuthHeaders() }
      );
      setActionMsg({ type: 'success', text: status === 'VERIFIED' ? (lang === 'hi' ? 'साक्ष्य सफलतापूर्वक सत्यापित किया गया।' : 'Evidence verified successfully.') : (lang === 'hi' ? 'साक्ष्य अस्वीकार कर दिया गया।' : 'Evidence rejected.') });
      setSelectedComplaint(prev => ({ ...prev, evidence_status: status }));
      fetchData();
    } catch (err) {
      setActionMsg({ type: 'error', text: err.response?.data?.detail || (lang === 'hi' ? 'कार्रवाई विफल।' : 'Action failed.') });
    } finally {
      setActionLoading(false);
    }
  };

  const runEvidenceAIAnalysis = async () => {
    if (!selectedComplaint) return;
    setEvidenceAnalysisLoading(true);
    setEvidenceAnalysis(null);
    try {
      const res = await API.post(
        `/api/worker/complaints/${selectedComplaint.token}/ai-evidence-analysis`,
        {},
        { headers: getAuthHeaders() }
      );
      setEvidenceAnalysis(res.data);
    } catch (err) {
      setEvidenceAnalysis({ error: err.response?.data?.detail || err.message });
    } finally {
      setEvidenceAnalysisLoading(false);
    }
  };

  const handleAddNote = async () => {
    if (!noteText.trim()) return;
    setActionLoading(true);
    try {
      await API.post(
        `/api/worker/complaints/${selectedComplaint.token}/notes`,
        { note_text: noteText },
        { headers: getAuthHeaders() }
      );
      setNoteText('');
      const notesRes = await API.get(`/api/worker/complaints/${selectedComplaint.token}/notes`, { headers: getAuthHeaders() });
      setNotes(notesRes.data);
      setActionMsg({ type: 'success', text: lang === 'hi' ? 'जांच नोट सहेजा गया।' : 'Investigation note saved.' });
      fetchData();
    } catch (err) {
      setActionMsg({ type: 'error', text: lang === 'hi' ? 'नोट सहेजना विफल।' : 'Failed to save note.' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleSubmitResolution = async () => {
    if (!resolutionForm.resolution_details.trim()) {
      setActionMsg({ type: 'error', text: lang === 'hi' ? 'समाधान का विवरण अनिवार्य है।' : 'Resolution details are required.' });
      return;
    }
    setActionLoading(true);
    try {
      const fd = new FormData();
      fd.append('resolution_details', resolutionForm.resolution_details);
      fd.append('resolution_type', resolutionForm.resolution_type);
      if (resolutionForm.transaction_reference) fd.append('transaction_reference', resolutionForm.transaction_reference);
      if (resolutionForm.resolved_amount) fd.append('resolved_amount', resolutionForm.resolved_amount);
      if (resolutionFile) fd.append('resolution_proof', resolutionFile);

      await API.post(`/api/worker/complaints/${selectedComplaint.token}/resolution`, fd, {
        headers: { ...getAuthHeaders(), 'Content-Type': 'multipart/form-data' }
      });
      setActionMsg({ type: 'success', text: lang === 'hi' ? 'समाधान प्रस्तुत किया गया। ग्राहक पुष्टि की प्रतीक्षा है।' : 'Resolution submitted. Awaiting customer confirmation.' });
      setResolutionForm({ resolution_details: '', resolution_type: 'FULL_REFUND', transaction_reference: '', resolved_amount: '' });
      setResolutionFile(null);
      fetchData();
    } catch (err) {
      setActionMsg({ type: 'error', text: err.response?.data?.detail || (lang === 'hi' ? 'प्रस्तुति विफल।' : 'Submission failed.') });
    } finally {
      setActionLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim()) return;
    setActionLoading(true);
    try {
      await API.post(`/api/complaints/${selectedComplaint.token}/messages`, {
        message_text: newMessage,
        sender_type: 'officer',
        sender_name: user?.full_name || 'Officer'
      }, { headers: getAuthHeaders() });
      setNewMessage('');
      const msgsRes = await API.get(`/api/complaints/${selectedComplaint.token}/messages`);
      setMessages(msgsRes.data);
    } catch (err) {
      setActionMsg({ type: 'error', text: lang === 'hi' ? 'संदेश भेजना विफल।' : 'Failed to send message.' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('grievanceiq_token');
    localStorage.removeItem('grievanceiq_user');
    window.location.href = '/login';
  };

  if (loading) return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '60vh', flexDirection: 'column', gap: '16px' }}>
      <div style={{ width: '48px', height: '48px', border: '4px solid #e2e8f0', borderTopColor: '#1e40af', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
      <p style={{ color: '#64748b', fontWeight: '600' }}>{lang === 'hi' ? 'अधिकारी कार्यक्षेत्र लोड हो रहा है...' : 'Loading Officer Workspace...'}</p>
    </div>
  );

  return (
    <div style={{ background: '#f1f5f9', minHeight: '100vh' }}>
      {/* Header */}
      <div style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%)', padding: '0 24px', borderBottom: '3px solid #c8a04a' }}>
        <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '64px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{ background: '#c8a04a', borderRadius: '8px', padding: '8px' }}>
              <Briefcase size={20} color="white" />
            </div>
            <div>
              <div style={{ color: 'white', fontWeight: '800', fontSize: '1rem', letterSpacing: '0.02em' }}>
                {t('officer_title')}
              </div>
              <div style={{ color: '#94a3b8', fontSize: '0.75rem' }}>
                {user?.full_name || t('officer_badge')} · {tDept(stats?.department) || stats?.department || 'Department'} · {user?.role?.toUpperCase() || 'STAFF'}
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            {/* Language Switcher */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(255,255,255,0.1)', padding: '5px 10px', borderRadius: '6px', border: '1px solid rgba(255,255,255,0.2)' }}>
              <Globe size={14} color="#c8a04a" />
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
              </select>
            </div>

            <button onClick={fetchData} style={{ background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: 'white', padding: '6px 14px', borderRadius: '6px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem' }}>
              <RefreshCw size={14} /> {t('refresh')}
            </button>
            <button onClick={handleLogout} style={{ background: 'rgba(220,38,38,0.15)', border: '1px solid rgba(220,38,38,0.4)', color: '#fca5a5', padding: '6px 14px', borderRadius: '6px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem' }}>
              <LogOut size={14} /> {t('nav_sign_out')}
            </button>
          </div>
        </div>
      </div>

      {/* KPI Stats Row */}
      {stats && (
        <div style={{ background: 'white', borderBottom: '1px solid #e2e8f0', padding: '16px 24px' }}>
          <div style={{ maxWidth: '1400px', margin: '0 auto', display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '16px' }}>
            {[
              { label: t('officer_stat_total'), value: stats.total_assigned, icon: <ClipboardList size={18} />, color: '#3b82f6' },
              { label: t('officer_stat_resolved'), value: stats.resolved, icon: <CheckCircle2 size={18} />, color: '#16a34a' },
              { label: t('officer_stat_pending'), value: stats.pending, icon: <Clock size={18} />, color: '#f59e0b' },
              { label: t('officer_stat_high_priority'), value: stats.high_priority_open, icon: <AlertTriangle size={18} />, color: '#dc2626' },
              { label: t('officer_stat_sla_breached'), value: stats.sla_breached, icon: <AlertCircle size={18} />, color: '#7c3aed' },
              { label: t('officer_stat_rate'), value: `${stats.resolution_rate_pct}%`, icon: <TrendingUp size={18} />, color: '#0284c7' },
            ].map((kpi, i) => (
              <div key={i} style={{ textAlign: 'center', padding: '12px', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                <div style={{ color: kpi.color, display: 'flex', justifyContent: 'center', marginBottom: '6px' }}>{kpi.icon}</div>
                <div style={{ fontSize: '1.5rem', fontWeight: '800', color: '#0f172a' }}>{kpi.value}</div>
                <div style={{ fontSize: '0.7rem', color: '#64748b', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{kpi.label}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Layout */}
      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '20px 24px', display: 'grid', gridTemplateColumns: '420px 1fr', gap: '20px' }}>

        {/* LEFT: Complaint Queue */}
        <div>
          <div style={{ background: 'white', borderRadius: '10px', border: '1px solid #e2e8f0', overflow: 'hidden' }}>
            {/* Filters */}
            <div style={{ padding: '14px 16px', borderBottom: '1px solid #e2e8f0', background: '#f8fafc' }}>
              <div style={{ fontWeight: '700', fontSize: '0.9rem', color: '#0f172a', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <ClipboardList size={16} color="#1e40af" /> {t('officer_queue_title')} ({filteredComplaints.length})
              </div>
              <input
                type="text"
                placeholder={t('officer_search_placeholder')}
                value={searchText}
                onChange={e => setSearchText(e.target.value)}
                style={{ width: '100%', padding: '7px 10px', border: '1px solid #d1d5db', borderRadius: '6px', fontSize: '0.82rem', marginBottom: '8px', boxSizing: 'border-box' }}
              />
              <div style={{ display: 'flex', gap: '8px' }}>
                <select value={filterStatus} onChange={e => setFilterStatus(e.target.value)} style={{ flex: 1, padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: '6px', fontSize: '0.8rem' }}>
                  <option value="all">{t('officer_filter_all_status')}</option>
                  <option value="open">{tStatus('open')}</option>
                  <option value="in_progress">{tStatus('in_progress')}</option>
                  <option value="escalated">{tStatus('escalated')}</option>
                  <option value="resolution_proposed">{tStatus('resolution_proposed')}</option>
                  <option value="resolved">{tStatus('resolved')}</option>
                </select>
                <select value={filterPriority} onChange={e => setFilterPriority(e.target.value)} style={{ flex: 1, padding: '6px 8px', border: '1px solid #d1d5db', borderRadius: '6px', fontSize: '0.8rem' }}>
                  <option value="all">{t('officer_filter_all_priority')}</option>
                  <option value="High">{tPriority('High')}</option>
                  <option value="Medium">{tPriority('Medium')}</option>
                  <option value="Low">{tPriority('Low')}</option>
                </select>
              </div>
            </div>

            {/* Complaint List */}
            <div style={{ maxHeight: 'calc(100vh - 280px)', overflowY: 'auto' }}>
              {filteredComplaints.length === 0 ? (
                <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>
                  <ClipboardList size={36} style={{ marginBottom: '10px', opacity: 0.4 }} />
                  <p style={{ fontWeight: '600' }}>{t('officer_no_cases')}</p>
                </div>
              ) : filteredComplaints.map(c => {
                const priority = PRIORITY_COLORS[c.priority] || PRIORITY_COLORS.Medium;
                const statusColor = STATUS_COLORS[c.status] || STATUS_COLORS.open;
                const isSelected = selectedComplaint?.token === c.token;
                return (
                  <div
                    key={c.token}
                    onClick={() => openComplaint(c)}
                    style={{
                      padding: '14px 16px', cursor: 'pointer', borderBottom: '1px solid #f1f5f9',
                      background: isSelected ? '#eff6ff' : 'white',
                      borderLeft: isSelected ? '3px solid #1e40af' : '3px solid transparent',
                      transition: 'all 0.15s'
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
                      <div style={{ fontWeight: '700', fontSize: '0.82rem', color: '#1e40af', fontFamily: 'monospace' }}>{c.token}</div>
                      <div style={{ display: 'flex', gap: '5px' }}>
                        <span style={{ fontSize: '0.7rem', fontWeight: '700', padding: '2px 8px', borderRadius: '999px', background: priority.bg, color: priority.text, border: `1px solid ${priority.border}` }}>
                          {tPriority(c.priority)}
                        </span>
                      </div>
                    </div>
                    <div style={{ fontSize: '0.78rem', color: '#374151', fontWeight: '600', marginBottom: '4px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {c.service_type}
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#6b7280', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', marginBottom: '6px' }}>
                      {c.description?.slice(0, 80)}...
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '0.7rem', color: '#64748b' }}>
                        <User size={10} style={{ marginRight: '3px', verticalAlign: 'middle' }} />
                        {c.customer_name}
                      </span>
                      <span style={{ fontSize: '0.7rem', fontWeight: '700', padding: '2px 8px', borderRadius: '999px', background: statusColor.bg, color: statusColor.color }}>
                        {tStatus(c.status)}
                      </span>
                    </div>
                    {c.sla?.overdue && (
                      <div style={{ marginTop: '4px', fontSize: '0.68rem', color: '#dc2626', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <AlertTriangle size={10} /> {lang === 'hi' ? 'समय-सीमा का उल्लंघन (SLA Breached)' : 'SLA Breached'}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* RIGHT: Complaint Detail Panel */}
        <div>
          {!selectedComplaint ? (
            <div style={{ background: 'white', borderRadius: '10px', border: '1px solid #e2e8f0', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', gap: '16px', color: '#94a3b8', padding: '60px' }}>
              <FileBadge size={56} style={{ opacity: 0.3 }} />
              <p style={{ fontWeight: '700', fontSize: '1.1rem' }}>{lang === 'hi' ? 'कतार से एक शिकायत चुनें' : 'Select a case from the queue'}</p>
              <p style={{ fontSize: '0.85rem', textAlign: 'center', maxWidth: '340px' }}>
                {t('officer_select_case_prompt')}
              </p>
            </div>
          ) : (
            <div style={{ background: 'white', borderRadius: '10px', border: '1px solid #e2e8f0', overflow: 'hidden' }}>
              {/* Case Header */}
              <div style={{ padding: '18px 20px', background: 'linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%)', color: 'white' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ fontFamily: 'monospace', fontSize: '1.1rem', fontWeight: '800', color: '#c8a04a' }}>{selectedComplaint.token}</div>
                    <div style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '2px' }}>{selectedComplaint.service_type} · {selectedComplaint.company_name}</div>
                  </div>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    {(() => {
                      const priority = PRIORITY_COLORS[selectedComplaint.priority] || PRIORITY_COLORS.Medium;
                      const statusColor = STATUS_COLORS[selectedComplaint.status] || STATUS_COLORS.open;
                      return (
                        <>
                          <span style={{ fontSize: '0.75rem', fontWeight: '700', padding: '4px 12px', borderRadius: '999px', background: priority.bg, color: priority.text }}>
                            {tPriority(selectedComplaint.priority)}
                          </span>
                          <span style={{ fontSize: '0.75rem', fontWeight: '700', padding: '4px 12px', borderRadius: '999px', background: statusColor.bg, color: statusColor.color }}>
                            {tStatus(selectedComplaint.status)}
                          </span>
                        </>
                      );
                    })()}
                  </div>
                </div>
              </div>

              {/* Action Alert */}
              {actionMsg && (
                <div style={{ padding: '10px 20px', background: actionMsg.type === 'success' ? '#f0fdf4' : '#fef2f2', borderBottom: `1px solid ${actionMsg.type === 'success' ? '#bbf7d0' : '#fecaca'}` }}>
                  <div style={{ color: actionMsg.type === 'success' ? '#166534' : '#991b1b', fontSize: '0.82rem', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '6px' }}>
                    {actionMsg.type === 'success' ? <CheckCircle2 size={14} /> : <AlertCircle size={14} />}
                    {actionMsg.text}
                  </div>
                </div>
              )}

              {/* Tabs */}
              <div style={{ display: 'flex', borderBottom: '2px solid #e2e8f0', background: '#f8fafc' }}>
                {[
                  { id: 'details', label: t('officer_tab_details'), icon: <Eye size={14} /> },
                  { id: 'notes', label: t('officer_tab_notes'), icon: <FileText size={14} /> },
                  { id: 'resolve', label: t('officer_tab_resolve'), icon: <CheckCircle2 size={14} /> },
                  { id: 'messages', label: t('officer_tab_messages'), icon: <MessageSquare size={14} /> },
                ].map(tab => (
                  <button
                    key={tab.id}
                    onClick={() => { setActiveTab(tab.id); setActionMsg(null); }}
                    style={{
                      flex: 1, padding: '12px 8px', border: 'none', borderBottom: activeTab === tab.id ? '2px solid #1e40af' : '2px solid transparent',
                      background: activeTab === tab.id ? 'white' : 'transparent',
                      color: activeTab === tab.id ? '#1e40af' : '#64748b',
                      fontWeight: activeTab === tab.id ? '700' : '500',
                      fontSize: '0.78rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '5px',
                      marginBottom: '-2px', transition: 'all 0.15s'
                    }}
                  >
                    {tab.icon} {tab.label}
                  </button>
                ))}
              </div>

              {/* Tab Content */}
              <div style={{ padding: '20px', maxHeight: 'calc(100vh - 380px)', overflowY: 'auto' }}>
                {/* DETAILS TAB */}
                {activeTab === 'details' && (
                  <div>
                    {/* Customer Info */}
                    <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '14px', marginBottom: '16px' }}>
                      <div style={{ fontWeight: '700', fontSize: '0.82rem', color: '#374151', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        {lang === 'hi' ? 'ग्राहक जानकारी' : 'Customer Information'}
                      </div>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 20px', fontSize: '0.82rem' }}>
                        <div><span style={{ color: '#64748b' }}>{t('officer_customer')}:</span> <strong>{selectedComplaint.customer_name}</strong></div>
                        <div><span style={{ color: '#64748b' }}>Email:</span> <strong>{selectedComplaint.customer_email || 'N/A'}</strong></div>
                        <div><span style={{ color: '#64748b' }}>{lang === 'hi' ? 'दर्ज तिथि:' : 'Filed:'}</span> <strong>{new Date(selectedComplaint.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</strong></div>
                        <div><span style={{ color: '#64748b' }}>{t('officer_bank')}:</span> <strong>{selectedComplaint.company_name}</strong></div>
                      </div>
                    </div>

                    {/* Complaint Fields */}
                    <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '14px', marginBottom: '16px' }}>
                      <div style={{ fontWeight: '700', fontSize: '0.82rem', color: '#374151', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        {t('officer_details_label')}
                      </div>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px 20px', fontSize: '0.82rem', marginBottom: '10px' }}>
                        {selectedComplaint.amount && <div><span style={{ color: '#64748b' }}>{t('officer_txn_amount')}:</span> <strong>₹{Number(selectedComplaint.amount).toLocaleString('en-IN')}</strong></div>}
                        {selectedComplaint.reference_id && <div><span style={{ color: '#64748b' }}>{t('officer_ref_id')}:</span> <strong style={{ fontFamily: 'monospace' }}>{selectedComplaint.reference_id}</strong></div>}
                        {selectedComplaint.transaction_date && <div><span style={{ color: '#64748b' }}>{t('officer_txn_date')}:</span> <strong>{selectedComplaint.transaction_date}</strong></div>}
                        {selectedComplaint.branch && <div><span style={{ color: '#64748b' }}>{lang === 'hi' ? 'शाखा:' : 'Branch:'}</span> <strong>{selectedComplaint.branch}</strong></div>}
                      </div>
                      <div style={{ fontSize: '0.82rem', color: '#374151', lineHeight: '1.5', background: 'white', padding: '10px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                        {selectedComplaint.description}
                      </div>
                    </div>

                    {/* Evidence Status */}
                    <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '14px', marginBottom: '16px' }}>
                      <div style={{ fontWeight: '700', fontSize: '0.82rem', color: '#374151', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.05em', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Shield size={14} /> {t('officer_attached_doc')}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
                        {selectedComplaint.proof_file_path ? (
                          <>
                            <a href={`http://localhost:8000/api/complaints/${selectedComplaint.token}/document`} target="_blank" rel="noreferrer"
                              style={{ fontSize: '0.8rem', color: '#1e40af', textDecoration: 'underline', display: 'flex', alignItems: 'center', gap: '4px' }}>
                              <FileText size={14} /> {t('officer_view_doc')}
                            </a>
                            <span style={{
                              fontSize: '0.75rem', fontWeight: '700', padding: '3px 10px', borderRadius: '999px',
                              background: selectedComplaint.evidence_status === 'VERIFIED' ? '#dcfce7' : selectedComplaint.evidence_status === 'REJECTED' ? '#fee2e2' : '#fffbeb',
                              color: selectedComplaint.evidence_status === 'VERIFIED' ? '#166534' : selectedComplaint.evidence_status === 'REJECTED' ? '#991b1b' : '#92400e',
                            }}>
                              {selectedComplaint.evidence_status || 'PENDING'}
                            </span>
                            {selectedComplaint.evidence_status !== 'VERIFIED' && (
                              <div style={{ display: 'flex', gap: '8px' }}>
                                <button onClick={() => handleVerifyEvidence('VERIFIED')} disabled={actionLoading}
                                  style={{ padding: '5px 12px', background: '#16a34a', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '0.78rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                  <CheckCircle2 size={12} /> {t('officer_ai_accept')}
                                </button>
                                <button onClick={() => handleVerifyEvidence('REJECTED')} disabled={actionLoading}
                                  style={{ padding: '5px 12px', background: '#dc2626', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '0.78rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                  <XCircle size={12} /> {t('officer_ai_reject')}
                                </button>
                              </div>
                            )}
                          </>
                        ) : (
                          <span style={{ fontSize: '0.8rem', color: '#64748b' }}>{lang === 'hi' ? 'ग्राहक द्वारा कोई दस्तावेज़ अपलोड नहीं किया गया।' : 'No document attached by customer.'}</span>
                        )}
                      </div>
                      {selectedComplaint.evidence_rejection_reason && (
                        <div style={{ marginTop: '8px', fontSize: '0.78rem', color: '#991b1b', background: '#fee2e2', padding: '6px 10px', borderRadius: '4px' }}>
                          {lang === 'hi' ? 'अस्वीकृति का कारण: ' : 'Rejection reason: '}{selectedComplaint.evidence_rejection_reason}
                        </div>
                      )}

                      {/* AI Evidence Confidence Score */}
                      {selectedComplaint.proof_file_path && (
                        <div style={{ marginTop: '14px' }}>
                          <button
                            onClick={runEvidenceAIAnalysis}
                            disabled={evidenceAnalysisLoading}
                            style={{ padding: '6px 14px', background: '#4f46e5', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontSize: '0.78rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '6px', opacity: evidenceAnalysisLoading ? 0.7 : 1 }}
                          >
                            <Eye size={13} />
                            {evidenceAnalysisLoading ? (lang === 'hi' ? 'दस्तावेज़ का विश्लेषण जारी...' : 'Analysing Document...') : t('officer_ai_run_analysis')}
                          </button>

                          {evidenceAnalysis && !evidenceAnalysis.error && (
                            <div style={{ marginTop: '12px', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '14px', fontSize: '0.82rem' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                                <div>
                                  <div style={{ fontSize: '0.72rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{t('officer_ai_confidence')}</div>
                                  <div style={{ fontSize: '1.6rem', fontWeight: '900', color: evidenceAnalysis.confidence_color, lineHeight: 1.2 }}>
                                    {evidenceAnalysis.confidence_score}<span style={{ fontSize: '0.9rem', fontWeight: '500' }}>/100</span>
                                  </div>
                                </div>
                                <div style={{ background: evidenceAnalysis.confidence_color, color: 'white', padding: '6px 14px', borderRadius: '8px', fontWeight: '800', fontSize: '0.78rem', letterSpacing: '0.04em', textAlign: 'center' }}>
                                  {evidenceAnalysis.confidence_label}<br />
                                  <span style={{ fontWeight: '500', fontSize: '0.72rem' }}>{evidenceAnalysis.auto_verdict}</span>
                                </div>
                              </div>
                              <div style={{ background: '#e2e8f0', borderRadius: '4px', height: '7px', overflow: 'hidden', marginBottom: '10px' }}>
                                <div style={{ width: `${evidenceAnalysis.confidence_score}%`, height: '100%', background: evidenceAnalysis.confidence_color, borderRadius: '4px', transition: 'width 0.6s' }} />
                              </div>
                              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', marginBottom: '10px' }}>
                                {[
                                  [lang === 'hi' ? 'फ़ाइल प्रकार' : 'File Type', evidenceAnalysis.score_breakdown?.file_type, 25],
                                  [lang === 'hi' ? 'कीवर्ड मिलान' : 'Keyword Match', evidenceAnalysis.score_breakdown?.keyword_match, 40],
                                  [lang === 'hi' ? 'समानता स्कोर' : 'Semantic Similarity', evidenceAnalysis.score_breakdown?.semantic_similarity, 25],
                                  [lang === 'hi' ? 'पठनीयता बोनस' : 'Readable Bonus', evidenceAnalysis.score_breakdown?.ocr_readable_bonus, 10],
                                ].map(([lbl, val, max]) => (
                                  <div key={lbl} style={{ background: 'white', border: '1px solid #e2e8f0', borderRadius: '6px', padding: '6px 10px' }}>
                                    <div style={{ color: '#94a3b8', fontSize: '0.7rem' }}>{lbl}</div>
                                    <div style={{ fontWeight: '700', color: '#1e293b', fontSize: '0.9rem' }}>{val ?? '-'}<span style={{ color: '#94a3b8', fontSize: '0.72rem' }}>/{max}</span></div>
                                  </div>
                                ))}
                              </div>
                              {evidenceAnalysis.analysis?.matched_keywords?.length > 0 && (
                                <div style={{ marginBottom: '8px' }}>
                                  <span style={{ color: '#64748b', fontSize: '0.72rem' }}>{lang === 'hi' ? 'पहचाने गए कीवर्ड्स: ' : 'Matched Keywords: '}</span>
                                  {evidenceAnalysis.analysis.matched_keywords.map(kw => (
                                    <span key={kw} style={{ background: '#dcfce7', color: '#166534', fontSize: '0.7rem', padding: '2px 7px', borderRadius: '999px', marginRight: '4px', fontWeight: '600' }}>{kw}</span>
                                  ))}
                                </div>
                              )}
                              <div style={{ background: '#f0f9ff', border: '1px solid #bae6fd', borderRadius: '6px', padding: '8px 10px', color: '#0c4a6e', fontSize: '0.78rem' }}>
                                <strong>{t('officer_ai_recommendation')}:</strong> {evidenceAnalysis.recommendation}
                              </div>
                            </div>
                          )}
                          {evidenceAnalysis?.error && (
                            <div style={{ marginTop: '8px', color: '#dc2626', fontSize: '0.78rem' }}>
                              {lang === 'hi' ? 'विश्लेषण विफल: ' : 'Analysis failed: '}{evidenceAnalysis.error}
                            </div>
                          )}
                        </div>
                      )}
                    </div>

                    {/* SLA Info */}
                    {selectedComplaint.sla && (
                      <div style={{ background: selectedComplaint.sla.overdue ? '#fef2f2' : '#eff6ff', border: `1px solid ${selectedComplaint.sla.overdue ? '#fecaca' : '#bfdbfe'}`, borderRadius: '8px', padding: '10px 14px', fontSize: '0.8rem' }}>
                        <strong style={{ color: selectedComplaint.sla.overdue ? '#b91c1c' : '#1e40af' }}>
                          {selectedComplaint.sla.overdue ? '⚠ SLA BREACHED' : `⏱ ${t('officer_sla_deadline')}:`}
                        </strong>
                        <span style={{ color: '#374151', marginLeft: '8px' }}>{selectedComplaint.sla.message || 'No deadline set'}</span>
                      </div>
                    )}
                  </div>
                )}

                {/* INVESTIGATION NOTES TAB */}
                {activeTab === 'notes' && (
                  <div>
                    <div style={{ marginBottom: '16px' }}>
                      <label style={{ display: 'block', fontWeight: '700', fontSize: '0.82rem', color: '#374151', marginBottom: '6px' }}>
                        {t('officer_notes_add')}
                      </label>
                      <textarea
                        value={noteText}
                        onChange={e => setNoteText(e.target.value)}
                        rows={4}
                        placeholder={lang === 'hi' ? 'अपनी जांच के निष्कर्ष, की गई कार्रवाई और टिप्पणियां यहाँ लिखें...' : 'Document your investigation findings, actions taken, observations...'}
                        style={{ width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '6px', fontSize: '0.82rem', resize: 'vertical', boxSizing: 'border-box' }}
                      />
                      <button onClick={handleAddNote} disabled={actionLoading || !noteText.trim()}
                        style={{ marginTop: '8px', padding: '8px 18px', background: '#1e40af', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: '700', fontSize: '0.82rem' }}>
                        {t('officer_notes_save')}
                      </button>
                    </div>

                    <div style={{ fontWeight: '700', fontSize: '0.82rem', color: '#374151', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      {lang === 'hi' ? 'जांच इतिहास' : 'Investigation History'}
                    </div>
                    {notes.length === 0 ? (
                      <div style={{ color: '#94a3b8', fontSize: '0.82rem', fontStyle: 'italic' }}>{lang === 'hi' ? 'अभी तक कोई जांच नोट नहीं है।' : 'No investigation notes yet.'}</div>
                    ) : notes.map(note => (
                      <div key={note.note_id} style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '12px', marginBottom: '10px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                          <strong style={{ fontSize: '0.82rem', color: '#0f172a' }}>{note.worker_name}</strong>
                          <span style={{ fontSize: '0.75rem', color: '#64748b' }}>{new Date(note.created_at).toLocaleString('en-IN')}</span>
                        </div>
                        <p style={{ fontSize: '0.82rem', color: '#374151', lineHeight: '1.5', margin: 0 }}>{note.note_text}</p>
                      </div>
                    ))}
                  </div>
                )}

                {/* RESOLUTION TAB */}
                {activeTab === 'resolve' && (
                  <div>
                    {['resolved', 'closed'].includes(selectedComplaint.status) ? (
                      <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '20px', textAlign: 'center' }}>
                        <CheckCircle2 size={32} color="#16a34a" style={{ marginBottom: '10px' }} />
                        <div style={{ fontWeight: '700', color: '#166534', marginBottom: '6px' }}>{lang === 'hi' ? 'यह शिकायत पहले ही हल हो चुकी है।' : 'This case is already resolved.'}</div>
                        <div style={{ fontSize: '0.82rem', color: '#374151' }}>{selectedComplaint.resolution_notes}</div>
                      </div>
                    ) : (
                      <div>
                        <div style={{ fontWeight: '700', fontSize: '0.85rem', color: '#0f172a', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <CheckCircle2 size={16} color="#1e40af" /> {t('officer_tab_resolve')}
                        </div>

                        <div style={{ marginBottom: '12px' }}>
                          <label style={{ display: 'block', fontWeight: '600', fontSize: '0.82rem', color: '#374151', marginBottom: '4px' }}>{t('officer_res_type')}</label>
                          <select value={resolutionForm.resolution_type} onChange={e => setResolutionForm({ ...resolutionForm, resolution_type: e.target.value })}
                            style={{ width: '100%', padding: '8px 10px', border: '1px solid #d1d5db', borderRadius: '6px', fontSize: '0.82rem' }}>
                            <option value="FULL_REFUND">{lang === 'hi' ? 'पूर्ण रिफंड स्वीकृत (Full Refund)' : 'Full Refund Processed'}</option>
                            <option value="PARTIAL_REFUND">{lang === 'hi' ? 'आंशिक रिफंड स्वीकृत (Partial Refund)' : 'Partial Refund Processed'}</option>
                            <option value="ACCOUNT_CORRECTED">{lang === 'hi' ? 'खाता / रिकॉर्ड सही किया गया' : 'Account / Record Corrected'}</option>
                            <option value="CARD_BLOCKED_REPLACED">{lang === 'hi' ? 'कार्ड ब्लॉक एवं नया प्रेषित' : 'Card Blocked & Replacement Dispatched'}</option>
                            <option value="KYC_UPDATED">{lang === 'hi' ? 'केवाईसी / दस्तावेज अद्यतन' : 'KYC / Documentation Updated'}</option>
                            <option value="CIBIL_RECTIFICATION">{lang === 'hi' ? 'सिबिल ब्यूरो सुधार प्रेषित' : 'CIBIL Bureau Rectification Submitted'}</option>
                            <option value="LOAN_NOC_ISSUED">{lang === 'hi' ? 'ऋण एनओसी जारी की गई' : 'Loan NOC / Foreclosure Certificate Issued'}</option>
                            <option value="COMPLAINT_REGISTERED">{lang === 'hi' ? 'नोडल स्तर पर औपचारिक मामला पंजीकृत' : 'Formal Complaint Registered with Nodal'}</option>
                            <option value="TECHNICAL_ISSUE_FIXED">{lang === 'hi' ? 'तकनीकी खामी ठीक की गई' : 'Technical / System Issue Resolved'}</option>
                            <option value="NO_MERIT">{lang === 'hi' ? 'जांच उपरांत शिकायत आधारहीन पाई गई' : 'Complaint Investigated - No Merit Found'}</option>
                            <option value="ESCALATED_TO_NODAL">{lang === 'hi' ? 'नोडल अधिकारी को अग्रेषित' : 'Escalated to Nodal Officer'}</option>
                          </select>
                        </div>

                        <div style={{ marginBottom: '12px' }}>
                          <label style={{ display: 'block', fontWeight: '600', fontSize: '0.82rem', color: '#374151', marginBottom: '4px' }}>{t('officer_res_details')}</label>
                          <textarea
                            value={resolutionForm.resolution_details}
                            onChange={e => setResolutionForm({ ...resolutionForm, resolution_details: e.target.value })}
                            rows={5}
                            placeholder={lang === 'hi' ? 'वैधानिक संदर्भ, उठाए गए कदम और परिणाम के साथ औपचारिक समाधान विवरण यहाँ लिखें...' : 'Write formal resolution details with regulatory references, steps taken, and outcome...'}
                            style={{ width: '100%', padding: '10px', border: '1px solid #d1d5db', borderRadius: '6px', fontSize: '0.82rem', resize: 'vertical', boxSizing: 'border-box' }}
                          />
                        </div>

                        {/* DYNAMIC FORM CONTEXT: Card Blocking & Security Operations vs Monetary Refund */}
                        {resolutionForm.resolution_type === 'CARD_BLOCKED_REPLACED' || (selectedComplaint?.service_type || '').toLowerCase().includes('card') && !resolutionForm.resolution_type.includes('REFUND') ? (
                          <div style={{ background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '14px', marginBottom: '16px' }}>
                            <div style={{ fontWeight: '700', fontSize: '0.85rem', color: '#166534', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                              <span>🛡️ Emergency Card Security & Action Dispatch</span>
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '8px' }}>
                              <div>
                                <label style={{ display: 'block', fontWeight: '600', fontSize: '0.8rem', color: '#374151', marginBottom: '4px' }}>
                                  Switch Blocking Auth Code / Hotlist Ref *
                                </label>
                                <input type="text" value={resolutionForm.transaction_reference} onChange={e => setResolutionForm({ ...resolutionForm, transaction_reference: e.target.value })}
                                  placeholder="e.g. BLK-SWITCH-HOST-98214"
                                  style={{ width: '100%', padding: '8px 10px', border: '1px solid #86efac', borderRadius: '6px', fontSize: '0.82rem', boxSizing: 'border-box' }} />
                              </div>
                              <div>
                                <label style={{ display: 'block', fontWeight: '600', fontSize: '0.8rem', color: '#374151', marginBottom: '4px' }}>
                                  Replacement Card Courier Tracking No
                                </label>
                                <input type="text" placeholder="e.g. BLUEDART-AWB-440192"
                                  style={{ width: '100%', padding: '8px 10px', border: '1px solid #86efac', borderRadius: '6px', fontSize: '0.82rem', boxSizing: 'border-box' }} />
                              </div>
                            </div>
                            <div style={{ fontSize: '0.75rem', color: '#15803d', marginTop: '4px' }}>
                              ✅ Payment / Refund amount is not applicable for Card Deactivation. Host switch will instantly hotlist card globally across ATM, POS, and E-Commerce channels.
                            </div>
                          </div>
                        ) : resolutionForm.resolution_type === 'KYC_UPDATED' || resolutionForm.resolution_type === 'LOAN_NOC_ISSUED' || resolutionForm.resolution_type === 'CIBIL_RECTIFICATION' ? (
                          <div style={{ background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '14px', marginBottom: '16px' }}>
                            <div style={{ fontWeight: '700', fontSize: '0.85rem', color: '#1e3a8a', marginBottom: '10px' }}>
                              📋 Administrative Service Fulfillment
                            </div>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
                              <div>
                                <label style={{ display: 'block', fontWeight: '600', fontSize: '0.8rem', color: '#374151', marginBottom: '4px' }}>
                                  Administrative Reference / NOC Serial No
                                </label>
                                <input type="text" value={resolutionForm.transaction_reference} onChange={e => setResolutionForm({ ...resolutionForm, transaction_reference: e.target.value })}
                                  placeholder="e.g. NOC-LN-2026-98124"
                                  style={{ width: '100%', padding: '8px 10px', border: '1px solid #d1d5db', borderRadius: '6px', fontSize: '0.82rem', boxSizing: 'border-box' }} />
                              </div>
                              <div>
                                <label style={{ display: 'block', fontWeight: '600', fontSize: '0.8rem', color: '#374151', marginBottom: '4px' }}>
                                  Upload Fulfillment Certificate (PDF / NOC)
                                </label>
                                <input type="file" accept=".pdf,.jpg,.jpeg,.png,.txt"
                                  onChange={e => setResolutionFile(e.target.files?.[0] || null)}
                                  style={{ width: '100%', padding: '6px', border: '1px solid #d1d5db', borderRadius: '6px', fontSize: '0.82rem' }} />
                              </div>
                            </div>
                          </div>
                        ) : (
                          /* Monetary Refund Form (UPI, ATM Failure, Duplicate Charges) */
                          <>
                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                              <div>
                                <label style={{ display: 'block', fontWeight: '600', fontSize: '0.82rem', color: '#374151', marginBottom: '4px' }}>{t('officer_res_ref')}</label>
                                <input type="text" value={resolutionForm.transaction_reference} onChange={e => setResolutionForm({ ...resolutionForm, transaction_reference: e.target.value })}
                                  placeholder="e.g. REFUND-TXN-20261011"
                                  style={{ width: '100%', padding: '8px 10px', border: '1px solid #d1d5db', borderRadius: '6px', fontSize: '0.82rem', boxSizing: 'border-box' }} />
                              </div>
                              <div>
                                <label style={{ display: 'block', fontWeight: '600', fontSize: '0.82rem', color: '#374151', marginBottom: '4px' }}>{t('officer_res_amount')}</label>
                                <input type="number" value={resolutionForm.resolved_amount} onChange={e => setResolutionForm({ ...resolutionForm, resolved_amount: e.target.value })}
                                  placeholder="0.00"
                                  style={{ width: '100%', padding: '8px 10px', border: '1px solid #d1d5db', borderRadius: '6px', fontSize: '0.82rem', boxSizing: 'border-box' }} />
                              </div>
                            </div>

                            <div style={{ marginBottom: '16px' }}>
                              <label style={{ display: 'block', fontWeight: '600', fontSize: '0.82rem', color: '#374151', marginBottom: '4px' }}>
                                <Upload size={14} style={{ verticalAlign: 'middle', marginRight: '4px' }} /> {t('officer_res_letter')}
                              </label>
                              <input type="file" accept=".pdf,.jpg,.jpeg,.png,.txt"
                                onChange={e => setResolutionFile(e.target.files?.[0] || null)}
                                style={{ width: '100%', padding: '6px', border: '1px solid #d1d5db', borderRadius: '6px', fontSize: '0.82rem' }} />
                              <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '4px' }}>
                                {lang === 'hi' ? 'मान्य प्रारूप: PDF, JPG, PNG, TXT। यह प्रमाण ग्राहक द्वारा डाउनलोड किया जा सकेगा।' : 'Accepted: PDF, JPG, PNG, TXT. This proof will be downloadable by the customer.'}
                              </div>
                            </div>
                          </>
                        )}

                        <button onClick={handleSubmitResolution} disabled={actionLoading}
                          style={{ width: '100%', padding: '12px', background: actionLoading ? '#94a3b8' : 'linear-gradient(135deg, #1e40af, #1d4ed8)', color: 'white', border: 'none', borderRadius: '8px', cursor: actionLoading ? 'not-allowed' : 'pointer', fontWeight: '700', fontSize: '0.9rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                          {actionLoading ? <><RefreshCw size={16} /> {lang === 'hi' ? 'प्रस्तुत किया जा रहा है...' : 'Submitting...'}</> : <><Send size={16} /> {t('officer_res_submit')}</>}
                        </button>
                        <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '8px', textAlign: 'center' }}>
                          {lang === 'hi' ? 'यह समाधान ग्राहक को पुष्टि हेतु भेजा जाएगा। वे इसे स्वीकार कर सकते हैं या पुनः खोल सकते हैं।' : 'The resolution will be sent to the customer for confirmation. They can accept or reopen the case.'}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* MESSAGES TAB */}
                {activeTab === 'messages' && (
                  <div>
                    <div style={{ maxHeight: '320px', overflowY: 'auto', marginBottom: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {messages.length === 0 ? (
                        <div style={{ color: '#94a3b8', fontSize: '0.82rem', fontStyle: 'italic', textAlign: 'center', padding: '20px' }}>
                          {lang === 'hi' ? 'अभी तक कोई संदेश नहीं है। ग्राहक के साथ संवाद शुरू करें।' : 'No messages yet. Start communication with the customer.'}
                        </div>
                      ) : messages.map(m => (
                        <div key={m.message_id} style={{
                          padding: '10px 12px', borderRadius: '8px', maxWidth: '85%',
                          alignSelf: m.sender_type === 'officer' ? 'flex-end' : 'flex-start',
                          background: m.sender_type === 'officer' ? '#1e40af' : '#f1f5f9',
                          color: m.sender_type === 'officer' ? 'white' : '#374151',
                        }}>
                          <div style={{ fontSize: '0.7rem', fontWeight: '700', marginBottom: '4px', opacity: 0.8 }}>{m.sender_name}</div>
                          <div style={{ fontSize: '0.82rem' }}>{m.message_text}</div>
                          <div style={{ fontSize: '0.68rem', opacity: 0.6, marginTop: '4px' }}>{new Date(m.created_at).toLocaleString('en-IN')}</div>
                        </div>
                      ))}
                    </div>

                    <div style={{ display: 'flex', gap: '8px' }}>
                      <textarea
                        value={newMessage}
                        onChange={e => setNewMessage(e.target.value)}
                        rows={2}
                        placeholder={t('officer_msg_placeholder')}
                        style={{ flex: 1, padding: '8px 10px', border: '1px solid #d1d5db', borderRadius: '6px', fontSize: '0.82rem', resize: 'none' }}
                        onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSendMessage(); } }}
                      />
                      <button onClick={handleSendMessage} disabled={actionLoading || !newMessage.trim()}
                        style={{ padding: '8px 16px', background: '#1e40af', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.82rem' }}>
                        <Send size={14} /> {t('officer_msg_send')}
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
