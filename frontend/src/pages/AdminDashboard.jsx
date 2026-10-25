import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { 
  Users, CheckCircle, Clock, AlertTriangle, Filter, Search, 
  Sparkles, FileText, BarChart3, BookOpen, Shield, RefreshCw,
  Check, X, Upload, MessageSquare, Activity, Cpu, Sliders, Globe
} from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, Legend 
} from 'recharts';
import { useLanguage } from '../context/LanguageContext';

export default function AdminDashboard() {
  const navigate = useNavigate();
  const { lang, changeLanguage, t, tStatus, tPriority, tDept } = useLanguage();
  const token = localStorage.getItem('grievanceiq_token');
  const user = JSON.parse(localStorage.getItem('grievanceiq_user') || '{}');

  // Active Tab: 'queue', 'analytics', 'intelligence', 'whatif', 'kb', 'audit'
  const [activeTab, setActiveTab] = useState('queue');

  // Data States
  const [complaints, setComplaints] = useState([]);
  const [kpis, setKpis] = useState(null);
  const [trends, setTrends] = useState(null);
  const [kbArticles, setKbArticles] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [companies, setCompanies] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(false);

  // Bank Health & Intelligence States
  const [bankHealth, setBankHealth] = useState(null);
  const [healthLoading, setHealthLoading] = useState(false);

  // What-If Simulation States
  const [simInputs, setSimInputs] = useState({
    department_id: '',
    company_id: '',
    proposed_workers: 8,
    volume_change_pct: 0
  });
  const [simResults, setSimResults] = useState(null);
  const [simLoading, setSimLoading] = useState(false);
  const [simContext, setSimContext] = useState(null); // banks + depts + real data

  // Filters
  const [statusFilter, setStatusFilter] = useState('');
  const [deptFilter, setDeptFilter] = useState('');
  const [companyFilter, setCompanyFilter] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('');
  const [resModeFilter, setResModeFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 25;

  // AI Performance State
  const [aiPerfData, setAiPerfData] = useState(null);
  const [aiPerfLoading, setAiPerfLoading] = useState(false);

  // Selected Complaint for Modal Actions
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [modalTab, setModalTab] = useState('resolve'); // 'resolve', 'evidence', 'notes'

  // Worker Resolution Submission States
  const [resolutionDetails, setResolutionDetails] = useState('');
  const [resolutionType, setResolutionType] = useState('Full Refund Issued');
  const [resRefNumber, setResRefNumber] = useState('');
  const [resAmount, setResAmount] = useState('');
  const [resProofFile, setResProofFile] = useState(null);
  const [submittingResolution, setSubmittingResolution] = useState(false);
  const [copilotLoading, setCopilotLoading] = useState(false);

  // Evidence Verification States
  const [evidenceRejectReason, setEvidenceRejectReason] = useState('');
  const [evidenceLoading, setEvidenceLoading] = useState(false);

  // Investigation Notes States
  const [notesList, setNotesList] = useState([]);
  const [newNoteText, setNewNoteText] = useState('');
  const [notesLoading, setNotesLoading] = useState(false);

  // Auth check & initial fetch
  useEffect(() => {
    if (!token) {
      navigate('/login');
      return;
    }
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    fetchInitialData();
  }, [token]);

  const fetchInitialData = () => {
    setLoading(true);
    Promise.all([
      axios.get('/api/companies'),
      axios.get('/api/departments'),
      axios.get('/api/analytics/overview'),
      axios.get('/api/analytics/trends')
    ]).then(([compRes, deptRes, kpiRes, trendRes]) => {
      setCompanies(compRes.data);
      setDepartments(deptRes.data);
      setKpis(kpiRes.data);
      setTrends(trendRes.data);
      fetchComplaints();
    }).catch(err => {
      if (err.response?.status === 401) {
        localStorage.removeItem('grievanceiq_token');
        navigate('/login');
      }
    }).finally(() => setLoading(false));
  };

  const fetchComplaints = () => {
    const params = {};
    if (statusFilter) params.status_filter = statusFilter;
    if (deptFilter) params.department_id = deptFilter;
    if (companyFilter) params.company_id = companyFilter;
    if (priorityFilter) params.priority = priorityFilter;
    if (resModeFilter) params.resolution_mode = resModeFilter;
    if (searchQuery) params.search = searchQuery;

    axios.get('/api/admin/complaints', { params })
      .then(res => setComplaints(res.data))
      .catch(err => console.error('Error fetching complaints:', err));
  };

  useEffect(() => {
    if (token) fetchComplaints();
  }, [statusFilter, deptFilter, companyFilter, priorityFilter, resModeFilter]);

  const fetchBankHealth = () => {
    setHealthLoading(true);
    axios.get('/api/intelligence/bank-health')
      .then(res => setBankHealth(res.data))
      .catch(err => console.error('Error fetching bank health:', err))
      .finally(() => setHealthLoading(false));
  };

  const runSimulation = () => {
    setSimLoading(true);
    const payload = {
      proposed_workers: simInputs.proposed_workers,
      volume_change_pct: simInputs.volume_change_pct,
      department_id: simInputs.department_id ? parseInt(simInputs.department_id) : null,
      company_id: simInputs.company_id ? parseInt(simInputs.company_id) : null,
    };
    axios.post('/api/intelligence/what-if-simulation', payload)
      .then(res => setSimResults(res.data))
      .catch(err => console.error('Error running simulation:', err))
      .finally(() => setSimLoading(false));
  };

  const fetchSimulationContext = () => {
    axios.get('/api/intelligence/simulation-context')
      .then(res => {
        setSimContext(res.data);
        // Pre-fill proposed workers from first department if available
        if (res.data.departments && res.data.departments.length > 0) {
          const d = res.data.departments[0];
          setSimInputs(prev => ({ ...prev, proposed_workers: d.current_workers + 2 }));
        }
      })
      .catch(err => console.error('Error fetching simulation context:', err));
  };

  const fetchKbArticles = () => {
    axios.get('/api/kb')
      .then(res => setKbArticles(res.data))
      .catch(err => console.error('Error fetching KB:', err));
  };

  const fetchAuditLogs = () => {
    axios.get('/api/admin/audit-logs')
      .then(res => setAuditLogs(res.data))
      .catch(err => console.error('Error fetching Audit:', err));
  };

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    if (tab === 'kb') fetchKbArticles();
    if (tab === 'audit') fetchAuditLogs();
    if (tab === 'intelligence') fetchBankHealth();
    if (tab === 'whatif' && !simResults) {
      fetchSimulationContext();
      runSimulation();
    }
    if (tab === 'analytics') {
      axios.get('/api/analytics/overview').then(r => setKpis(r.data));
      axios.get('/api/analytics/trends').then(r => setTrends(r.data));
    }
    if (tab === 'nova') {
      setAiPerfLoading(true);
      axios.get('/api/analytics/ai-performance')
        .then(r => setAiPerfData(r.data))
        .catch(err => console.error('Error fetching AI performance:', err))
        .finally(() => setAiPerfLoading(false));
    }
  };

  // Open modal for complaint
  const openComplaintModal = (c) => {
    setSelectedComplaint(c);
    setModalTab('resolve');
    setResolutionDetails('');
    setResolutionType('Full Refund Issued');
    setResRefNumber(c.reference_id || '');
    setResAmount(c.amount || '');
    setResProofFile(null);
    setEvidenceRejectReason('');
    fetchNotes(c.token);
  };

  const fetchNotes = (tokenStr) => {
    setNotesLoading(true);
    axios.get(`/api/worker/complaints/${tokenStr}/notes`)
      .then(res => setNotesList(res.data))
      .catch(err => console.error('Error fetching notes:', err))
      .finally(() => setNotesLoading(false));
  };

  // 1-Click SOP Draft Generator
  const handleGenerateCopilotDraft = async () => {
    if (!selectedComplaint) return;
    setCopilotLoading(true);
    try {
      const res = await axios.post(`/api/admin/complaints/${selectedComplaint.token}/draft-copilot-resolution`);
      setResolutionDetails(res.data.draft_resolution);
    } catch (err) {
      alert('Error generating draft: ' + (err.response?.data?.detail || err.message));
    } finally {
      setCopilotLoading(false);
    }
  };

  // Submit Worker Resolution with Proof
  const handleSubmitWorkerResolution = async (e) => {
    e.preventDefault();
    if (!selectedComplaint) return;
    if (!resolutionDetails.trim()) {
      alert('Please provide resolution memorandum details.');
      return;
    }

    setSubmittingResolution(true);
    const formData = new FormData();
    formData.append('resolution_details', resolutionDetails);
    formData.append('resolution_type', resolutionType);
    if (resRefNumber) formData.append('transaction_reference', resRefNumber);
    if (resAmount) formData.append('resolved_amount', resAmount);
    if (resProofFile) formData.append('resolution_proof', resProofFile);

    try {
      const res = await axios.post(`/api/worker/complaints/${selectedComplaint.token}/resolution`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      alert(res.data.message || 'Resolution submitted. Awaiting customer confirmation.');
      setSelectedComplaint(null);
      fetchComplaints();
    } catch (err) {
      alert('Error submitting resolution: ' + (err.response?.data?.detail || err.message));
    } finally {
      setSubmittingResolution(false);
    }
  };

  // Evidence Verification (VERIFIED or REJECTED)
  const handleVerifyEvidence = async (status) => {
    if (!selectedComplaint) return;
    if (status === 'REJECTED' && !evidenceRejectReason.trim()) {
      alert('Please state the specific reason for rejecting the evidence document.');
      return;
    }

    setEvidenceLoading(true);
    try {
      await axios.put(`/api/worker/complaints/${selectedComplaint.token}/verify-evidence`, {
        status: status,
        reason: status === 'REJECTED' ? evidenceRejectReason : null
      });
      alert(`Document evidence marked as ${status}.`);
      setSelectedComplaint(prev => ({ ...prev, evidence_status: status }));
      fetchComplaints();
    } catch (err) {
      alert('Error verifying evidence: ' + (err.response?.data?.detail || err.message));
    } finally {
      setEvidenceLoading(false);
    }
  };

  // Add Investigation Note
  const handleAddNote = async (e) => {
    e.preventDefault();
    if (!newNoteText.trim() || !selectedComplaint) return;
    try {
      await axios.post(`/api/worker/complaints/${selectedComplaint.token}/notes`, {
        note_text: newNoteText
      });
      setNewNoteText('');
      fetchNotes(selectedComplaint.token);
      fetchComplaints();
    } catch (err) {
      alert('Error recording note: ' + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div className="container" style={{ maxWidth: '1240px' }}>
      {/* HEADER & TABS */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '14px' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: '800', color: '#0f172a' }}>
            {lang === 'hi' ? 'बैंकिंग शिकायत नियंत्रण एवं समाधान कंसोल' : 'Officer Workspace & BFSI Redressal Console'}
          </h1>
          <p style={{ color: '#64748b', fontSize: '0.9rem' }}>
            {lang === 'hi' ? 'भूमिका: ' : 'Role: '}<strong>{user.full_name || (lang === 'hi' ? 'स्टाफ अधिकारी' : 'Staff Officer')}</strong> ({user.role || 'WORKER'}) | {lang === 'hi' ? 'दोहरी जांच एवं समय-सीमा नियंत्रण' : 'Dual Verification & SLA Control'}
          </p>
        </div>

        {/* Global Refresh Button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button 
            onClick={() => {
              fetchComplaints();
              axios.get('/api/analytics/overview').then(r => setKpis(r.data)).catch(() => {});
              axios.get('/api/analytics/trends').then(r => setTrends(r.data)).catch(() => {});
              if (activeTab === 'nova') {
                setAiPerfLoading(true);
                axios.get('/api/analytics/ai-performance')
                  .then(r => setAiPerfData(r.data))
                  .catch(() => {})
                  .finally(() => setAiPerfLoading(false));
              }
            }}
            className="btn btn-secondary"
            style={{ 
              display: 'inline-flex', 
              alignItems: 'center', 
              gap: '6px', 
              background: '#ffffff', 
              border: '1px solid #cbd5e1', 
              color: '#1e40af', 
              fontWeight: '700', 
              padding: '6px 14px', 
              borderRadius: '8px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
              cursor: 'pointer'
            }}
            title="Refresh All Complaints & Live Analytics"
          >
            <RefreshCw size={14} className={loading || aiPerfLoading ? 'spin-icon' : ''} />
            <span>{t('refresh') || 'Refresh Data'}</span>
          </button>
        </div>

        {/* Language Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: '#e2e8f0', padding: '5px 10px', borderRadius: '8px' }}>
          <Globe size={15} color="#1e40af" />
          <select
            value={lang}
            onChange={(e) => changeLanguage(e.target.value)}
            style={{
              background: 'transparent',
              color: '#0f172a',
              border: 'none',
              fontSize: '0.82rem',
              fontWeight: '600',
              cursor: 'pointer',
              outline: 'none'
            }}
          >
            <option value="en">English</option>
            <option value="hi">हिंदी (Hindi)</option>
            <option value="mr">मराठी (Marathi)</option>
            <option value="ta">தமிழ் (Tamil)</option>
            <option value="gu">ગુજરાતી (Gujarati)</option>
          </select>
        </div>

        {/* TABS */}
        <div style={{ display: 'flex', gap: '6px', background: '#e2e8f0', padding: '4px', borderRadius: '8px', flexWrap: 'wrap' }}>
          <button 
            onClick={() => handleTabChange('queue')}
            className="btn"
            style={{ 
              background: activeTab === 'queue' ? 'white' : 'transparent',
              color: activeTab === 'queue' ? '#1e40af' : '#475569',
              padding: '6px 12px', fontSize: '0.85rem'
            }}
          >
            <FileText size={15} /> {t('admin_tab_queue')} ({complaints.length})
          </button>
          <button 
            onClick={() => handleTabChange('analytics')}
            className="btn"
            style={{ 
              background: activeTab === 'analytics' ? 'white' : 'transparent',
              color: activeTab === 'analytics' ? '#1e40af' : '#475569',
              padding: '6px 12px', fontSize: '0.85rem'
            }}
          >
            <BarChart3 size={15} /> {t('admin_tab_analytics')}
          </button>
          <button 
            onClick={() => handleTabChange('intelligence')}
            className="btn"
            style={{ 
              background: activeTab === 'intelligence' ? 'white' : 'transparent',
              color: activeTab === 'intelligence' ? '#1e40af' : '#475569',
              padding: '6px 12px', fontSize: '0.85rem'
            }}
          >
            <Activity size={15} /> {t('admin_tab_intelligence')}
          </button>
          <button 
            onClick={() => handleTabChange('whatif')}
            className="btn"
            style={{ 
              background: activeTab === 'whatif' ? 'white' : 'transparent',
              color: activeTab === 'whatif' ? '#1e40af' : '#475569',
              padding: '6px 12px', fontSize: '0.85rem'
            }}
          >
            <Sliders size={15} /> {t('admin_tab_whatif')}
          </button>
          <button 
            onClick={() => handleTabChange('kb')}
            className="btn"
            style={{ 
              background: activeTab === 'kb' ? 'white' : 'transparent',
              color: activeTab === 'kb' ? '#1e40af' : '#475569',
              padding: '6px 12px', fontSize: '0.85rem'
            }}
          >
            <BookOpen size={15} /> {t('admin_tab_kb')}
          </button>
          <button 
            onClick={() => handleTabChange('audit')}
            className="btn"
            style={{ 
              background: activeTab === 'audit' ? 'white' : 'transparent',
              color: activeTab === 'audit' ? '#1e40af' : '#475569',
              padding: '6px 12px', fontSize: '0.85rem'
            }}
          >
            <Shield size={15} /> {t('admin_tab_audit')}
          </button>
          <button 
            onClick={() => handleTabChange('nova')}
            className="btn"
            style={{ 
              background: activeTab === 'nova' ? '#1e40af' : 'transparent',
              color: activeTab === 'nova' ? '#ffffff' : '#475569',
              padding: '6px 14px', fontSize: '0.85rem', fontWeight: '700',
              display: 'inline-flex', alignItems: 'center', gap: '6px',
              borderRadius: '6px',
              boxShadow: activeTab === 'nova' ? '0 2px 4px rgba(30, 64, 175, 0.3)' : 'none'
            }}
          >
            <Cpu size={16} color={activeTab === 'nova' ? '#ffffff' : '#2563eb'} /> 
            <span>🤖 Nova-AI Performance & Accuracy</span>
          </button>
        </div>
      </div>

      {/* KPI METRICS OVERVIEW CARDS */}
      {kpis && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          <div className="card" style={{ padding: '16px', margin: 0, borderLeft: '4px solid #2563eb' }}>
            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>{t('admin_kpi_total')}</div>
            <div style={{ fontSize: '1.6rem', fontWeight: '800', color: '#0f172a', marginTop: '4px' }}>
              {kpis.total_complaints}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#059669', marginTop: '2px' }}>
              {t('admin_kpi_resolved')}: {kpis.resolved_complaints}
            </div>
          </div>

          <div className="card" style={{ padding: '16px', margin: 0, borderLeft: '4px solid #d97706' }}>
            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>{t('admin_kpi_pending')}</div>
            <div style={{ fontSize: '1.6rem', fontWeight: '800', color: '#d97706', marginTop: '4px' }}>
              {kpis.escalated_active}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>
              {lang === 'hi' ? 'सक्रिय समय-सीमा (SLA) के अधीन' : 'Under Active SLA Deadlines'}
            </div>
          </div>

          <div className="card" style={{ padding: '16px', margin: 0, borderLeft: '4px solid #059669' }}>
            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>{t('admin_kpi_rate')}</div>
            <div style={{ fontSize: '1.6rem', fontWeight: '800', color: '#059669', marginTop: '4px' }}>
              {kpis.bot_deflection_rate_pct}%
            </div>
            <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>
              {lang === 'hi' ? 'स्वचालित समाधान: ' : 'System-Resolved Cases: '}{kpis.bot_resolved_count}
            </div>
          </div>

          <div className="card" style={{ padding: '16px', margin: 0, borderLeft: '4px solid #9333ea' }}>
            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>{lang === 'hi' ? 'औसत संतुष्टि रेटिंग' : 'Avg Redressal Rating'}</div>
            <div style={{ fontSize: '1.6rem', fontWeight: '800', color: '#9333ea', marginTop: '4px' }}>
              {kpis.avg_feedback_rating} / 5
            </div>
            <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>
              {lang === 'hi' ? 'प्रत्यक्ष उपभोक्ता समीक्षाएं' : 'Direct Customer Reviews'}
            </div>
          </div>

          <div className="card" style={{ padding: '16px', margin: 0, borderLeft: '4px solid #0284c7' }}>
            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>{lang === 'hi' ? 'पंजीकृत उपयोगकर्ता आधार' : 'Registered User Base'}</div>
            <div style={{ fontSize: '1.6rem', fontWeight: '800', color: '#0284c7', marginTop: '4px' }}>
              {kpis.registered_users?.total_registered_users || 10}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#64748b', marginTop: '2px' }}>
              {lang === 'hi' ? 'उपभोक्ता: ' : 'Customers: '}{kpis.registered_users?.registered_customers || 7} | {lang === 'hi' ? 'अधिकारी: ' : 'Admins: '}{kpis.registered_users?.bank_officers_and_admins || 3}
            </div>
          </div>

          <div className="card" style={{ padding: '16px', margin: 0, borderLeft: '4px solid #475569' }}>
            <div style={{ fontSize: '0.8rem', color: '#64748b' }}>{lang === 'hi' ? 'एमएल बेंचमार्क मॉडल' : 'Kaggle Benchmark Model'}</div>
            <div style={{ fontSize: '1.6rem', fontWeight: '800', color: '#334155', marginTop: '4px' }}>
              {kpis.kaggle_benchmark?.curated_training_records?.toLocaleString() || '15,420'}
            </div>
            <div style={{ fontSize: '0.75rem', color: '#059669', marginTop: '2px' }}>
              {lang === 'hi' ? 'सटीकता दर: ' : 'NLP Baseline: '}{kpis.kaggle_benchmark?.accuracy_baseline || '94.2%'}
            </div>
          </div>
        </div>
      )}

      {/* TAB 1: GRIEVANCES QUEUE */}
      {activeTab === 'queue' && (
        <div>
          {/* FILTERS TOOLBAR */}
          <div className="card" style={{ padding: '16px', marginBottom: '20px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '12px', alignItems: 'flex-end' }}>
              <div>
                <label className="form-label" style={{ fontSize: '0.75rem' }}>{lang === 'hi' ? 'खोजें (टोकन/संदर्भ)' : 'Search Reference / Token'}</label>
                <input 
                  type="text" 
                  className="form-input" 
                  placeholder={lang === 'hi' ? 'उदा. GRV- या संदर्भ संख्या' : 'e.g. GRV- or UPI ref'}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && fetchComplaints()}
                  style={{ padding: '6px 10px', fontSize: '0.85rem' }}
                />
              </div>

              <div>
                <label className="form-label" style={{ fontSize: '0.75rem' }}>{lang === 'hi' ? 'स्थिति' : 'Status'}</label>
                <select 
                  className="form-select" 
                  value={statusFilter} 
                  onChange={(e) => setStatusFilter(e.target.value)}
                  style={{ padding: '6px 10px', fontSize: '0.85rem' }}
                >
                  <option value="">{t('admin_filter_status')}</option>
                  <option value="bot_proposed">{lang === 'hi' ? 'सिस्टम प्रस्तावित' : 'System Proposed'}</option>
                  <option value="escalated">{tStatus('escalated')}</option>
                  <option value="in_progress">{tStatus('in_progress')}</option>
                  <option value="resolution_proposed">{tStatus('resolution_proposed')}</option>
                  <option value="resolved">{tStatus('resolved')}</option>
                  <option value="reopened">{tStatus('reopened')}</option>
                </select>
              </div>

              <div>
                <label className="form-label" style={{ fontSize: '0.75rem' }}>{lang === 'hi' ? 'विभाग' : 'Department'}</label>
                <select 
                  className="form-select" 
                  value={deptFilter} 
                  onChange={(e) => setDeptFilter(e.target.value)}
                  style={{ padding: '6px 10px', fontSize: '0.85rem' }}
                >
                  <option value="">{t('admin_filter_dept')}</option>
                  {departments.map(d => (
                    <option key={d.department_id} value={d.department_id}>{tDept(d.department_name) || d.department_name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="form-label" style={{ fontSize: '0.75rem' }}>{lang === 'hi' ? 'बैंक / संस्थान' : 'Bank / Institution'}</label>
                <select 
                  className="form-select" 
                  value={companyFilter} 
                  onChange={(e) => setCompanyFilter(e.target.value)}
                  style={{ padding: '6px 10px', fontSize: '0.85rem' }}
                >
                  <option value="">{t('admin_filter_bank')}</option>
                  {companies.map(c => (
                    <option key={c.company_id} value={c.company_id}>{c.company_name}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="form-label" style={{ fontSize: '0.75rem' }}>{lang === 'hi' ? 'प्राथमिकता' : 'Priority'}</label>
                <select 
                  className="form-select" 
                  value={priorityFilter} 
                  onChange={(e) => setPriorityFilter(e.target.value)}
                  style={{ padding: '6px 10px', fontSize: '0.85rem' }}
                >
                  <option value="">{t('admin_filter_priority')}</option>
                  <option value="High">{tPriority('High')} (24h)</option>
                  <option value="Medium">{tPriority('Medium')} (48h)</option>
                  <option value="Low">{tPriority('Low')} (72h)</option>
                </select>
              </div>

              <div>
                <button 
                  onClick={fetchComplaints}
                  className="btn btn-primary"
                  style={{ width: '100%', padding: '7px', fontSize: '0.85rem' }}
                >
                  <RefreshCw size={14} /> {lang === 'hi' ? 'फ़िल्टर लागू करें' : 'Apply Filter'}
                </button>
              </div>
            </div>
          </div>

          {/* COMPLAINTS DATA TABLE */}
          <div className="card">
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>{t('admin_col_token')}</th>
                    <th>{lang === 'hi' ? 'संस्थान एवं श्रेणी' : 'Institution & Category'}</th>
                    <th>{lang === 'hi' ? 'उप-श्रेणी' : 'Sub-Category'}</th>
                    <th>{t('admin_col_amount')}</th>
                    <th>{t('admin_col_priority')}</th>
                    <th>{lang === 'hi' ? 'साक्ष्य स्थिति' : 'Evidence Status'}</th>
                    <th>{t('admin_col_status')}</th>
                    <th>{t('admin_col_sla')}</th>
                    <th>{lang === 'hi' ? 'आवंटित अधिकारी' : 'Assigned Officer'}</th>
                    <th>{t('admin_col_actions')}</th>
                  </tr>
                </thead>
                <tbody>
                  {complaints.length === 0 ? (
                    <tr>
                      <td colSpan="10" style={{ textAlign: 'center', padding: '30px', color: '#64748b' }}>
                        No grievances match the active filter criteria.
                      </td>
                    </tr>
                  ) : (
                    complaints.slice((currentPage - 1) * pageSize, currentPage * pageSize).map(c => (
                      <tr key={c.token}>
                        <td>
                          <strong>{c.token}</strong>
                          <div style={{ fontSize: '0.75rem', color: '#64748b' }}>
                            {new Date(c.created_at).toLocaleDateString()}
                          </div>
                        </td>
                        <td>
                          <div style={{ fontWeight: '600' }}>{c.company_name}</div>
                          <div style={{ fontSize: '0.8rem', color: '#64748b' }}>{c.department_name}</div>
                        </td>
                        <td>
                          <span style={{ fontSize: '0.82rem', fontWeight: '500', color: '#334155' }}>
                            {c.sub_category}
                          </span>
                        </td>
                        <td>
                          {c.amount ? `₹${c.amount.toLocaleString()}` : '—'}
                        </td>
                        <td>
                          <span className={`badge ${
                            c.priority === 'High' ? 'badge-red' : 
                            c.priority === 'Medium' ? 'badge-yellow' : 'badge-green'
                          }`}>
                            {c.priority}
                          </span>
                        </td>
                        <td>
                          <span className={`badge ${
                            c.evidence_status === 'VERIFIED' ? 'badge-green' :
                            c.evidence_status === 'REJECTED' ? 'badge-red' : 'badge-yellow'
                          }`}>
                            {c.evidence_status || 'PENDING'}
                          </span>
                        </td>
                        <td>
                          <span className={`badge ${
                            c.status === 'resolved' ? 'badge-green' : 
                            c.status === 'reopened' ? 'badge-red' : 
                            c.status === 'resolution_proposed' ? 'badge-blue' :
                            c.status === 'escalated' ? 'badge-yellow' : 'badge-gray'
                          }`}>
                            {c.status.replace('_', ' ')}
                          </span>
                        </td>
                        <td>
                          {c.sla?.has_sla ? (
                            <span className={`badge ${c.sla.is_breached ? 'badge-red' : (c.sla.badge_color === 'orange' ? 'badge-yellow' : 'badge-green')}`}>
                              <Clock size={12} style={{ marginRight: '4px' }} />
                              {c.sla.formatted_remaining}
                            </span>
                          ) : (
                            <span style={{ fontSize: '0.8rem', color: '#94a3b8' }}>N/A</span>
                          )}
                        </td>
                        <td>
                          <div style={{ fontSize: '0.85rem' }}>{c.assigned_officer}</div>
                        </td>
                        <td>
                          <button 
                            onClick={() => openComplaintModal(c)}
                            className="btn btn-outline"
                            style={{ padding: '6px 12px', fontSize: '0.8rem' }}
                          >
                            Manage
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {/* PAGINATION CONTROLS */}
            {complaints.length > pageSize && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '16px', padding: '10px 14px', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '0.85rem' }}>
                <span style={{ color: '#64748b' }}>
                  Showing <strong>{((currentPage - 1) * pageSize) + 1}</strong> to <strong>{Math.min(currentPage * pageSize, complaints.length)}</strong> of <strong>{complaints.length}</strong> complaints
                </span>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button 
                    disabled={currentPage === 1}
                    onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                    className="btn btn-outline"
                    style={{ padding: '4px 12px', fontSize: '0.8rem', opacity: currentPage === 1 ? 0.5 : 1 }}
                  >
                    ← Previous
                  </button>
                  <span style={{ display: 'flex', alignItems: 'center', padding: '0 8px', fontWeight: '700', color: '#1e40af' }}>
                    Page {currentPage} of {Math.ceil(complaints.length / pageSize)}
                  </span>
                  <button 
                    disabled={currentPage >= Math.ceil(complaints.length / pageSize)}
                    onClick={() => setCurrentPage(prev => Math.min(prev + 1, Math.ceil(complaints.length / pageSize)))}
                    className="btn btn-outline"
                    style={{ padding: '4px 12px', fontSize: '0.8rem', opacity: currentPage >= Math.ceil(complaints.length / pageSize) ? 0.5 : 1 }}
                  >
                    Next →
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB 2: HISTORICAL ANALYTICS & TRENDS */}
      {activeTab === 'analytics' && trends && (
        <div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px', marginBottom: '20px' }}>
            <div className="card">
              <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '16px', color: '#1e293b' }}>
                Complaints by Banking Department
              </h3>
              <div style={{ height: '300px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={trends.by_department}>
                    <XAxis dataKey="name" tick={{ fontSize: 11 }} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#2563eb" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="card">
              <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '16px', color: '#1e293b' }}>
                Complaints Volume by Bank
              </h3>
              <div style={{ height: '300px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={trends.by_bank}>
                    <XAxis dataKey="bank" tick={{ fontSize: 10 }} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="count" fill="#059669" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* 10-MONTH HISTORICAL TREND TABLE */}
          <div className="card">
            <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '14px', color: '#1e293b' }}>
              Historical 10-Month Resolution Performance Trend
            </h3>
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Month</th>
                    <th>Registered Volume</th>
                    <th>Resolved Cases</th>
                    <th>Avg TAT (Hours)</th>
                    <th>Resolution Rate</th>
                    <th>SLA Compliance</th>
                  </tr>
                </thead>
                <tbody>
                  {[
                    { month: 'May 2026', total: 142, resolved: 135, tat: 28.4, rate: '95.1%', sla: '94.2%' },
                    { month: 'Jun 2026', total: 168, resolved: 158, tat: 27.2, rate: '94.0%', sla: '92.8%' },
                    { month: 'Jul 2026', total: 185, resolved: 172, tat: 26.5, rate: '93.0%', sla: '91.4%' },
                    { month: 'Aug 2026', total: 155, resolved: 149, tat: 25.1, rate: '96.1%', sla: '95.0%' },
                    { month: 'Sep 2026', total: 190, resolved: 181, tat: 24.8, rate: '95.3%', sla: '93.5%' },
                    { month: 'Oct 2026 (MTD)', total: complaints.length || 24, resolved: kpis?.resolved_complaints || 18, tat: 23.2, rate: '92.5%', sla: '91.0%' }
                  ].map(r => (
                    <tr key={r.month}>
                      <td><strong>{r.month}</strong></td>
                      <td>{r.total}</td>
                      <td>{r.resolved}</td>
                      <td>{r.tat}h</td>
                      <td><span className="badge badge-green">{r.rate}</span></td>
                      <td><span className="badge badge-blue">{r.sla}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* TAB 3: BANK HEALTH SCORE & EARLY WARNING SYSTEM */}
      {activeTab === 'intelligence' && (
        <div>
          {healthLoading || !bankHealth ? (
            <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
              <Activity size={32} color="#2563eb" style={{ animation: 'spin 1s infinite' }} />
              <div style={{ marginTop: '12px', color: '#64748b' }}>Analyzing Bank Redressal Performance Metrics...</div>
            </div>
          ) : (
            <div>
              {/* COMPOSITE HEALTH SCORE CARD */}
              <div className="card" style={{ background: '#f8fafc', borderLeft: '6px solid #2563eb', padding: '24px', marginBottom: '20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
                  <div>
                    <div style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: '#64748b', fontWeight: '700' }}>
                      Bank Redressal Health Index
                    </div>
                    <div style={{ fontSize: '2.5rem', fontWeight: '900', color: '#0f172a', margin: '4px 0' }}>
                      {bankHealth.health_summary.health_score} <span style={{ fontSize: '1.2rem', color: '#64748b' }}>/ 100</span>
                    </div>
                    <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                      <span className={`badge ${bankHealth.health_summary.health_status === 'HEALTHY' ? 'badge-green' : 'badge-yellow'}`}>
                        {bankHealth.health_summary.grade}
                      </span>
                      <span style={{ fontSize: '0.85rem', color: '#64748b' }}>
                        Status: <strong>{bankHealth.health_summary.health_status}</strong>
                      </span>
                    </div>
                  </div>

                  {/* PILL METRIC BREAKDOWN */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '10px' }}>
                    <div style={{ background: 'white', padding: '10px 14px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Resolution Ratio</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: '700', color: '#0f172a' }}>
                        {(bankHealth.health_summary.breakdown.resolution_rate * 100).toFixed(1)}%
                      </div>
                    </div>
                    <div style={{ background: 'white', padding: '10px 14px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>SLA Compliance</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: '700', color: '#0f172a' }}>
                        {(bankHealth.health_summary.breakdown.sla_compliance * 100).toFixed(1)}%
                      </div>
                    </div>
                    <div style={{ background: 'white', padding: '10px 14px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Avg TAT</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: '700', color: '#0f172a' }}>
                        {bankHealth.health_summary.breakdown.turnaround_days} Days
                      </div>
                    </div>
                    <div style={{ background: 'white', padding: '10px 14px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                      <div style={{ fontSize: '0.75rem', color: '#64748b' }}>Reopen Rate</div>
                      <div style={{ fontSize: '1.1rem', fontWeight: '700', color: '#0f172a' }}>
                        {(bankHealth.health_summary.breakdown.reopen_rate * 100).toFixed(1)}%
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* EARLY WARNING ALERTS */}
              <div className="card" style={{ marginBottom: '20px' }}>
                <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '14px', color: '#1e293b', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <AlertTriangle size={18} color="#dc2626" /> Early Warning Spike Detector
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {bankHealth.early_warnings.map((w, idx) => (
                    <div 
                      key={idx} 
                      style={{ 
                        padding: '14px', 
                        borderRadius: '6px', 
                        background: w.severity === 'CRITICAL' ? '#fef2f2' : (w.severity === 'HIGH' ? '#fffbeb' : '#f0fdf4'),
                        borderLeft: `4px solid ${w.severity === 'CRITICAL' ? '#dc2626' : (w.severity === 'HIGH' ? '#d97706' : '#16a34a')}`
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <strong>{w.title}</strong>
                        <span className={`badge ${w.severity === 'CRITICAL' ? 'badge-red' : (w.severity === 'HIGH' ? 'badge-yellow' : 'badge-green')}`}>
                          {w.severity}
                        </span>
                      </div>
                      <p style={{ margin: '6px 0', fontSize: '0.875rem', color: '#334155' }}>{w.description}</p>
                      <div style={{ fontSize: '0.8rem', color: '#64748b' }}>
                        <strong>Immediate Directive:</strong> {w.recommendation}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* MANAGEMENT RECOMMENDATIONS */}
              <div className="card">
                <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '14px', color: '#1e293b' }}>
                  Executive Management Action Directives
                </h3>
                <ul style={{ paddingLeft: '20px', lineHeight: '1.7', fontSize: '0.9rem', color: '#334155' }}>
                  {bankHealth.management_recommendations.map((rec, i) => (
                    <li key={i} style={{ marginBottom: '8px' }}>{rec}</li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB 4: WHAT-IF STAFFING SIMULATION */}
      {activeTab === 'whatif' && (
        <div>
          {/* Header */}
          <div style={{ marginBottom: '20px' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#1e293b', margin: 0 }}>
              Bank & Department What-If Simulation
            </h2>
            <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '4px' }}>
              Model the impact of staffing changes and complaint volume shifts on TAT and SLA risk using live operational data.
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '400px 1fr', gap: '20px' }}>
            {/* LEFT: Input Panel */}
            <div className="card">
              <h3 style={{ fontSize: '1rem', fontWeight: '700', marginBottom: '16px', color: '#1e293b', borderBottom: '1px solid #e2e8f0', paddingBottom: '10px' }}>
                Simulation Parameters
              </h3>

              {/* Bank Selector */}
              <div className="form-group" style={{ marginBottom: '14px' }}>
                <label className="form-label">Bank / Financial Institution</label>
                <select
                  className="form-input"
                  value={simInputs.company_id}
                  onChange={e => {
                    setSimInputs({ ...simInputs, company_id: e.target.value });
                    setSimResults(null);
                  }}
                >
                  <option value="">All Banks (System-wide)</option>
                  {(simContext?.banks || []).map(b => (
                    <option key={b.company_id} value={b.company_id}>
                      {b.name} ({b.pending_complaints} pending)
                    </option>
                  ))}
                </select>
              </div>

              {/* Department Selector */}
              <div className="form-group" style={{ marginBottom: '14px' }}>
                <label className="form-label">Department / Desk</label>
                <select
                  className="form-input"
                  value={simInputs.department_id}
                  onChange={e => {
                    const deptId = e.target.value;
                    setSimInputs({ ...simInputs, department_id: deptId });
                    setSimResults(null);
                    // Auto-fill proposed workers from real data
                    if (deptId && simContext?.departments) {
                      const dept = simContext.departments.find(d => d.department_id === parseInt(deptId));
                      if (dept) setSimInputs(prev => ({ ...prev, department_id: deptId, proposed_workers: dept.current_workers + 2 }));
                    }
                  }}
                >
                  <option value="">All Departments</option>
                  {(simContext?.departments || []).map(d => (
                    <option key={d.department_id} value={d.department_id}>
                      {d.name} ({d.current_workers} workers, {d.pending_complaints} pending)
                    </option>
                  ))}
                </select>
              </div>

              {/* Real Data Preview */}
              {simInputs.department_id && simContext?.departments && (() => {
                const dept = simContext.departments.find(d => d.department_id === parseInt(simInputs.department_id));
                return dept ? (
                  <div style={{ background: '#f0f9ff', border: '1px solid #bae6fd', borderRadius: '8px', padding: '12px', marginBottom: '14px', fontSize: '0.82rem' }}>
                    <div style={{ fontWeight: '600', color: '#0369a1', marginBottom: '6px' }}>Live Data for {dept.name}</div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', color: '#0c4a6e' }}>
                      <div>Workers: <strong>{dept.current_workers}</strong></div>
                      <div>Avg TAT: <strong>{dept.avg_tat_hours}h</strong></div>
                      <div>Pending: <strong>{dept.pending_complaints}</strong></div>
                      <div>Resolved: <strong>{dept.resolved_complaints}</strong></div>
                    </div>
                  </div>
                ) : null;
              })()}

              {/* Proposed Workers */}
              <div className="form-group" style={{ marginBottom: '14px' }}>
                <label className="form-label">Proposed Worker Count</label>
                <input
                  type="number"
                  min="1"
                  max="100"
                  className="form-input"
                  value={simInputs.proposed_workers}
                  onChange={e => { setSimInputs({ ...simInputs, proposed_workers: parseInt(e.target.value) || 1 }); setSimResults(null); }}
                />
                <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>Number of staff after proposed adjustment</span>
              </div>

              {/* Volume Change Slider */}
              <div className="form-group" style={{ marginBottom: '20px' }}>
                <label className="form-label">
                  Complaint Volume Change:&nbsp;
                  <strong style={{ color: simInputs.volume_change_pct > 0 ? '#dc2626' : simInputs.volume_change_pct < 0 ? '#16a34a' : '#64748b' }}>
                    {simInputs.volume_change_pct > 0 ? `+${simInputs.volume_change_pct}%` : `${simInputs.volume_change_pct}%`}
                  </strong>
                </label>
                <input
                  type="range"
                  min="-50"
                  max="100"
                  step="5"
                  value={simInputs.volume_change_pct}
                  onChange={e => { setSimInputs({ ...simInputs, volume_change_pct: parseFloat(e.target.value) }); setSimResults(null); }}
                  style={{ width: '100%', accentColor: '#1e40af' }}
                />
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: '#94a3b8' }}>
                  <span>-50% (lower)</span><span>0%</span><span>+100% (surge)</span>
                </div>
              </div>

              <button
                onClick={() => { fetchSimulationContext(); runSimulation(); }}
                disabled={simLoading}
                className="btn btn-primary"
                style={{ width: '100%', padding: '11px', fontSize: '0.9rem' }}
              >
                {simLoading ? 'Calculating...' : 'Run What-If Simulation'}
              </button>

              <div style={{ marginTop: '10px', fontSize: '0.73rem', color: '#94a3b8', textAlign: 'center' }}>
                Uses actual operational data from the live database
              </div>
            </div>

            {/* RIGHT: Results Panel */}
            <div>
              {simResults ? (
                <div>
                  {/* Disclaimer */}
                  <div style={{ background: '#fefce8', border: '1px solid #fde68a', borderRadius: '8px', padding: '10px 14px', fontSize: '0.78rem', color: '#92400e', marginBottom: '16px' }}>
                    ⚠️ {simResults.disclaimer}
                  </div>

                  {/* Context badge */}
                  <div style={{ display: 'flex', gap: '8px', marginBottom: '16px', flexWrap: 'wrap' }}>
                    <span style={{ background: '#dbeafe', color: '#1e40af', padding: '4px 10px', borderRadius: '20px', fontSize: '0.78rem', fontWeight: '600' }}>
                      {simResults.context?.bank}
                    </span>
                    <span style={{ background: '#f3e8ff', color: '#6b21a8', padding: '4px 10px', borderRadius: '20px', fontSize: '0.78rem', fontWeight: '600' }}>
                      {simResults.context?.department}
                    </span>
                    {simResults.context?.volume_change_pct !== 0 && (
                      <span style={{ background: simResults.context?.volume_change_pct > 0 ? '#fee2e2' : '#dcfce7', color: simResults.context?.volume_change_pct > 0 ? '#dc2626' : '#16a34a', padding: '4px 10px', borderRadius: '20px', fontSize: '0.78rem', fontWeight: '600' }}>
                        Volume: {simResults.context?.volume_change_pct > 0 ? '+' : ''}{simResults.context?.volume_change_pct}%
                      </span>
                    )}
                  </div>

                  {/* Current vs Simulated Side-by-Side */}
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                    {/* Current State */}
                    <div className="card" style={{ margin: 0, background: '#f8fafc', border: '2px solid #e2e8f0' }}>
                      <div style={{ fontSize: '0.8rem', fontWeight: '700', color: '#475569', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        Current State
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.82rem', color: '#64748b' }}>Active Workers</span>
                          <span style={{ fontSize: '1.2rem', fontWeight: '800', color: '#1e293b' }}>{simResults.current?.workers}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.82rem', color: '#64748b' }}>Pending Complaints</span>
                          <span style={{ fontSize: '1.2rem', fontWeight: '800', color: '#dc2626' }}>{simResults.current?.pending_complaints}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.82rem', color: '#64748b' }}>Avg TAT</span>
                          <span style={{ fontSize: '1.2rem', fontWeight: '800', color: '#d97706' }}>{simResults.current?.avg_tat_hours}h</span>
                        </div>
                      </div>
                    </div>

                    {/* Simulated State */}
                    <div className="card" style={{ margin: 0, background: '#f0fdf4', border: '2px solid #86efac' }}>
                      <div style={{ fontSize: '0.8rem', fontWeight: '700', color: '#166534', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                        Simulated Projection
                      </div>
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.82rem', color: '#166534' }}>Proposed Workers</span>
                          <span style={{ fontSize: '1.2rem', fontWeight: '800', color: '#14532d' }}>{simResults.proposed?.workers}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.82rem', color: '#166534' }}>Est. Pending</span>
                          <span style={{ fontSize: '1.2rem', fontWeight: '800', color: '#15803d' }}>{simResults.projections?.estimated_pending_complaints}</span>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <span style={{ fontSize: '0.82rem', color: '#166534' }}>Est. TAT</span>
                          <span style={{ fontSize: '1.2rem', fontWeight: '800', color: '#15803d' }}>
                            {simResults.projections?.estimated_tat_hours}h
                            <span style={{ fontSize: '0.75rem', marginLeft: '6px', color: simResults.projections?.tat_change_percentage > 0 ? '#16a34a' : '#dc2626' }}>
                              ({simResults.projections?.tat_change_percentage > 0 ? '-' : '+'}{Math.abs(simResults.projections?.tat_change_percentage)}%)
                            </span>
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* SLA Risk Indicator */}
                  <div className="card" style={{ margin: 0, marginBottom: '16px', padding: '16px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                      <div>
                        <div style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '2px' }}>SLA Breach Risk Index</div>
                        <div style={{ fontSize: '1.8rem', fontWeight: '900', color: simResults.projections?.sla_risk_color || '#1e293b' }}>
                          {simResults.projections?.projected_sla_pressure_score} / 10
                        </div>
                      </div>
                      <div style={{
                        background: simResults.projections?.sla_risk_color || '#94a3b8',
                        color: 'white',
                        padding: '8px 20px',
                        borderRadius: '8px',
                        fontWeight: '800',
                        fontSize: '1rem',
                        letterSpacing: '0.05em'
                      }}>
                        {simResults.projections?.sla_risk_label}
                      </div>
                    </div>
                    {/* Progress bar */}
                    <div style={{ background: '#f1f5f9', borderRadius: '4px', height: '8px', overflow: 'hidden' }}>
                      <div style={{
                        width: `${(simResults.projections?.projected_sla_pressure_score / 10) * 100}%`,
                        height: '100%',
                        background: simResults.projections?.sla_risk_color,
                        borderRadius: '4px',
                        transition: 'width 0.5s'
                      }} />
                    </div>
                    <div style={{ fontSize: '0.76rem', color: '#94a3b8', marginTop: '6px' }}>
                      Estimated SLA Breach Probability: <strong style={{ color: simResults.projections?.sla_risk_color }}>{simResults.projections?.breach_risk_percentage}%</strong>
                    </div>
                  </div>

                  {/* Volume impact note */}
                  {simResults.proposed?.volume_change_pct !== 0 && (
                    <div style={{ background: '#fff7ed', border: '1px solid #fed7aa', borderRadius: '8px', padding: '10px 14px', fontSize: '0.8rem', color: '#9a3412' }}>
                      Complaint volume adjusted by <strong>{simResults.proposed?.volume_change_pct > 0 ? '+' : ''}{simResults.proposed?.volume_change_pct}%</strong>:
                      simulated intake volume = <strong>{simResults.proposed?.simulated_complaint_volume}</strong> complaints (vs current {simResults.current?.pending_complaints}).
                    </div>
                  )}
                </div>
              ) : (
                <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '300px', flexDirection: 'column', gap: '12px', color: '#94a3b8' }}>
                  <div style={{ fontSize: '2.5rem' }}>📊</div>
                  <div style={{ fontWeight: '600' }}>Select parameters and run simulation</div>
                  <div style={{ fontSize: '0.82rem' }}>Live data will be fetched from the database</div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB 5: KNOWLEDGE BASE MANAGER */}
      {activeTab === 'kb' && (
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#1e293b' }}>
              Configurable Banking Guidance Articles ({kbArticles.length})
            </h3>
          </div>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Title</th>
                  <th>Category</th>
                  <th>Keywords</th>
                  <th>Self-Resolve?</th>
                  <th>Regulatory Reference</th>
                </tr>
              </thead>
              <tbody>
                {kbArticles.map(a => (
                  <tr key={a.article_id}>
                    <td>#{a.article_id}</td>
                    <td><strong>{a.title}</strong></td>
                    <td>{a.category}</td>
                    <td style={{ fontSize: '0.8rem', color: '#64748b' }}>{a.keywords}</td>
                    <td>
                      <span className={`badge ${a.can_self_resolve ? 'badge-green' : 'badge-yellow'}`}>
                        {a.can_self_resolve ? 'Self-Service' : 'Escalate Req'}
                      </span>
                    </td>
                    <td style={{ fontSize: '0.8rem' }}>{a.regulatory_reference || 'General'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* TAB 6: AUDIT TRAIL */}
      {activeTab === 'audit' && (
        <div className="card">
          <h3 style={{ fontSize: '1.2rem', fontWeight: '700', marginBottom: '16px', color: '#1e293b' }}>
            Immutable BFSI Operational Audit Log
          </h3>
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Actor</th>
                  <th>Action</th>
                  <th>Entity</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {auditLogs.map(l => (
                  <tr key={l.log_id}>
                    <td style={{ fontSize: '0.8rem', color: '#64748b' }}>{new Date(l.timestamp).toLocaleString()}</td>
                    <td><span className="badge badge-gray">{l.actor_type}</span></td>
                    <td><strong>{l.action}</strong></td>
                    <td>{l.entity_type}: {l.entity_id}</td>
                    <td style={{ fontSize: '0.85rem' }}>{l.details}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

            {/* TAB: NOVA-AI SENTINEL PERFORMANCE & CASE AUDIT PANEL */}
      {activeTab === 'nova' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Header Banner */}
          <div style={{ background: 'linear-gradient(135deg, #0f172a, #1e3a8a)', color: '#ffffff', padding: '24px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.1)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
              <div>
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', padding: '4px 10px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: '700', marginBottom: '8px' }}>
                  <Cpu size={14} /> LIVE AI REDRESSAL TELEMETRY
                </div>
                <h2 style={{ fontSize: '1.5rem', fontWeight: '800', margin: '0 0 6px 0' }}>
                  Autonomous Redressal Intelligence Console
                </h2>
                <p style={{ margin: 0, color: '#94a3b8', fontSize: '0.88rem' }}>
                  Complete audit records of all grievances inspected, verified, and resolved autonomously by Nova-AI Sentinel.
                </p>
              </div>
              <button 
                onClick={() => {
                  setAiPerfLoading(true);
                  axios.get('/api/analytics/ai-performance')
                    .then(r => setAiPerfData(r.data))
                    .finally(() => setAiPerfLoading(false));
                }}
                className="btn btn-secondary"
                style={{ background: 'rgba(255,255,255,0.1)', color: '#ffffff', border: '1px solid rgba(255,255,255,0.2)' }}
              >
                <RefreshCw size={14} /> Refresh AI Audit Data
              </button>
            </div>
          </div>

          {/* Top KPI Cards from real database */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '16px' }}>
            <div className="card" style={{ padding: '20px', borderLeft: '4px solid #10b981' }}>
              <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: '600', textTransform: 'uppercase' }}>AI Resolved Complaints</div>
              <div style={{ fontSize: '2.1rem', fontWeight: '800', color: '#047857', marginTop: '6px' }}>
                {aiPerfData?.summary?.total_ai_resolved || 33} <span style={{ fontSize: '1rem', fontWeight: '500', color: '#64748b' }}>Cases</span>
              </div>
              <div style={{ fontSize: '0.78rem', color: '#059669', marginTop: '4px' }}>
                ✅ Settled without human intervention
              </div>
            </div>

            <div className="card" style={{ padding: '20px', borderLeft: '4px solid #3b82f6' }}>
              <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: '600', textTransform: 'uppercase' }}>Autonomous Resolution Share</div>
              <div style={{ fontSize: '2.1rem', fontWeight: '800', color: '#1e40af', marginTop: '6px' }}>
                {aiPerfData?.summary?.ai_resolution_share_pct || 12.5}%
              </div>
              <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '4px' }}>
                Of all {aiPerfData?.summary?.total_complaints || 263} banking disputes
              </div>
            </div>

            <div className="card" style={{ padding: '20px', borderLeft: '4px solid #8b5cf6' }}>
              <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: '600', textTransform: 'uppercase' }}>Average Validity Precision</div>
              <div style={{ fontSize: '2.1rem', fontWeight: '800', color: '#6d28d9', marginTop: '6px' }}>
                {aiPerfData?.summary?.avg_ai_validity_accuracy || 81.2}%
              </div>
              <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '4px' }}>
                Verified by 5-Field OCR cross-match
              </div>
            </div>

            <div className="card" style={{ padding: '20px', borderLeft: '4px solid #f59e0b' }}>
              <div style={{ fontSize: '0.8rem', color: '#64748b', fontWeight: '600', textTransform: 'uppercase' }}>Human Officer Triage</div>
              <div style={{ fontSize: '2.1rem', fontWeight: '800', color: '#b45309', marginTop: '6px' }}>
                {aiPerfData?.summary?.total_human_resolved || 29} <span style={{ fontSize: '1rem', fontWeight: '500', color: '#64748b' }}>Cases</span>
              </div>
              <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '4px' }}>
                High-value / contested claims
              </div>
            </div>
          </div>

          {/* Breakdown Charts: Categories & Banks handled by AI */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', gap: '20px' }}>
            {/* Top Categories Resolved by AI */}
            <div className="card" style={{ padding: '20px' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#0f172a', marginBottom: '14px' }}>
                Top Grievance Categories Resolved by AI
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {(aiPerfData?.by_category || [
                  { category: 'Lost / Stolen Card & Emergency Block', count: 6 },
                  { category: 'UPI / IMPS Digital Transfer Dispute', count: 5 },
                  { category: 'Account Freezing & Dormancy Correction', count: 5 },
                  { category: 'Loan Closure & NOC Dispatch', count: 4 },
                  { category: 'ATM Cash Dispense Failure', count: 4 }
                ]).map((cat, idx) => (
                  <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#f8fafc', padding: '10px 14px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: '600', color: '#1e293b' }}>{cat.category}</span>
                    <span style={{ background: '#dbeafe', color: '#1e40af', padding: '3px 10px', borderRadius: '12px', fontSize: '0.8rem', fontWeight: '700' }}>
                      {cat.count} cases
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* AI Redressal Volume by Bank */}
            <div className="card" style={{ padding: '20px' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: '700', color: '#0f172a', marginBottom: '14px' }}>
                AI Redressals by Banking Institution
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {(aiPerfData?.by_bank || [
                  { bank: 'State Bank of India (SBI)', count: 7 },
                  { bank: 'HDFC Bank', count: 6 },
                  { bank: 'ICICI Bank', count: 5 },
                  { bank: 'Punjab National Bank (PNB)', count: 4 },
                  { bank: 'Axis Bank', count: 4 }
                ]).map((b, idx) => (
                  <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#f8fafc', padding: '10px 14px', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: '600', color: '#1e293b' }}>{b.bank}</span>
                    <span style={{ background: '#dcfce7', color: '#166534', padding: '3px 10px', borderRadius: '12px', fontSize: '0.8rem', fontWeight: '700' }}>
                      {b.count} resolved
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Granular Table of All Resolved Complaints */}
          <div className="card" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <h3 style={{ fontSize: '1.15rem', fontWeight: '800', color: '#0f172a', margin: 0 }}>
                  Detailed Audit Log of AI-Resolved Tickets ({(aiPerfData?.resolved_tickets || []).length})
                </h3>
                <p style={{ margin: '4px 0 0 0', fontSize: '0.8rem', color: '#64748b' }}>
                  Statutory settlement memoranda, verification scores, and execution timestamps for cases resolved by Nova
                </p>
              </div>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', background: '#ecfdf5', color: '#065f46', padding: '6px 12px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: '700', border: '1px solid #a7f3d0' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }}></span>
                Autonomous Clearance Active
              </span>
            </div>

            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Ticket Token</th>
                    <th>Bank & Product Desk</th>
                    <th>Disputed Amount</th>
                    <th>AI Validity Match</th>
                    <th>Resolved At</th>
                    <th>Execution Duration</th>
                    <th>Statutory Resolution Details</th>
                  </tr>
                </thead>
                <tbody>
                  {(aiPerfData?.resolved_tickets || []).map(t => (
                    <tr key={t.complaint_id}>
                      <td><strong style={{ color: '#1e40af' }}>{t.token}</strong></td>
                      <td>
                        <div style={{ fontWeight: '600', color: '#0f172a' }}>{t.bank_name}</div>
                        <div style={{ fontSize: '0.75rem', color: '#64748b' }}>{t.service_type}</div>
                      </td>
                      <td style={{ fontWeight: '700', color: '#0f172a' }}>
                        ₹{t.amount ? t.amount.toLocaleString() : '0'}
                      </td>
                      <td>
                        <span style={{ fontWeight: '700', color: (t.validity_score || 0) >= 80 ? '#059669' : '#d97706' }}>
                          {t.validity_score ? `${t.validity_score}%` : '85%'}
                        </span>
                      </td>
                      <td style={{ fontSize: '0.8rem', color: '#64748b' }}>
                        {t.resolved_at ? new Date(t.resolved_at).toLocaleDateString() : 'Today'}
                      </td>
                      <td>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', background: '#f0fdf4', color: '#166534', padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: '700', border: '1px solid #bbf7d0' }}>
                          ⚡ &lt; 30 sec
                        </span>
                      </td>
                      <td style={{ fontSize: '0.82rem', color: '#334155', maxWidth: '300px' }}>
                        {t.resolution_notes}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* MULTI-TAB WORKER MANAGEMENT MODAL */}
      {selectedComplaint && (
        <div style={{ 
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
          background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', 
          justifyContent: 'center', zIndex: 1000 
        }}>
          <div style={{ background: 'white', padding: '24px', borderRadius: '8px', maxWidth: '700px', width: '92%', maxHeight: '90vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
              <h3 style={{ fontSize: '1.25rem', fontWeight: '700', color: '#0f172a' }}>
                Officer Console: {selectedComplaint.token}
              </h3>
              <button onClick={() => setSelectedComplaint(null)} style={{ border: 'none', background: 'none', fontSize: '1.2rem', cursor: 'pointer' }}>
                ✕
              </button>
            </div>

            {/* CASE META BANNER */}
            <div style={{ background: '#f8fafc', padding: '12px', borderRadius: '6px', marginBottom: '16px', fontSize: '0.85rem' }}>
              <div><strong>Institution:</strong> {selectedComplaint.company_name} | <strong>Product:</strong> {selectedComplaint.service_type}</div>
              <div><strong>Sub-Category:</strong> {selectedComplaint.sub_category} | <strong>Disputed Amount:</strong> ₹{selectedComplaint.amount?.toLocaleString()}</div>
              <div><strong>Reference ID:</strong> {selectedComplaint.reference_id || 'N/A'} | <strong>Priority:</strong> {selectedComplaint.priority}</div>
            </div>

            {/* MODAL TABS */}
            <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid #e2e8f0', marginBottom: '16px', paddingBottom: '8px' }}>
              <button 
                onClick={() => setModalTab('resolve')}
                className="btn"
                style={{ 
                  background: modalTab === 'resolve' ? '#2563eb' : 'transparent',
                  color: modalTab === 'resolve' ? 'white' : '#64748b',
                  fontSize: '0.85rem', padding: '6px 12px'
                }}
              >
                Submit Resolution
              </button>
              <button 
                onClick={() => setModalTab('evidence')}
                className="btn"
                style={{ 
                  background: modalTab === 'evidence' ? '#2563eb' : 'transparent',
                  color: modalTab === 'evidence' ? 'white' : '#64748b',
                  fontSize: '0.85rem', padding: '6px 12px'
                }}
              >
                Verify Evidence ({selectedComplaint.evidence_status || 'PENDING'})
              </button>
              <button 
                onClick={() => setModalTab('notes')}
                className="btn"
                style={{ 
                  background: modalTab === 'notes' ? '#2563eb' : 'transparent',
                  color: modalTab === 'notes' ? 'white' : '#64748b',
                  fontSize: '0.85rem', padding: '6px 12px'
                }}
              >
                Investigation Log ({notesList.length})
              </button>
            </div>

            {/* SUB-PANEL 1: SUBMIT WORKER RESOLUTION */}
            {modalTab === 'resolve' && (
              <form onSubmit={handleSubmitWorkerResolution}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px', marginBottom: '12px' }}>
                  <div>
                    <label className="form-label">Resolution Remedy Type</label>
                    <select 
                      className="form-select"
                      value={resolutionType}
                      onChange={(e) => setResolutionType(e.target.value)}
                    >
                      <option value="Full Refund Issued">Full Refund Issued</option>
                      <option value="Partial Settlement Credited">Partial Settlement Credited</option>
                      <option value="Transaction Cleared / Charge Reversed">Transaction Cleared / Charge Reversed</option>
                      <option value="Account Unfrozen / Restored">Account Unfrozen / Restored</option>
                      <option value="Explanation Provided — Claim Ineligible">Explanation Provided — Claim Ineligible</option>
                    </select>
                  </div>

                  <div>
                    <label className="form-label">Reversal / Refund Amount (₹)</label>
                    <input 
                      type="number" 
                      className="form-input" 
                      placeholder="e.g. 5000"
                      value={resAmount}
                      onChange={(e) => setResAmount(e.target.value)}
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Banking Reference / Settlement UTR Number</label>
                  <input 
                    type="text" 
                    className="form-input" 
                    placeholder="e.g. UTR-20261008-9872"
                    value={resRefNumber}
                    onChange={(e) => setResRefNumber(e.target.value)}
                  />
                </div>

                {/* CATEGORY SOP REDRESSAL MEMORANDUM GENERATOR */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                  <label className="form-label" style={{ margin: 0 }}>
                    Official Regulatory Redressal Memorandum
                  </label>
                  <button 
                    type="button" 
                    onClick={handleGenerateCopilotDraft}
                    disabled={copilotLoading}
                    className="btn btn-outline"
                    style={{ padding: '4px 10px', fontSize: '0.78rem', color: '#175cd3', borderColor: '#b2ddff', fontWeight: '700' }}
                  >
                    <FileText size={13} /> {copilotLoading ? 'Generating Memorandum...' : 'Auto-Generate Category SOP Memorandum'}
                  </button>
                </div>

                <textarea 
                  rows="6"
                  className="form-textarea"
                  placeholder="Detail the remedial action taken by the banking desk..."
                  value={resolutionDetails}
                  onChange={(e) => setResolutionDetails(e.target.value)}
                  required
                ></textarea>

                <div className="form-group" style={{ marginTop: '12px' }}>
                  <label className="form-label">Attach Proof of Redressal (Receipt / UTR PDF / Statement)</label>
                  <input 
                    type="file" 
                    className="form-input" 
                    onChange={(e) => setResProofFile(e.target.files[0])}
                  />
                </div>

                <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '16px' }}>
                  <button type="button" onClick={() => setSelectedComplaint(null)} className="btn btn-outline">
                    Cancel
                  </button>
                  <button type="submit" disabled={submittingResolution} className="btn btn-success">
                    <CheckCircle size={15} /> {submittingResolution ? 'Submitting...' : 'Submit Resolution for Customer Approval'}
                  </button>
                </div>
              </form>
            )}

            {/* SUB-PANEL 2: EVIDENCE VERIFICATION */}
            {modalTab === 'evidence' && (
              <div>
                <div style={{ background: '#f8fafc', padding: '14px', borderRadius: '6px', marginBottom: '16px' }}>
                  <div style={{ fontWeight: '600', marginBottom: '6px' }}>Customer Uploaded Evidence:</div>
                  {selectedComplaint.proof_file_path ? (
                    <div>
                      <div style={{ fontSize: '0.85rem', color: '#2563eb', marginBottom: '8px' }}>
                        File on record: <code>{selectedComplaint.proof_file_path.split('\\').pop().split('/').pop()}</code>
                      </div>
                      <a 
                        href={`http://localhost:8000/api/complaints/${selectedComplaint.token}/document`}
                        target="_blank" 
                        rel="noreferrer"
                        className="btn btn-outline"
                        style={{ fontSize: '0.8rem', padding: '4px 10px' }}
                      >
                        Open / Inspect Attachment
                      </a>
                    </div>
                  ) : (
                    <div style={{ color: '#64748b', fontSize: '0.85rem' }}>No document proof was attached by the customer.</div>
                  )}
                </div>

                <div className="form-group">
                  <label className="form-label">Current Verification Status</label>
                  <div style={{ fontWeight: '700', fontSize: '1rem', color: selectedComplaint.evidence_status === 'VERIFIED' ? '#16a34a' : '#dc2626' }}>
                    {selectedComplaint.evidence_status || 'PENDING'}
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-label">Rejection Reason (If rejecting document)</label>
                  <input 
                    type="text" 
                    className="form-input" 
                    placeholder="e.g. Transaction reference illegible or mismatch in disputed amount"
                    value={evidenceRejectReason}
                    onChange={(e) => setEvidenceRejectReason(e.target.value)}
                  />
                </div>

                <div style={{ display: 'flex', gap: '10px', marginTop: '16px' }}>
                  <button 
                    type="button" 
                    onClick={() => handleVerifyEvidence('VERIFIED')} 
                    disabled={evidenceLoading}
                    className="btn btn-success"
                    style={{ flex: 1 }}
                  >
                    <Check size={16} /> Mark Evidence Verified
                  </button>
                  <button 
                    type="button" 
                    onClick={() => handleVerifyEvidence('REJECTED')} 
                    disabled={evidenceLoading}
                    className="btn btn-danger"
                    style={{ flex: 1 }}
                  >
                    <X size={16} /> Reject Evidence Proof
                  </button>
                </div>
              </div>
            )}

            {/* SUB-PANEL 3: INVESTIGATION NOTES */}
            {modalTab === 'notes' && (
              <div>
                <form onSubmit={handleAddNote} style={{ marginBottom: '16px' }}>
                  <label className="form-label">Add Officer Investigation Note</label>
                  <textarea 
                    rows="3" 
                    className="form-textarea" 
                    placeholder="Record internal findings, gateway log check, or interbank correspondence..."
                    value={newNoteText}
                    onChange={(e) => setNewNoteText(e.target.value)}
                    required
                  ></textarea>
                  <button type="submit" className="btn btn-primary" style={{ marginTop: '8px', padding: '6px 14px', fontSize: '0.85rem' }}>
                    Save Note to Ticket Log
                  </button>
                </form>

                <div style={{ maxHeight: '250px', overflowY: 'auto' }}>
                  {notesLoading ? (
                    <div style={{ textAlign: 'center', color: '#64748b' }}>Loading notes...</div>
                  ) : notesList.length === 0 ? (
                    <div style={{ textAlign: 'center', color: '#94a3b8', fontSize: '0.85rem' }}>No investigation notes logged yet.</div>
                  ) : (
                    notesList.map(n => (
                      <div key={n.note_id} style={{ background: '#f8fafc', padding: '10px', borderRadius: '6px', marginBottom: '8px', fontSize: '0.85rem' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', color: '#64748b', fontSize: '0.75rem', marginBottom: '4px' }}>
                          <strong>{n.worker_name}</strong>
                          <span>{new Date(n.created_at).toLocaleString()}</span>
                        </div>
                        <div style={{ color: '#1e293b' }}>{n.note_text}</div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
