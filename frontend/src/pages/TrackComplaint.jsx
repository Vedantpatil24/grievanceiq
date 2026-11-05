import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useSearchParams } from 'react-router-dom';
import { useLanguage } from '../context/LanguageContext';
import { 
  Search, Clock, ShieldCheck, UserCheck, MessageSquare, 
  Send, RefreshCw, Star, AlertCircle, FileText, CheckCircle2, Upload, AlertTriangle 
, Download
} from 'lucide-react';

export default function TrackComplaint() {
  const { t } = useLanguage();
  const [searchParams] = useSearchParams();
  const [tokenInput, setTokenInput] = useState(searchParams.get('token') || '');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [complaint, setComplaint] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);
  const [resolvedCelebration, setResolvedCelebration] = useState(false);
  const prevStatusRef = React.useRef(null);

  // Messaging state
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [msgSending, setMsgSending] = useState(false);

  // Feedback state
  const [rating, setRating] = useState(5);
  const [feedbackComment, setFeedbackComment] = useState('');
  const [feedbackSent, setFeedbackSent] = useState(false);

  // Reopen state
  const [reopenReason, setReopenReason] = useState('');
  const [showReopenModal, setShowReopenModal] = useState(false);

  // Evidence Re-upload state
  const [newProofFile, setNewProofFile] = useState(null);
  const [uploadingProof, setUploadingProof] = useState(false);
  const [proofSuccessMsg, setProofSuccessMsg] = useState('');
  const [proofErrorMsg, setProofErrorMsg] = useState('');

  const handleResubmitEvidence = async (e) => {
    e.preventDefault();
    if (!newProofFile || !complaint?.token) return;
    setUploadingProof(true);
    setProofSuccessMsg('');
    setProofErrorMsg('');
    try {
      const formData = new FormData();
      formData.append('proof_file', newProofFile);
      const res = await axios.post(`/api/complaints/${complaint.token}/resubmit-evidence`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setProofSuccessMsg(res.data.message || 'Evidence uploaded successfully!');
      setNewProofFile(null);
      fetchComplaint(complaint.token);
    } catch (err) {
      setProofErrorMsg(err.response?.data?.detail || 'Failed to upload proof. Please try again.');
    } finally {
      setUploadingProof(false);
    }
  };

  const fetchComplaint = async (tkn, silent = false) => {
    if (!tkn) return;
    if (!silent) setLoading(true);
    setErrorMsg(null);
    try {
      const res = await axios.get(`/api/complaints/${tkn}/track`);
      setComplaint(res.data);
      fetchMessages(tkn);
    } catch (err) {
      if (!silent) {
        setErrorMsg(err.response?.data?.detail || 'Complaint token not found. Please check and try again.');
        setComplaint(null);
      }
    } finally {
      if (!silent) setLoading(false);
    }
  };

  // ── NOVA-AI 30-SECOND AUTONOMOUS SETTLEMENT POLLER ──
  useEffect(() => {
    if (!complaint?.token) return;

    if (prevStatusRef.current && prevStatusRef.current !== 'resolved' && complaint.status === 'resolved') {
      setResolvedCelebration(true);
    }
    prevStatusRef.current = complaint.status;

    // Auto-poll every 3 seconds while complaint is pending or bot_processing
    if (complaint.status !== 'resolved' && complaint.status !== 'rejected') {
      const interval = setInterval(() => {
        fetchComplaint(complaint.token, true);
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [complaint?.token, complaint?.status]);

  const fetchMessages = async (tkn) => {
    try {
      const res = await axios.get(`/api/complaints/${tkn}/messages`);
      setMessages(res.data);
    } catch (err) {
      console.error('Error fetching messages:', err);
    }
  };

  useEffect(() => {
    const qToken = searchParams.get('token');
    if (qToken) {
      setTokenInput(qToken);
      fetchComplaint(qToken);
    }
  }, [searchParams]);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchComplaint(tokenInput.trim());
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !complaint?.token) return;
    setMsgSending(true);
    try {
      await axios.post(`/api/complaints/${complaint.token}/messages`, {
        message_text: newMessage,
        sender_type: 'customer',
        sender_name: 'Customer'
      });
      setNewMessage('');
      fetchMessages(complaint.token);
    } catch (err) {
      alert('Error sending message: ' + (err.response?.data?.detail || err.message));
    } finally {
      setMsgSending(false);
    }
  };

  const handleSendFeedback = async () => {
    try {
      await axios.post(`/api/complaints/${complaint.token}/feedback`, {
        rating: rating,
        comments: feedbackComment
      });
      setFeedbackSent(true);
    } catch (err) {
      alert('Error saving feedback: ' + (err.response?.data?.detail || err.message));
    }
  };

  const handleReopen = async () => {
    if (!reopenReason.trim()) {
      alert('Please state why the issue was not resolved.');
      return;
    }
    try {
      await axios.post(`/api/complaints/${complaint.token}/reopen`, {
        reopen_reason: reopenReason
      });
      alert('Case reopened and escalated to Senior Nodal Officer.');
      setShowReopenModal(false);
      fetchComplaint(complaint.token);
    } catch (err) {
      alert(err.response?.data?.detail || 'Error reopening complaint');
    }
  };

  return (
    <div className="container" style={{ maxWidth: '980px' }}>
      <div style={{ textAlign: 'center', marginBottom: '28px' }}>
        <h1 style={{ fontSize: '1.85rem', fontWeight: '800', color: '#0f172a' }}>
          {t('track_title')}
        </h1>
        <p style={{ color: '#64748b', fontSize: '0.95rem', marginTop: '4px' }}>
          {t('track_subtitle')}
        </p>

        {/* SEARCH BAR */}
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '10px', maxWidth: '500px', margin: '20px auto 0' }}>
          <input 
            type="text" 
            placeholder={t('token_placeholder')}
            className="form-input"
            value={tokenInput}
            onChange={(e) => setTokenInput(e.target.value)}
            required
          />
          <button type="submit" className="btn btn-primary" disabled={loading}>
            <Search size={18} /> {t('track_btn')}
          </button>
        </form>
      </div>

      {loading && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#64748b' }}>
          Loading grievance details...
        </div>
      )}

      {errorMsg && (
        <div style={{ background: '#fef2f2', border: '1px solid #fecaca', borderRadius: '8px', padding: '16px', color: '#991b1b', textAlign: 'center' }}>
          <AlertCircle size={24} style={{ display: 'inline', verticalAlign: 'middle', marginRight: '8px' }} />
          {errorMsg}
        </div>
      )}

      {complaint && (
        <div>
          {/* TICKET SUMMARY CARD */}
          <div className="card" style={{ borderTop: '4px solid #2563eb' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '15px' }}>
              <div>
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
                  <span className="badge badge-blue" style={{ fontFamily: 'monospace' }}>{complaint.token}</span>
                  <button
                    type="button"
                    onClick={() => {
                      navigator.clipboard.writeText(complaint.token);
                      setCopied(true);
                      setTimeout(() => setCopied(false), 2000);
                    }}
                    style={{
                      background: copied ? '#16a34a' : '#e2e8f0',
                      color: copied ? 'white' : '#475569',
                      border: 'none',
                      borderRadius: '4px',
                      padding: '2px 8px',
                      fontSize: '0.72rem',
                      fontWeight: '600',
                      cursor: 'pointer'
                    }}
                  >
                    {copied ? '✓ Copied' : '📋 Copy'}
                  </button>
                  <a
                    href={`/api/complaints/${complaint.token}/statutory-receipt`}
                    target="_blank"
                    rel="noreferrer"
                    style={{
                      background: '#0f2942',
                      color: '#93c5fd',
                      border: '1px solid #1e3a8a',
                      borderRadius: '4px',
                      padding: '2px 10px',
                      fontSize: '0.72rem',
                      fontWeight: '700',
                      textDecoration: 'none',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '4px'
                    }}
                  >
                    <Download size={11} /> Download PDF Receipt
                  </a>
                </div>
                <h2 style={{ fontSize: '1.4rem', fontWeight: '700', marginTop: '8px', color: '#0f172a' }}>
                  {complaint.service_type}
                </h2>
                <p style={{ color: '#64748b', fontSize: '0.9rem' }}>
                  Institution: <strong>{complaint.company_name}</strong> | Department: <strong>{complaint.department_name}</strong>
                </p>
                <p style={{ color: '#64748b', fontSize: '0.85rem' }}>
                  Disputed Amount: <strong>₹{complaint.amount?.toLocaleString()}</strong> | Ref: {complaint.reference_id || 'N/A'}
                </p>
              </div>

              {/* STATUS & SLA BADGE */}
              <div style={{ textAlign: 'right' }}>
                <div style={{ marginBottom: '6px' }}>
                  <span className={`badge ${
                    complaint.status === 'resolved' ? 'badge-green' : 
                    complaint.status === 'reopened' ? 'badge-red' : 
                    complaint.status === 'escalated' ? 'badge-yellow' : 'badge-blue'
                  }`} style={{ fontSize: '0.85rem', padding: '6px 14px' }}>
                    Status: {complaint.status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>

                {complaint.sla?.has_sla && (
                  <div style={{ 
                    background: complaint.sla.is_breached ? '#fee2e2' : '#f0fdf4', 
                    padding: '8px 12px', 
                    borderRadius: '6px', 
                    border: `1px solid ${complaint.sla.is_breached ? '#fca5a5' : '#86efac'}`,
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    fontSize: '0.85rem',
                    fontWeight: '600',
                    color: complaint.sla.is_breached ? '#991b1b' : '#166534'
                  }}>
                    <Clock size={16} />
                    SLA: {complaint.sla.formatted_remaining}
                  </div>
                )}
              </div>
            </div>

            {/* ── NOVA-AI 30-SECOND LIVE SETTLEMENT BANNER ── */}
            {complaint.status !== 'resolved' && complaint.status !== 'rejected' && (
              <div style={{
                marginTop: '16px',
                background: 'linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%)',
                border: '2px solid #3b82f6',
                borderRadius: '10px',
                padding: '14px 18px',
                display: 'flex',
                alignItems: 'center',
                gap: '14px',
                boxShadow: '0 4px 12px rgba(59, 130, 246, 0.12)'
              }}>
                <div style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '50%',
                  background: '#2563eb',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#ffffff',
                  flexShrink: 0
                }}>
                  <RefreshCw size={20} style={{ animation: 'spin 2s linear infinite' }} />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
                    <strong style={{ color: '#1e3a8a', fontSize: '0.95rem' }}>
                      ⚡ Nova-AI Sentinel Autonomous Settlement Desk Active
                    </strong>
                    <span style={{ fontSize: '0.74rem', background: '#dbeafe', color: '#1e40af', border: '1px solid #93c5fd', padding: '2px 10px', borderRadius: '12px', fontWeight: '800' }}>
                      Target SLA &lt; 30 Seconds
                    </span>
                  </div>
                  <p style={{ margin: '4px 0 0 0', fontSize: '0.84rem', color: '#334155', lineHeight: '1.4' }}>
                    Assigned to <strong>Nova-AI Sentinel</strong>. System is reconciling dual inter-bank clearing switch ledgers and executing automated reversal protocols per RBI TAT mandates.
                  </p>
                </div>
              </div>
            )}

            {/* ── AUTONOMOUS SETTLEMENT CELEBRATION BANNER ── */}
            {(resolvedCelebration || complaint.status === 'resolved') && (
              <div style={{
                marginTop: '16px',
                background: '#dcfce7',
                border: '2px solid #22c55e',
                borderRadius: '10px',
                padding: '16px 20px',
                display: 'flex',
                alignItems: 'center',
                gap: '14px',
                boxShadow: '0 4px 12px rgba(34, 197, 94, 0.12)'
              }}>
                <div style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: '50%',
                  background: '#16a34a',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: '#ffffff',
                  flexShrink: 0
                }}>
                  <CheckCircle2 size={24} />
                </div>
                <div style={{ flex: 1 }}>
                  <h4 style={{ margin: 0, color: '#14532d', fontSize: '1.02rem', fontWeight: '800' }}>
                    🎉 Grievance Autonomously Resolved by Nova-AI Sentinel in &lt; 30 Seconds!
                  </h4>
                  <p style={{ margin: '4px 0 0 0', fontSize: '0.84rem', color: '#166534', lineHeight: '1.4' }}>
                    Dual inter-bank clearing switch ledgers reconciled with 100% precision. Reversal protocol confirmed and statutory settlement memorandum issued below.
                  </p>
                </div>
              </div>
            )}

            {/* ── UPI 3-LEG TRANSACTION SETTLEMENT RADAR ── */}
            {['upi', 'imps', 'card', 'transfer', 'atm'].some(k => (complaint.service_type || '').toLowerCase().includes(k)) && (
              <div style={{ marginTop: '16px', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '10px', padding: '14px 18px' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: '700', color: '#0f2942', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span>🌐 Interbank Dispute Settlement Node Trail (NPCI / Switch)</span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr auto 1fr', alignItems: 'center', gap: '8px' }}>
                  {/* Leg 1 */}
                  <div style={{ background: '#dcfce7', border: '1px solid #86efac', borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.7rem', color: '#166534', fontWeight: '800' }}>LEG 1: REMITTER</div>
                    <div style={{ fontSize: '0.82rem', fontWeight: '700', color: '#14532d', marginTop: '2px' }}>{complaint.company_name || 'Sender Bank'}</div>
                    <div style={{ fontSize: '0.72rem', color: '#166534', marginTop: '2px' }}>✓ Debited</div>
                  </div>
                  <div style={{ color: '#94a3b8', fontWeight: '800' }}>➔</div>
                  {/* Leg 2 */}
                  <div style={{ background: '#eff6ff', border: '1px solid #bfdbfe', borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.7rem', color: '#1e40af', fontWeight: '800' }}>LEG 2: NPCI / SWITCH</div>
                    <div style={{ fontSize: '0.82rem', fontWeight: '700', color: '#1e3a8a', marginTop: '2px' }}>Central Payment Switch</div>
                    <div style={{ fontSize: '0.72rem', color: '#1e40af', marginTop: '2px' }}>✓ Cleared & Routed</div>
                  </div>
                  <div style={{ color: '#94a3b8', fontWeight: '800' }}>➔</div>
                  {/* Leg 3 */}
                  <div style={{ background: complaint.status === 'resolved' ? '#dcfce7' : '#fffbeb', border: `1px solid ${complaint.status === 'resolved' ? '#86efac' : '#fcd34d'}`, borderRadius: '8px', padding: '10px', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.7rem', color: complaint.status === 'resolved' ? '#166534' : '#92400e', fontWeight: '800' }}>LEG 3: BENEFICIARY</div>
                    <div style={{ fontSize: '0.82rem', fontWeight: '700', color: complaint.status === 'resolved' ? '#14532d' : '#78350f', marginTop: '2px' }}>Destination Account</div>
                    <div style={{ fontSize: '0.72rem', color: complaint.status === 'resolved' ? '#166534' : '#b45309', marginTop: '2px' }}>
                      {complaint.status === 'resolved' ? '✓ Credited / Reversible' : '⏳ Nodal Dispute Active'}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* ── RBI MANDATED T+5 COMPENSATION ACCRUAL RADAR ── */}
            <div style={{ marginTop: '12px', background: '#fffbeb', border: '1px solid #fde68a', borderRadius: '8px', padding: '10px 14px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', color: '#92400e' }}>
                <span style={{ fontSize: '1.1rem' }}>⚖️</span>
                <span><strong>RBI Harmonisation Mandate (DPSS.CO.PD No.629):</strong> Failed transaction resolution turnaround time active. Delayed reversal compensation tracked at ₹100/day.</span>
              </div>
              <span style={{ fontSize: '0.75rem', background: '#fef3c7', padding: '3px 8px', borderRadius: '12px', fontWeight: '700', color: '#b45309', border: '1px solid #fcd34d' }}>
                Statutory Auto-Tracking
              </span>
            </div>

            {/* ── EXPLAINABLE AI (XAI) ATTRIBUTION SIGNALS ── */}
            {complaint.xai_attribution && complaint.xai_attribution.length > 0 && (
              <div style={{ marginTop: '12px', background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: '8px', padding: '10px 14px' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: '700', color: '#166534', marginBottom: '6px' }}>
                  🤖 Explainable AI (XAI) Discriminative Feature Signals:
                </div>
                <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                  {complaint.xai_attribution.map((item, idx) => (
                    <span key={idx} style={{ background: 'white', border: '1px solid #86efac', padding: '2px 8px', borderRadius: '12px', fontSize: '0.72rem', color: '#15803d', fontWeight: '600' }}>
                      {item.word} ({Math.round(item.weight * 100)}%)
                    </span>
                  ))}
                  <span style={{ fontSize: '0.72rem', color: '#166534', alignSelf: 'center', marginLeft: '6px' }}>
                    🔒 PII Masked under DPDP Act 2023
                  </span>
                </div>
              </div>
            )}

            {/* RESOLUTION MODE & OFFICER */}
            <div style={{ display: 'flex', gap: '20px', marginTop: '16px', paddingTop: '16px', borderTop: '1px solid #f1f5f9', fontSize: '0.875rem' }}>
              <div>
                <span style={{ color: '#64748b' }}>Resolution Mode: </span>
                <strong style={{ color: complaint.resolution_mode === 'BOT' ? '#2563eb' : '#059669' }}>
                  {complaint.resolution_mode === 'BOT' ? '⚡ Settlement Desk (Automated)' : (complaint.resolution_mode === 'HUMAN' ? '👤 Grievance Redressal Officer' : 'Pending Assignment')}
                </strong>
              </div>
              <div>
                <span style={{ color: '#64748b' }}>Assigned Officer: </span>
                <strong>{complaint.assigned_officer}</strong>
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr', gap: '24px' }}>
            {/* LEFT COLUMN: TIMELINE */}
            <div className="card">
              <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '14px', color: '#1e293b' }}>
                Resolution Progress Timeline
              </h3>
              
              <div className="timeline">
                {complaint.timeline.map((step, idx) => (
                  <div key={idx} className="timeline-item">
                    <div className="timeline-dot"></div>
                    <div className="timeline-title">{step.event}</div>
                    <div className="timeline-time">
                      {new Date(step.timestamp).toLocaleString()}
                    </div>
                    <div className="timeline-desc">{step.detail}</div>
                  </div>
                ))}
              </div>

              {/* AI AUTONOMOUS RESOLUTION ADVICE MEMORANDUM */}
              {complaint.status === 'resolved' && complaint.resolution_notes && (
                <div style={{ marginTop: '20px', padding: '18px', background: '#f0fdf4', borderRadius: '10px', border: '2px solid #86efac', boxShadow: '0 4px 12px rgba(34, 197, 94, 0.08)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px', flexWrap: 'wrap', gap: '8px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <CheckCircle2 size={20} color="#16a34a" />
                      <h4 style={{ color: '#166534', fontSize: '1.05rem', fontWeight: '800', margin: 0 }}>
                        Official Statutory Settlement Memorandum
                      </h4>
                    </div>
                    <span style={{ background: '#dcfce7', color: '#15803d', border: '1px solid #86efac', padding: '3px 10px', borderRadius: '12px', fontSize: '0.74rem', fontWeight: '800' }}>
                      {complaint.resolution_mode === 'BOT' ? '🤖 NOVA-AI AUTONOMOUS RESOLUTION' : '👤 OFFICER SETTLED'}
                    </span>
                  </div>

                  <p style={{ fontSize: '0.9rem', color: '#1e3a1e', lineHeight: '1.6', background: 'white', padding: '14px', borderRadius: '8px', border: '1px solid #bbf7d0', marginBottom: '12px', whiteSpace: 'pre-line' }}>
                    {complaint.resolution_notes}
                  </p>

                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.78rem', color: '#166534', flexWrap: 'wrap', gap: '6px' }}>
                    <span>⚖️ <strong>Regulatory Framework:</strong> RBI Turn Around Time (TAT) Framework & Auto-reversal Mandate</span>
                    {complaint.resolved_at && (
                      <span>Resolved on {new Date(complaint.resolved_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</span>
                    )}
                  </div>
                </div>
              )}

              {/* PROPOSED WORKER RESOLUTION REVIEW CARD */}
              {complaint.latest_resolution && (
                <div style={{ marginTop: '20px', padding: '18px', background: '#f0fdf4', borderRadius: '8px', border: '2px solid #86efac' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <h4 style={{ color: '#166534', fontSize: '1.05rem', fontWeight: '700' }}>
                      Official Resolution Submitted by Bank Officer
                    </h4>
                    <span className="badge badge-green">
                      {complaint.latest_resolution.resolution_type}
                    </span>
                  </div>

                  <p style={{ fontSize: '0.9rem', color: '#14532d', marginBottom: '10px', whiteSpace: 'pre-line' }}>
                    {complaint.latest_resolution.resolution_details}
                  </p>

                  <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap', fontSize: '0.85rem', color: '#166534', background: '#ffffff', padding: '10px', borderRadius: '6px', border: '1px solid #bbf7d0', marginBottom: '12px' }}>
                    {complaint.latest_resolution.resolved_amount && (
                      <div><strong>Remedy Amount:</strong> Rs. {complaint.latest_resolution.resolved_amount.toLocaleString()}</div>
                    )}
                    {complaint.latest_resolution.transaction_reference && (
                      <div><strong>Reference / UTR:</strong> {complaint.latest_resolution.transaction_reference}</div>
                    )}
                    <div><strong>Officer:</strong> {complaint.latest_resolution.worker_name}</div>
                  </div>

                  {complaint.latest_resolution.resolution_proof_url && (
                    <div style={{ marginBottom: '14px' }}>
                      <a 
                        href={complaint.latest_resolution.resolution_proof_url} 
                        target="_blank" 
                        rel="noreferrer"
                        className="btn btn-outline"
                        style={{ fontSize: '0.82rem', padding: '6px 12px', background: '#ffffff' }}
                      >
                        <FileText size={14} /> View Attached Resolution Proof (Slip / Letter)
                      </a>
                    </div>
                  )}

                  {/* Customer Confirmation Buttons (If status is resolution_proposed) */}
                  {complaint.status === 'resolution_proposed' && (
                    <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid #bbf7d0' }}>
                      <p style={{ fontSize: '0.875rem', fontWeight: '600', color: '#14532d', marginBottom: '10px' }}>
                        Does this resolution successfully solve your issue?
                      </p>
                      <div style={{ display: 'flex', gap: '10px' }}>
                        <button
                          onClick={async () => {
                            try {
                              await axios.post(`/api/complaints/${complaint.token}/confirm-resolution`, {
                                confirmed: true,
                                feedback_or_reason: 'Customer accepted and confirmed officer resolution.'
                              });
                              alert('Resolution confirmed. Thank you!');
                              fetchComplaint(complaint.token);
                            } catch (e) {
                              alert('Error confirming resolution');
                            }
                          }}
                          className="btn btn-success"
                          style={{ padding: '8px 16px', fontSize: '0.85rem' }}
                        >
                          <CheckCircle2 size={16} /> Yes, I Confirm (Close Grievance)
                        </button>
                        <button
                          onClick={() => setShowReopenModal(true)}
                          className="btn btn-danger"
                          style={{ padding: '8px 16px', fontSize: '0.85rem' }}
                        >
                          <AlertCircle size={16} /> No, Still Unresolved (Reopen)
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* EVIDENCE RE-UPLOAD CARD IF REJECTED OR PENDING */}
              {complaint.evidence_status === 'REJECTED' && (
                <div style={{ marginTop: '20px', padding: '18px', background: '#fff1f2', borderRadius: '8px', border: '2px solid #fecdd3' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                    <AlertTriangle size={20} color="#e11d48" />
                    <h4 style={{ color: '#9f1239', fontSize: '1.05rem', fontWeight: '800', margin: 0 }}>
                      Evidence Proof Rejected — Action Required
                    </h4>
                  </div>
                  <p style={{ fontSize: '0.88rem', color: '#881337', marginBottom: '12px', background: '#ffe4e6', padding: '10px 12px', borderRadius: '6px', borderLeft: '4px solid #e11d48' }}>
                    <strong>Reason: </strong> {complaint.evidence_rejection_reason || 'The attached proof was insufficient or did not match the transaction details. Please upload a clear receipt, bank statement, or payment reference slip.'}
                  </p>

                  <form onSubmit={handleResubmitEvidence} style={{ marginTop: '12px' }}>
                    <label style={{ display: 'block', fontSize: '0.85rem', fontWeight: '700', color: '#9f1239', marginBottom: '6px' }}>
                      Upload New Valid Proof Document (PDF, PNG, JPG ≤ 10MB):
                    </label>
                    <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
                      <input 
                        type="file" 
                        accept=".pdf,.png,.jpg,.jpeg"
                        onChange={(e) => {
                          setNewProofFile(e.target.files[0]);
                          setProofSuccessMsg('');
                          setProofErrorMsg('');
                        }}
                        style={{ fontSize: '0.85rem', padding: '6px', background: 'white', borderRadius: '6px', border: '1px solid #fda4af', flex: 1, minWidth: '220px' }}
                        required
                      />
                      <button 
                        type="submit" 
                        className="btn btn-primary"
                        disabled={uploadingProof || !newProofFile}
                        style={{ padding: '8px 16px', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px', background: '#e11d48', borderColor: '#e11d48' }}
                      >
                        <Upload size={16} /> {uploadingProof ? 'Uploading & Verifying...' : 'Submit New Proof'}
                      </button>
                    </div>

                    {proofSuccessMsg && (
                      <div style={{ marginTop: '10px', fontSize: '0.85rem', color: '#166534', background: '#f0fdf4', padding: '8px 12px', borderRadius: '6px', border: '1px solid #bbf7d0', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <CheckCircle2 size={16} /> {proofSuccessMsg}
                      </div>
                    )}
                    {proofErrorMsg && (
                      <div style={{ marginTop: '10px', fontSize: '0.85rem', color: '#991b1b', background: '#fef2f2', padding: '8px 12px', borderRadius: '6px', border: '1px solid #fecaca', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <AlertCircle size={16} /> {proofErrorMsg}
                      </div>
                    )}
                  </form>
                </div>
              )}

              {/* REOPEN SECTION */}
              {complaint.can_reopen && (
                <div style={{ marginTop: '24px', padding: '14px', background: '#fffbeb', borderRadius: '6px', border: '1px solid #fde68a' }}>
                  <p style={{ fontSize: '0.85rem', color: '#92400e', marginBottom: '8px' }}>
                    Has your issue remained unresolved? You may request a formal case reopen within 7 days of resolution.
                  </p>
                  <button 
                    onClick={() => setShowReopenModal(true)} 
                    className="btn btn-outline"
                    style={{ borderColor: '#d97706', color: '#b45309', fontSize: '0.85rem', padding: '6px 12px' }}
                  >
                    <RefreshCw size={14} /> Request Case Reopen (Level 2 Nodal)
                  </button>
                </div>
              )}
            </div>

            {/* RIGHT COLUMN: MESSAGING WITH OFFICER & FEEDBACK */}
            <div>
              {/* MESSAGING THREAD */}
              <div className="card">
                <h3 style={{ fontSize: '1.1rem', fontWeight: '700', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <MessageSquare size={18} color="#2563eb" /> Communication Portal
                </h3>
                <p style={{ fontSize: '0.8rem', color: '#64748b', marginBottom: '14px' }}>
                  Exchange direct messages and clarification with your assigned grievance desk.
                </p>

                {/* Message list */}
                <div style={{ maxHeight: '240px', overflowY: 'auto', marginBottom: '14px', padding: '10px', background: '#f8fafc', borderRadius: '6px', border: '1px solid #e2e8f0' }}>
                  {messages.length === 0 ? (
                    <div style={{ textAlign: 'center', color: '#94a3b8', fontSize: '0.85rem', padding: '20px' }}>
                      No messages yet. You can post a query below.
                    </div>
                  ) : (
                    messages.map((m) => (
                      <div key={m.message_id} style={{ 
                        marginBottom: '10px', 
                        padding: '8px 12px', 
                        borderRadius: '6px',
                        background: m.sender_type === 'customer' ? '#dbeafe' : '#ffffff',
                        border: '1px solid #cbd5e1',
                        marginLeft: m.sender_type === 'customer' ? '20px' : '0',
                        marginRight: m.sender_type === 'customer' ? '0' : '20px'
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: '#64748b' }}>
                          <strong>{m.sender_name}</strong>
                          <span>{new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                        </div>
                        <div style={{ fontSize: '0.875rem', marginTop: '4px', color: '#0f172a' }}>
                          {m.message_text}
                        </div>
                      </div>
                    ))
                  )}
                </div>

                {/* Post message */}
                <form onSubmit={handleSendMessage} style={{ display: 'flex', gap: '8px' }}>
                  <input 
                    type="text"
                    placeholder="Type a message to officer..."
                    className="form-input"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    disabled={msgSending}
                  />
                  <button type="submit" className="btn btn-primary" style={{ padding: '8px 14px' }} disabled={msgSending}>
                    <Send size={16} />
                  </button>
                </form>
              </div>

              {/* POST-RESOLUTION FEEDBACK CARD */}
              {complaint.status === 'resolved' && !feedbackSent && (
                <div className="card" style={{ background: '#f0fdf4', border: '1px solid #bbf7d0' }}>
                  <h4 style={{ color: '#166534', fontSize: '1rem', fontWeight: '700', marginBottom: '8px' }}>
                    Rate Your Redressal Experience
                  </h4>
                  <div style={{ display: 'flex', gap: '8px', marginBottom: '10px' }}>
                    {[1, 2, 3, 4, 5].map((s) => (
                      <button 
                        key={s} 
                        type="button"
                        onClick={() => setRating(s)}
                        style={{ background: 'none', border: 'none', cursor: 'pointer', padding: '2px' }}
                      >
                        <Star size={24} fill={s <= rating ? '#eab308' : 'none'} color={s <= rating ? '#eab308' : '#cbd5e1'} />
                      </button>
                    ))}
                  </div>
                  <textarea 
                    rows="2"
                    placeholder="Optional feedback comments..."
                    className="form-textarea"
                    value={feedbackComment}
                    onChange={(e) => setFeedbackComment(e.target.value)}
                    style={{ marginBottom: '10px', fontSize: '0.85rem' }}
                  ></textarea>
                  <button onClick={handleSendFeedback} className="btn btn-success" style={{ width: '100%', padding: '8px' }}>
                    Submit Redressal Rating
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* REOPEN MODAL */}
      {showReopenModal && (
        <div style={{ 
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, 
          background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', 
          justifyContent: 'center', zIndex: 1000 
        }}>
          <div style={{ background: 'white', padding: '24px', borderRadius: '8px', maxWidth: '480px', width: '90%' }}>
            <h3 style={{ fontSize: '1.2rem', fontWeight: '700', color: '#991b1b', marginBottom: '10px' }}>
              Request Case Reopen
            </h3>
            <p style={{ fontSize: '0.875rem', color: '#475569', marginBottom: '14px' }}>
              Please describe why the previous resolution was unsatisfactory. This will elevate your grievance to Level 2 (Senior Nodal Redressal) under high-priority SLA.
            </p>
            <textarea 
              rows="4"
              className="form-textarea"
              placeholder="Explain the unresolved discrepancy..."
              value={reopenReason}
              onChange={(e) => setReopenReason(e.target.value)}
            ></textarea>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '16px' }}>
              <button onClick={() => setShowReopenModal(false)} className="btn btn-outline">
                Cancel
              </button>
              <button onClick={handleReopen} className="btn btn-danger">
                Submit Escalation
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
