import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Link, useNavigate } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import {
  FileText, Clock, CheckCircle2, AlertTriangle, Search, RefreshCw,
  Eye, ChevronDown, ChevronUp, Building2, ThumbsUp, ThumbsDown,
  Download, RotateCcw, AlertCircle, XCircle, IndianRupee, Calendar,
  Hash, MapPin, Shield
} from 'lucide-react';

const getAuthHeaders = () => {
  const token = localStorage.getItem('grievanceiq_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

const STATUS_CONFIG = {
  open:                { label: 'Open',                bg: '#eff6ff', color: '#1d4ed8', dot: '#3b82f6' },
  in_progress:         { label: 'In Progress',         bg: '#e0f2fe', color: '#0369a1', dot: '#0284c7' },
  escalated:           { label: 'Escalated',           bg: '#fff7ed', color: '#c2410c', dot: '#f97316' },
  resolved:            { label: 'Resolved',            bg: '#f0fdf4', color: '#15803d', dot: '#22c55e' },
  closed:              { label: 'Closed',              bg: '#f8fafc', color: '#475569', dot: '#94a3b8' },
  reopened:            { label: 'Reopened',            bg: '#fef2f2', color: '#b91c1c', dot: '#ef4444' },
  resolution_proposed: { label: 'Resolution Proposed', bg: '#faf5ff', color: '#7c3aed', dot: '#8b5cf6' },
};

const PRIORITY_CONFIG = {
  High:   { bg: '#fef2f2', color: '#b91c1c', border: '#fca5a5' },
  Medium: { bg: '#fffbeb', color: '#92400e', border: '#fcd34d' },
  Low:    { bg: '#f0fdf4', color: '#15803d', border: '#86efac' },
};

export default function CustomerHistory() {
  const { t } = useLanguage();
  const navigate = useNavigate();
  const authToken = localStorage.getItem('grievanceiq_token');
  const user = JSON.parse(localStorage.getItem('grievanceiq_user') || '{}');

  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('ALL');
  const [searchText, setSearchText] = useState('');
  const [expandedToken, setExpandedToken] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);
  const [actionMsg, setActionMsg] = useState(null);
  const [reopenModal, setReopenModal] = useState(null); // token or null
  const [reopenReason, setReopenReason] = useState('');

  useEffect(() => {
    if (!authToken) { navigate('/login'); return; }
    fetchHistory();
  }, [authToken]);

  const fetchHistory = useCallback(() => {
    setLoading(true);
    axios.get('/api/customer/complaints', { headers: getAuthHeaders() })
      .then(res => setComplaints(res.data))
      .catch(err => {
        if (err.response?.status === 401) {
          localStorage.removeItem('grievanceiq_token');
          navigate('/login');
        }
      })
      .finally(() => setLoading(false));
  }, []);

  const filtered = complaints.filter(c => {
    const statusMatch =
      filterStatus === 'ALL' ? true :
      filterStatus === 'ACTIVE' ? !['resolved', 'closed'].includes(c.status) :
      filterStatus === 'RESOLVED' ? c.status === 'resolved' :
      filterStatus === 'PENDING_ACTION' ? c.status === 'resolution_proposed' :
      true;

    const searchMatch = !searchText.trim() ||
      c.token?.toLowerCase().includes(searchText.toLowerCase()) ||
      c.company_name?.toLowerCase().includes(searchText.toLowerCase()) ||
      c.service_type?.toLowerCase().includes(searchText.toLowerCase());

    return statusMatch && searchMatch;
  });

  const handleConfirmResolution = async (token, confirmed) => {
    setActionLoading(true);
    setActionMsg(null);
    try {
      const res = await axios.post(`/api/complaints/${token}/confirm-resolution`, {
        confirmed,
        feedback_or_reason: confirmed ? 'Customer confirmed resolution as satisfactory.' : reopenReason || 'Not satisfied with proposed resolution.',
      }, { headers: getAuthHeaders() });
      setActionMsg({ type: 'success', text: res.data.message });
      setReopenModal(null);
      setReopenReason('');
      fetchHistory();
    } catch (err) {
      setActionMsg({ type: 'error', text: err.response?.data?.detail || 'Action failed.' });
    } finally {
      setActionLoading(false);
    }
  };

  const handleReopen = async (token) => {
    if (!reopenReason.trim()) return;
    setActionLoading(true);
    setActionMsg(null);
    try {
      const res = await axios.post(`/api/complaints/${token}/reopen`, {
        reopen_reason: reopenReason,
      }, { headers: getAuthHeaders() });
      setActionMsg({ type: 'success', text: res.data.message });
      setReopenModal(null);
      setReopenReason('');
      fetchHistory();
    } catch (err) {
      setActionMsg({ type: 'error', text: err.response?.data?.detail || 'Could not reopen complaint.' });
    } finally {
      setActionLoading(false);
    }
  };

  const canReopen = (c) => {
    if (c.status !== 'resolved') return false;
    if ((c.reopen_count || 0) >= 2) return false;
    if (c.can_reopen_until) return new Date(c.can_reopen_until) > new Date();
    return false;
  };

  const stats = {
    total: complaints.length,
    active: complaints.filter(c => !['resolved', 'closed'].includes(c.status)).length,
    resolved: complaints.filter(c => c.status === 'resolved').length,
    pendingAction: complaints.filter(c => c.status === 'resolution_proposed').length,
  };

  return (
    <div className="container" style={{ maxWidth: '1100px' }}>

      {/* ── Header ───────────────────────────────────────────────── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
        <div>
          <h1 style={{ fontSize: '1.55rem', fontWeight: '800', color: '#0f172a', margin: '0 0 4px 0' }}>
            {t('history_title')}
          </h1>
          <p style={{ color: '#64748b', fontSize: '0.875rem', margin: 0 }}>
            {t('history_subtitle')}
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <Link to="/submit" className="btn btn-primary" style={{ padding: '9px 18px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
            + New Complaint
          </Link>
          <button onClick={fetchHistory} style={{ padding: '9px 14px', border: '1px solid #e2e8f0', borderRadius: '8px', background: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.82rem', color: '#475569' }}>
            <RefreshCw size={14} /> Refresh
          </button>
        </div>
      </div>

      {/* ── Stats Row ─────────────────────────────────────────────── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px', marginBottom: '24px' }}>
        {[
          { label: t('total_complaints'), value: stats.total, color: '#3b82f6', bg: '#eff6ff' },
          { label: t('active_cases'), value: stats.active, color: '#f59e0b', bg: '#fffbeb' },
          { label: t('resolved_cases'), value: stats.resolved, color: '#16a34a', bg: '#f0fdf4' },
          { label: t('action_needed'), value: stats.pendingAction, color: '#7c3aed', bg: '#faf5ff' },
        ].map((s, i) => (
          <div key={i} style={{ background: s.bg, border: `1px solid ${s.color}30`, borderRadius: '10px', padding: '14px 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontSize: '1.8rem', fontWeight: '800', color: s.color, lineHeight: 1 }}>{s.value}</div>
              <div style={{ fontSize: '0.72rem', color: '#64748b', fontWeight: '600', textTransform: 'uppercase', letterSpacing: '0.05em', marginTop: '4px' }}>{s.label}</div>
            </div>
            {s.label === 'Awaiting Your Response' && s.value > 0 && (
              <div style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#7c3aed', animation: 'pulse 1.5s infinite' }} />
            )}
          </div>
        ))}
      </div>

      {/* ── Action Alert ──────────────────────────────────────────── */}
      {actionMsg && (
        <div style={{ padding: '12px 16px', background: actionMsg.type === 'success' ? '#f0fdf4' : '#fef2f2', border: `1px solid ${actionMsg.type === 'success' ? '#bbf7d0' : '#fecaca'}`, borderRadius: '8px', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.875rem', fontWeight: '600', color: actionMsg.type === 'success' ? '#166534' : '#991b1b' }}>
          {actionMsg.type === 'success' ? <CheckCircle2 size={15} /> : <AlertCircle size={15} />}
          {actionMsg.text}
          <button onClick={() => setActionMsg(null)} style={{ marginLeft: 'auto', background: 'none', border: 'none', cursor: 'pointer', color: 'inherit', opacity: 0.7 }}>✕</button>
        </div>
      )}

      {/* ── Filters & Search ──────────────────────────────────────── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {[
            { key: 'ALL', label: `All (${stats.total})` },
            { key: 'ACTIVE', label: `Active (${stats.active})` },
            { key: 'PENDING_ACTION', label: `Action Needed (${stats.pendingAction})` },
            { key: 'RESOLVED', label: `Resolved (${stats.resolved})` },
          ].map(f => (
            <button key={f.key} onClick={() => setFilterStatus(f.key)}
              style={{ padding: '7px 14px', border: '1.5px solid', borderRadius: '6px', cursor: 'pointer', fontSize: '0.82rem', fontWeight: '600', transition: 'all 0.15s',
                background: filterStatus === f.key ? '#1e40af' : 'white',
                color: filterStatus === f.key ? 'white' : '#475569',
                borderColor: filterStatus === f.key ? '#1e40af' : '#d1d5db',
              }}>
              {f.label}
            </button>
          ))}
        </div>
        <div style={{ position: 'relative', flex: '0 0 240px' }}>
          <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: '#9ca3af' }} />
          <input type="text" value={searchText} onChange={e => setSearchText(e.target.value)}
            placeholder="Search by token, bank, type..."
            style={{ width: '100%', paddingLeft: '32px', paddingRight: '12px', paddingTop: '8px', paddingBottom: '8px', border: '1.5px solid #d1d5db', borderRadius: '6px', fontSize: '0.82rem', boxSizing: 'border-box' }} />
        </div>
      </div>

      {/* ── Complaint Cards ───────────────────────────────────────── */}
      {loading ? (
        <div style={{ textAlign: 'center', padding: '60px', color: '#64748b' }}>
          <div style={{ width: '36px', height: '36px', border: '3px solid #e2e8f0', borderTopColor: '#1e40af', borderRadius: '50%', animation: 'spin 0.8s linear infinite', margin: '0 auto 12px' }} />
          <div style={{ fontWeight: '600' }}>Loading your complaint history...</div>
        </div>
      ) : filtered.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '60px 20px', color: '#64748b', background: 'white', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
          <FileText size={48} color="#cbd5e1" style={{ marginBottom: '12px' }} />
          <h3 style={{ fontSize: '1.1rem', fontWeight: '700', color: '#334155', marginBottom: '6px' }}>No complaints found</h3>
          <p style={{ fontSize: '0.875rem', marginBottom: '18px' }}>
            {searchText ? 'No complaints match your search.' : "You haven't filed any complaints matching this filter yet."}
          </p>
          <Link to="/submit" className="btn btn-primary" style={{ fontSize: '0.875rem' }}>
            Submit a Complaint Now
          </Link>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {filtered.map(c => {
            const statusCfg = STATUS_CONFIG[c.status] || STATUS_CONFIG.open;
            const priorityCfg = PRIORITY_CONFIG[c.priority] || PRIORITY_CONFIG.Medium;
            const isExpanded = expandedToken === c.token;
            const hasResolutionProposed = c.status === 'resolution_proposed' && c.latest_resolution;
            const isResolved = c.status === 'resolved';

            return (
              <div key={c.token} style={{ background: 'white', borderRadius: '10px', border: `1px solid ${hasResolutionProposed ? '#c4b5fd' : '#e2e8f0'}`, overflow: 'hidden', transition: 'box-shadow 0.2s' }}>
                {/* Attention banner for resolution proposed */}
                {hasResolutionProposed && (
                  <div style={{ padding: '8px 16px', background: '#faf5ff', borderBottom: '1px solid #e9d5ff', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <AlertCircle size={14} color="#7c3aed" />
                    <span style={{ fontSize: '0.8rem', fontWeight: '700', color: '#7c3aed' }}>
                      Action Required — A resolution has been proposed. Please review and confirm or dispute it.
                    </span>
                  </div>
                )}

                {/* Card Header (always visible) */}
                <div style={{ padding: '16px 18px', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '10px' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px', flexWrap: 'wrap' }}>
                      <span style={{ fontFamily: 'monospace', fontWeight: '800', fontSize: '0.9rem', color: '#1e40af' }}>{c.token}</span>
                      <span style={{ padding: '3px 10px', borderRadius: '999px', fontSize: '0.72rem', fontWeight: '700', background: statusCfg.bg, color: statusCfg.color }}>
                        <span style={{ display: 'inline-block', width: '6px', height: '6px', borderRadius: '50%', background: statusCfg.dot, marginRight: '5px', verticalAlign: 'middle' }} />
                        {statusCfg.label}
                      </span>
                      <span style={{ padding: '3px 10px', borderRadius: '999px', fontSize: '0.72rem', fontWeight: '700', background: priorityCfg.bg, color: priorityCfg.color, border: `1px solid ${priorityCfg.border}` }}>
                        {c.priority} Priority
                      </span>
                      {c.sla?.overdue && <span style={{ padding: '3px 10px', borderRadius: '999px', fontSize: '0.72rem', fontWeight: '700', background: '#fee2e2', color: '#b91c1c' }}>⚠ SLA Breached</span>}
                    </div>
                    <div style={{ fontWeight: '600', color: '#0f172a', fontSize: '0.9rem', marginBottom: '3px' }}>{c.service_type}</div>
                    <div style={{ fontSize: '0.8rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
                      <span><Building2 size={11} style={{ verticalAlign: 'middle', marginRight: '4px' }} />{c.company_name}</span>
                      {c.amount && <span><IndianRupee size={11} style={{ verticalAlign: 'middle', marginRight: '2px' }} />₹{Number(c.amount).toLocaleString('en-IN')}</span>}
                      <span><Calendar size={11} style={{ verticalAlign: 'middle', marginRight: '4px' }} />{new Date(c.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</span>
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <Link to={`/track?token=${c.token}`}
                      style={{ padding: '7px 14px', border: '1px solid #d1d5db', borderRadius: '6px', background: 'white', color: '#374151', fontSize: '0.8rem', fontWeight: '600', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '5px' }}>
                      <Eye size={13} /> Track
                    </Link>
                    <button onClick={() => setExpandedToken(isExpanded ? null : c.token)}
                      style={{ padding: '7px 12px', border: '1px solid #d1d5db', borderRadius: '6px', background: isExpanded ? '#f1f5f9' : 'white', color: '#374151', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem', fontWeight: '600' }}>
                      {isExpanded ? <><ChevronUp size={14} /> Less</> : <><ChevronDown size={14} /> Details</>}
                    </button>
                  </div>
                </div>

                {/* Expanded Details */}
                {isExpanded && (
                  <div style={{ borderTop: '1px solid #f1f5f9', padding: '16px 18px', background: '#fafafa' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '10px 20px', marginBottom: '16px' }}>
                      {c.description && (
                        <div style={{ gridColumn: '1 / -1' }}>
                          <div style={{ fontSize: '0.72rem', fontWeight: '700', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '4px' }}>Complaint Description</div>
                          <div style={{ fontSize: '0.85rem', color: '#374151', lineHeight: '1.5', background: 'white', padding: '10px 12px', borderRadius: '6px', border: '1px solid #e2e8f0' }}>{c.description}</div>
                        </div>
                      )}
                      {c.reference_id && (
                        <div>
                          <div style={{ fontSize: '0.72rem', fontWeight: '700', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '3px' }}><Hash size={10} style={{ marginRight: '3px', verticalAlign: 'middle' }} />Reference / UTR</div>
                          <div style={{ fontFamily: 'monospace', fontSize: '0.85rem', fontWeight: '700', color: '#0f172a' }}>{c.reference_id}</div>
                        </div>
                      )}
                      {c.transaction_date && (
                        <div>
                          <div style={{ fontSize: '0.72rem', fontWeight: '700', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '3px' }}>Transaction Date</div>
                          <div style={{ fontSize: '0.85rem', color: '#0f172a' }}>{c.transaction_date}</div>
                        </div>
                      )}
                      {c.branch && (
                        <div>
                          <div style={{ fontSize: '0.72rem', fontWeight: '700', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '3px' }}><MapPin size={10} style={{ marginRight: '3px', verticalAlign: 'middle' }} />Branch / City</div>
                          <div style={{ fontSize: '0.85rem', color: '#0f172a' }}>{c.branch}</div>
                        </div>
                      )}
                      <div>
                        <div style={{ fontSize: '0.72rem', fontWeight: '700', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '3px' }}><Shield size={10} style={{ marginRight: '3px', verticalAlign: 'middle' }} />Document Status</div>
                        <div style={{ fontSize: '0.85rem', color: c.evidence_status === 'VERIFIED' ? '#16a34a' : c.evidence_status === 'REJECTED' ? '#dc2626' : '#92400e', fontWeight: '600' }}>
                          {c.evidence_status}
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: '0.72rem', fontWeight: '700', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '3px' }}>Validity Score</div>
                        <div style={{ fontSize: '0.85rem', fontWeight: '700', color: (c.validity_score || 0) >= 70 ? '#16a34a' : '#f59e0b' }}>{c.validity_score || 0}/100</div>
                      </div>
                    </div>

                    {/* Resolution info if resolved */}
                    {c.resolution_notes && (
                      <div style={{ background: '#f0fdf4', border: '1px solid #86efac', borderRadius: '10px', padding: '16px', marginBottom: '14px', boxShadow: '0 2px 8px rgba(34, 197, 94, 0.08)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', flexWrap: 'wrap', gap: '8px' }}>
                          <div style={{ fontWeight: '800', fontSize: '0.9rem', color: '#166534', display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <CheckCircle2 size={18} color="#16a34a" /> 
                            <span>Official Redressal Memorandum & Settlement Advice</span>
                          </div>
                          <span style={{ background: '#dcfce7', color: '#15803d', border: '1px solid #bbf7d0', padding: '3px 10px', borderRadius: '12px', fontSize: '0.74rem', fontWeight: '800' }}>
                            {c.resolution_mode === 'BOT' ? '🤖 NOVA-AI AUTONOMOUS RESOLUTION' : '👤 OFFICER SETTLED'}
                          </span>
                        </div>
                        
                        <div style={{ fontSize: '0.88rem', color: '#1e3a1e', lineHeight: '1.6', background: 'white', padding: '14px', borderRadius: '8px', border: '1px solid #dcfce7' }}>
                          {c.resolution_notes}
                        </div>

                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '10px', fontSize: '0.78rem', color: '#15803d', flexWrap: 'wrap', gap: '6px' }}>
                          <span>
                            ⚖️ <strong>Regulatory Framework:</strong> RBI Turn Around Time (TAT) Framework & Auto-reversal Mandate
                          </span>
                          {c.resolved_at && (
                            <span>
                              Resolved on {new Date(c.resolved_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                            </span>
                          )}
                        </div>
                      </div>
                    )}

                    {/* Resolution proposed — confirm or dispute */}
                    {hasResolutionProposed && (
                      <div style={{ background: '#faf5ff', border: '1px solid #d8b4fe', borderRadius: '8px', padding: '14px 16px', marginBottom: '12px' }}>
                        <div style={{ fontWeight: '700', fontSize: '0.85rem', color: '#7c3aed', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <AlertCircle size={14} /> Proposed Resolution from Banking Officer
                        </div>
                        <div style={{ fontSize: '0.85rem', color: '#374151', lineHeight: '1.5', marginBottom: '10px' }}>
                          {c.latest_resolution.resolution_details}
                        </div>
                        {c.latest_resolution.resolved_amount && (
                          <div style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '4px' }}>
                            <strong>Amount:</strong> ₹{Number(c.latest_resolution.resolved_amount).toLocaleString('en-IN')}
                          </div>
                        )}
                        {c.latest_resolution.transaction_reference && (
                          <div style={{ fontSize: '0.82rem', color: '#64748b', marginBottom: '10px' }}>
                            <strong>Ref:</strong> <span style={{ fontFamily: 'monospace' }}>{c.latest_resolution.transaction_reference}</span>
                          </div>
                        )}
                        {c.latest_resolution.resolution_proof_path && (
                          <a href={`/uploads/${c.latest_resolution.resolution_proof_path.split('/').pop()}`} target="_blank" rel="noreferrer"
                            style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '7px 14px', background: '#ede9fe', color: '#6d28d9', border: '1px solid #c4b5fd', borderRadius: '6px', fontSize: '0.8rem', fontWeight: '700', textDecoration: 'none', marginBottom: '14px' }}>
                            <Download size={13} /> Download Resolution Proof
                          </a>
                        )}
                        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                          <button onClick={() => handleConfirmResolution(c.token, true)} disabled={actionLoading}
                            style={{ padding: '9px 20px', background: '#16a34a', color: 'white', border: 'none', borderRadius: '7px', cursor: 'pointer', fontWeight: '700', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <ThumbsUp size={14} /> Accept — Mark as Resolved
                          </button>
                          <button onClick={() => { setReopenModal(c.token); setReopenReason(''); }} disabled={actionLoading}
                            style={{ padding: '9px 20px', background: 'white', color: '#dc2626', border: '1.5px solid #fca5a5', borderRadius: '7px', cursor: 'pointer', fontWeight: '700', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <ThumbsDown size={14} /> Dispute — Request Re-investigation
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Reopen button for resolved complaints */}
                    {isResolved && canReopen(c) && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                        <button onClick={() => { setReopenModal(`reopen_${c.token}`); setReopenReason(''); }}
                          style={{ padding: '8px 16px', background: 'white', color: '#f97316', border: '1.5px solid #fed7aa', borderRadius: '7px', cursor: 'pointer', fontWeight: '700', fontSize: '0.82rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <RotateCcw size={13} /> Reopen Complaint
                        </button>
                        <span style={{ fontSize: '0.75rem', color: '#94a3b8' }}>
                          Can reopen until {new Date(c.can_reopen_until).toLocaleDateString('en-IN')} &bull; {2 - (c.reopen_count || 0)} attempt(s) remaining
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* ── Reopen / Dispute Modal ────────────────────────────────── */}
      {reopenModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
          <div style={{ background: 'white', borderRadius: '12px', padding: '28px', maxWidth: '500px', width: '100%', boxShadow: '0 25px 50px rgba(0,0,0,0.25)' }}>
            <h3 style={{ fontSize: '1.1rem', fontWeight: '800', color: '#0f172a', marginTop: 0, marginBottom: '6px' }}>
              {reopenModal.startsWith('reopen_') ? 'Reopen Complaint' : 'Dispute Proposed Resolution'}
            </h3>
            <p style={{ color: '#64748b', fontSize: '0.875rem', marginBottom: '16px', lineHeight: '1.5' }}>
              {reopenModal.startsWith('reopen_')
                ? 'Provide a reason for reopening this complaint. It will be re-investigated by a senior nodal officer.'
                : 'Please describe why the proposed resolution is unsatisfactory. The case will be escalated for re-investigation.'}
            </p>
            <textarea
              value={reopenReason}
              onChange={e => setReopenReason(e.target.value)}
              rows={4}
              placeholder="e.g. The refund amount is incorrect / The issue persists / I was not informed about this resolution..."
              style={{ width: '100%', padding: '10px 12px', border: '1.5px solid #d1d5db', borderRadius: '8px', fontSize: '0.875rem', resize: 'vertical', boxSizing: 'border-box', lineHeight: '1.5' }}
            />
            <div style={{ display: 'flex', gap: '10px', marginTop: '16px' }}>
              <button
                onClick={() => {
                  const token = reopenModal.replace('reopen_', '');
                  if (reopenModal.startsWith('reopen_')) handleReopen(token);
                  else handleConfirmResolution(token, false);
                }}
                disabled={actionLoading || !reopenReason.trim()}
                style={{ flex: 1, padding: '11px', background: '#dc2626', color: 'white', border: 'none', borderRadius: '8px', fontWeight: '700', cursor: (actionLoading || !reopenReason.trim()) ? 'not-allowed' : 'pointer', opacity: (actionLoading || !reopenReason.trim()) ? 0.6 : 1, fontSize: '0.875rem' }}>
                {actionLoading ? 'Submitting...' : (reopenModal.startsWith('reopen_') ? 'Submit Reopen Request' : 'Dispute Resolution')}
              </button>
              <button onClick={() => { setReopenModal(null); setReopenReason(''); }}
                style={{ padding: '11px 20px', background: '#f1f5f9', color: '#374151', border: 'none', borderRadius: '8px', fontWeight: '600', cursor: 'pointer', fontSize: '0.875rem' }}>
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
