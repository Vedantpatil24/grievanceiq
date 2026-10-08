import { useState, useEffect, useRef } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8000";

function fmtDate(d) {
  if (!d) return "—";
  return new Date(d).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });
}

function priorityClass(p) {
  if (p === "High")   return "badge badge-high";
  if (p === "Medium") return "badge badge-medium";
  return "badge badge-low";
}

function statusBadgeClass(s) {
  if (!s) return "badge badge-open";
  const v = s.toLowerCase();
  if (v === "open" || v === "submitted") return "badge badge-open";
  if (v === "in_progress") return "badge badge-inprogress";
  if (v === "resolved")    return "badge badge-resolved";
  if (v === "closed")      return "badge badge-closed";
  if (v === "rejected")    return "badge badge-rejected";
  return "badge badge-open";
}

function dueBadge(c) {
  if (!c.sla_due_at) return null;
  const hours = (new Date(c.sla_due_at) - Date.now()) / 3600000;
  if (hours < 0)  return <span className="badge badge-rejected">Overdue</span>;
  if (hours < 4)  return <span className="badge badge-high">Due &lt;4h</span>;
  if (hours < 24) return <span className="badge badge-medium">Due &lt;24h</span>;
  return null;
}

/* ─── Top Nav ────────────────────────────────────────── */
function TopNav({ employee, onLogout, notifCount, darkMode, onToggleTheme }) {
  return (
    <nav className="topnav">
      <div className="topnav-brand">
        <span className="brand-name">GrievanceIQ</span>
        <span className="brand-tag">Officer Workspace</span>
      </div>
      <div className="topnav-right">
        <span className="topnav-badge">🆔 {employee?.employee_id}</span>
        <span className="topnav-badge">🏢 {employee?.department}</span>
        <span style={{ color: "#e2e8f0", fontSize: "0.88rem", fontWeight: 500 }}>
          👤 {employee?.name}
        </span>
        {notifCount > 0 && (
          <div className="notif-btn" style={{ color: "#fbbf24" }}>
            🔔 <span style={{ fontWeight: 700 }}>{notifCount}</span>
          </div>
        )}
        <button className="theme-toggle" onClick={onToggleTheme} title="Toggle theme">
          {darkMode ? "☀️ Light" : "🌙 Dark"}
        </button>
        <button className="btn btn-outline btn-sm" style={{ borderColor: "rgba(255,255,255,.2)", color: "#cbd5e1", background: "rgba(255,255,255,.06)" }}
          onClick={onLogout}>
          🚪 Logout
        </button>
      </div>
    </nav>
  );
}

/* ─── Action Panel ───────────────────────────────────── */
function ActionPanel({ complaint: c, token, onDone }) {
  const [action, setAction] = useState(""); // "investigate"|"request_proof"|"reject"|"resolve"
  const [notes, setNotes] = useState("");
  const [reason, setReason] = useState("");
  const [proofReason, setProofReason] = useState("");
  const [proofFile, setProofFile] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [err, setErr] = useState("");

  const submit = async () => {
    if (!action) { setErr("Select an action first."); return; }
    if (action === "request_proof" && !proofReason.trim()) {
      setErr("Please specify what additional proof is needed.");
      return;
    }
    if (action === "reject" && !reason.trim()) {
      setErr("Please provide a rejection reason.");
      return;
    }
    if (action === "resolve" && !notes.trim()) {
      setErr("Please provide resolution notes.");
      return;
    }
    setErr(""); setSubmitting(true);

    try {
      const fd = new FormData();
      fd.append("action", action);
      if (notes)       fd.append("resolution_notes", notes);
      if (reason)      fd.append("rejection_reason", reason);
      if (proofReason) fd.append("request_proof_reason", proofReason);
      if (proofFile)   fd.append("proof_doc", proofFile);

      await axios.post(`${API}/employee/complaint/${c.token}/action`, fd, {
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "multipart/form-data" }
      });
      onDone();
    } catch (e) {
      setErr(e?.response?.data?.detail || "Failed to submit action.");
    }
    setSubmitting(false);
  };

  return (
    <div style={{ marginTop: "1.25rem" }}>
      <div className="section-title">Take Action</div>

      {/* Action selector */}
      <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "1rem" }}>
        {[
          { id: "investigate",    label: "🔍 Investigate",          cls: "btn-outline" },
          { id: "request_proof",  label: "📎 Request More Proof",   cls: "btn-outline" },
          { id: "reject",         label: "❌ Reject",               cls: "btn-rose" },
          { id: "resolve",        label: "✅ Resolve",              cls: "btn-emerald" },
        ].map(a => (
          <button key={a.id}
            className={`btn btn-sm ${action === a.id ? a.cls : "btn-outline"}`}
            onClick={() => { setAction(a.id); setErr(""); }}>
            {a.label}
          </button>
        ))}
      </div>

      {/* Context fields */}
      {action === "request_proof" && (
        <div className="form-group">
          <label className="form-label">What additional proof is needed? <span className="required">*</span></label>
          <textarea className="form-textarea" rows={2} value={proofReason}
            onChange={e => setProofReason(e.target.value)}
            placeholder="e.g. Please upload your bank statement for the past 3 months." />
        </div>
      )}

      {action === "reject" && (
        <div className="form-group">
          <label className="form-label">Rejection Reason <span className="required">*</span></label>
          <textarea className="form-textarea" rows={3} value={reason}
            onChange={e => setReason(e.target.value)}
            placeholder="Provide a clear, valid reason for rejection." />
        </div>
      )}

      {action === "resolve" && (
        <>
          <div className="form-group">
            <label className="form-label">Resolution Notes <span className="required">*</span></label>
            <textarea className="form-textarea" rows={3} value={notes}
              onChange={e => setNotes(e.target.value)}
              placeholder="Describe what was investigated and how it was resolved." />
          </div>
          <div className="form-group">
            <label className="form-label">Resolution Proof Document</label>
            <input type="file" className="form-input" onChange={e => setProofFile(e.target.files[0])} />
            <span className="form-hint">Upload a letter, screenshot, or document as proof of resolution.</span>
          </div>
        </>
      )}

      {err && <div className="alert alert-error mb-2">{err}</div>}

      {action && (
        <button className="btn btn-primary" onClick={submit} disabled={submitting}>
          {submitting ? "Submitting…" : "Submit Action"}
        </button>
      )}
    </div>
  );
}

/* ─── Complaint Detail Modal ─────────────────────────── */
function ComplaintDetailModal({ complaint: c, token, onClose, onActionDone }) {
  const [actionDone, setActionDone] = useState(false);

  const handleDone = () => { setActionDone(true); onActionDone(); };

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal-box modal-wide fade-in">
        <div className="modal-header">
          <div>
            <h3>Complaint #{c.token}</h3>
            <div style={{ display: "flex", gap: "0.4rem", marginTop: "0.35rem" }}>
              <span className={priorityClass(c.priority)}>{c.priority}</span>
              <span className={statusBadgeClass(c.status)}>{c.status?.replace("_", " ")}</span>
              {c.is_escalated && <span className="badge badge-escalated">⚠ Escalated</span>}
            </div>
          </div>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          {/* Priority reason */}
          {c.priority_reason && (
            <div className="alert alert-info mb-2">
              <div><strong>📊 Why {c.priority} Priority:</strong> {c.priority_reason}</div>
            </div>
          )}

          {c.requires_more_proof && (
            <div className="alert alert-warn mb-2">
              <strong>📎 Pending More Proof:</strong> {c.requires_more_proof}
            </div>
          )}

          <div className="section-title">Complainant & Case Info</div>
          <div className="detail-grid mb-2">
            <div className="detail-field"><span className="df-label">Company</span><span className="df-value">{c.company}</span></div>
            <div className="detail-field"><span className="df-label">Department</span><span className="df-value">{c.department}</span></div>
            <div className="detail-field"><span className="df-label">Service</span><span className="df-value">{c.service_type || "—"}</span></div>
            <div className="detail-field"><span className="df-label">Amount</span><span className="df-value">{c.amount ? `₹${c.amount}` : "—"}</span></div>
            <div className="detail-field"><span className="df-label">Reference ID</span><span className="df-value" style={{ fontFamily: "monospace" }}>{c.reference_id || "—"}</span></div>
            <div className="detail-field"><span className="df-label">Branch</span><span className="df-value">{c.branch || "—"}</span></div>
            <div className="detail-field"><span className="df-label">Txn Date</span><span className="df-value">{c.transaction_date || "—"}</span></div>
            <div className="detail-field"><span className="df-label">Submitted</span><span className="df-value">{fmtDate(c.created_at)}</span></div>
            <div className="detail-field"><span className="df-label">SLA Deadline</span><span className="df-value">{fmtDate(c.sla_due_at)}</span></div>
          </div>

          <div className="section-title">Description</div>
          <div style={{ background: "var(--slate-50)", borderRadius: "var(--radius-sm)", padding: "0.9rem 1rem", fontSize: "0.88rem", lineHeight: 1.7, marginBottom: "1rem", border: "1px solid var(--slate-200)" }}>
            {c.description || "No description provided."}
          </div>

          {c.proof_url && (
            <div className="mb-2">
              <div className="section-title">Submitted Proof</div>
              <a href={`${API}${c.proof_url}`} target="_blank" rel="noreferrer" className="btn btn-outline btn-sm">
                📎 View Proof Document
              </a>
            </div>
          )}

          {c.customer_appeal && (
            <div style={{ marginBottom: "1rem" }}>
              <div className="section-title">Customer Appeal</div>
              <div className="alert alert-warn">{c.customer_appeal}</div>
            </div>
          )}

          {/* Action panel or done message */}
          {actionDone ? (
            <div className="alert alert-success mt-2">✅ Action submitted successfully. This complaint has been updated.</div>
          ) : (
            <ActionPanel complaint={c} token={token} onDone={handleDone} />
          )}
        </div>
      </div>
    </div>
  );
}

/* ─── Notifications Panel ────────────────────────────── */
function NotificationsPanel({ token, onClose }) {
  const [notifs, setNotifs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API}/employee/notifications`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => setNotifs(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal-box fade-in" style={{ maxWidth: 480 }}>
        <div className="modal-header">
          <h3>🔔 Notifications from Admin</h3>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body" style={{ padding: 0 }}>
          {loading && <div className="loading-center"><div className="spinner"></div></div>}
          {!loading && notifs.length === 0 && (
            <div className="empty-state"><div className="es-icon">🔔</div><div className="es-title">No notifications</div></div>
          )}
          {notifs.map((n, i) => (
            <div key={i} style={{ padding: "0.9rem 1.25rem", borderBottom: "1px solid var(--slate-100)" }}>
              <div style={{ fontSize: "0.86rem", color: "var(--primary)", fontWeight: 500 }}>{n.message}</div>
              <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.25rem" }}>{fmtDate(n.created_at)}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

/* ─── Main EmployeeDashboard ─────────────────────────── */
export default function EmployeeDashboard({ token, employee, onLogout, darkMode, onToggleTheme }) {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filterPriority, setFilterPriority] = useState("");
  const [filterStatus, setFilterStatus] = useState("");
  const [selected, setSelected] = useState(null);
  const [notifCount, setNotifCount] = useState(0);
  const [showNotifs, setShowNotifs] = useState(false);

  const fetchComplaints = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filterPriority) params.priority = filterPriority;
      if (filterStatus)   params.status   = filterStatus;
      const r = await axios.get(`${API}/employee/complaints`, {
        params,
        headers: { Authorization: `Bearer ${token}` }
      });
      setComplaints(r.data);
    } catch { /* noop */ }
    setLoading(false);
  };

  const fetchNotifs = async () => {
    try {
      const r = await axios.get(`${API}/employee/notifications`, { headers: { Authorization: `Bearer ${token}` } });
      setNotifCount(r.data.length);
    } catch { /* noop */ }
  };

  useEffect(() => { fetchComplaints(); fetchNotifs(); }, [token]);
  useEffect(() => { fetchComplaints(); }, [filterPriority, filterStatus]);

  const handleActionDone = () => { setSelected(null); fetchComplaints(); };

  // Sort by SLA urgency
  const sorted = [...complaints].sort((a, b) => {
    const pa = { High: 3, Medium: 2, Low: 1 }[a.priority] || 0;
    const pb = { High: 3, Medium: 2, Low: 1 }[b.priority] || 0;
    return pb - pa;
  });

  const stats = {
    total: complaints.length,
    open: complaints.filter(c => c.status === "open").length,
    inProgress: complaints.filter(c => c.status === "in_progress").length,
    escalated: complaints.filter(c => c.is_escalated).length,
  };

  return (
    <>
      <TopNav employee={employee} onLogout={onLogout} notifCount={notifCount} darkMode={darkMode} onToggleTheme={onToggleTheme} />

      <div className="page" style={{ paddingTop: "1.75rem" }}>
        <div className="flex-between mb-3">
          <div>
            <h1 style={{ fontWeight: 800, fontSize: "1.4rem" }}>My Assigned Complaints</h1>
            <p className="text-muted">Welcome, {employee?.name} — {employee?.department} Department</p>
          </div>
          <div style={{ display: "flex", gap: "0.6rem" }}>
            <button className="btn btn-outline btn-sm" onClick={() => { setShowNotifs(true); }}>
              🔔 Notifications {notifCount > 0 && `(${notifCount})`}
            </button>
            <button className="btn btn-outline btn-sm" onClick={fetchComplaints}>🔄 Refresh</button>
          </div>
        </div>

        {/* Stats row */}
        <div className="grid-4 mb-3">
          {[
            { label: "Total Assigned", val: stats.total, icon: "📋", bg: "#eff6ff" },
            { label: "Open",           val: stats.open, icon: "📂", bg: "#fef3c7" },
            { label: "In Progress",    val: stats.inProgress, icon: "⚙️", bg: "#ecfdf5" },
            { label: "Escalated",      val: stats.escalated, icon: "⚠️", bg: "#fdf4ff" },
          ].map(s => (
            <div key={s.label} className="stat-card">
              <div className="stat-icon" style={{ background: s.bg }}>{s.icon}</div>
              <div className="stat-info">
                <div className="si-label">{s.label}</div>
                <div className="si-value">{s.val}</div>
              </div>
            </div>
          ))}
        </div>

        {/* Filters */}
        <div className="filter-bar mb-2" style={{ borderRadius: "var(--radius)", border: "1px solid var(--slate-200)", marginBottom: "1rem" }}>
          <select className="form-select" value={filterPriority} onChange={e => setFilterPriority(e.target.value)}>
            <option value="">All Priorities</option>
            <option>High</option>
            <option>Medium</option>
            <option>Low</option>
          </select>
          <select className="form-select" value={filterStatus} onChange={e => setFilterStatus(e.target.value)}>
            <option value="">All Statuses</option>
            <option value="open">Open</option>
            <option value="in_progress">In Progress</option>
            <option value="resolved">Resolved</option>
          </select>
          <button className="btn btn-ghost btn-sm" onClick={() => { setFilterPriority(""); setFilterStatus(""); }}>Clear</button>
        </div>

        {/* Complaint list */}
        {loading && <div className="loading-center"><div className="spinner"></div><span>Loading…</span></div>}

        {!loading && sorted.length === 0 && (
          <div className="empty-state">
            <div className="es-icon">✅</div>
            <div className="es-title">No complaints in queue</div>
            <div className="es-text">All caught up! Check back later.</div>
          </div>
        )}

        <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
          {sorted.map(c => (
            <div key={c.token} className="complaint-card" onClick={() => setSelected(c)}>
              <div className="cc-left">
                <div className="cc-token">#{c.token}</div>
                <div className="cc-title">{c.description?.slice(0, 80) || "No description"}…</div>
                <div className="cc-meta">{c.company} · {c.department} · Submitted: {fmtDate(c.created_at)}</div>
              </div>
              <div className="cc-right">
                <span className={priorityClass(c.priority)}>{c.priority}</span>
                <span className={statusBadgeClass(c.status)}>{c.status?.replace("_", " ")}</span>
                {dueBadge(c)}
                {c.is_escalated && <span className="badge badge-escalated">⚠ Late</span>}
                <span style={{ color: "var(--text-muted)", fontSize: "1.1rem" }}>›</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {selected && (
        <ComplaintDetailModal
          complaint={selected}
          token={token}
          onClose={() => setSelected(null)}
          onActionDone={handleActionDone}
        />
      )}

      {showNotifs && <NotificationsPanel token={token} onClose={() => setShowNotifs(false)} />}
    </>
  );
}
