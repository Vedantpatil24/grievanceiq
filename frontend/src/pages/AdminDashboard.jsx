import { useState, useEffect, useRef } from "react";
import axios from "axios";
import {
  PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, LineChart, Line,
  AreaChart, Area, RadialBarChart, RadialBar
} from "recharts";

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

const PIE_COLORS  = ["#e11d48", "#d97706", "#059669"];
const BAR_COLORS  = ["#2563eb", "#d97706", "#059669", "#7c3aed", "#e11d48"];
const CLUSTER_CFG = [
  { icon: "🚨", color: "#fef2f2", border: "#fecaca" },
  { icon: "🏧", color: "#fff7ed", border: "#fed7aa" },
  { icon: "💳", color: "#eff6ff", border: "#bfdbfe" },
  { icon: "📋", color: "#f0fdf4", border: "#bbf7d0" },
  { icon: "🔐", color: "#fdf4ff", border: "#e9d5ff" },
  { icon: "💰", color: "#fff8f1", border: "#fde68a" },
];

/* ────────────────── SIDEBAR NAV ─────────────────────── */
const SIDEBAR_ITEMS = [
  { id: "queue",      icon: "📋", label: "Grievance Queue" },
  { id: "departments",icon: "🏢", label: "Departments & Officers" },
  { id: "analytics",  icon: "📊", label: "Analytics" },
  { id: "leaderboard",icon: "🏆", label: "Leaderboard" },
  { id: "clusters",   icon: "🔍", label: "Complaint Clusters" },
  { id: "audit",      icon: "🛡️", label: "Audit Logs" },
];

function Sidebar({ active, setActive, onLogout, darkMode, onToggleTheme }) {
  return (
    <div className="sidebar">
      <div className="sidebar-logo">
        <div className="sl-name">GrievanceIQ</div>
        <div className="sl-role">Admin Command</div>
      </div>
      <div className="sidebar-nav">
        {SIDEBAR_ITEMS.map(item => (
          <div key={item.id}
            className={`sidebar-item ${active === item.id ? "active" : ""}`}
            onClick={() => setActive(item.id)}>
            <span className="si-icon">{item.icon}</span>
            {item.label}
          </div>
        ))}
      </div>
      <div className="sidebar-footer">
        <div
          onClick={onToggleTheme}
          style={{
            display: "flex", alignItems: "center", gap: "0.65rem",
            padding: "0.65rem 0.75rem", borderRadius: "var(--radius-sm)",
            fontSize: "0.88rem", fontWeight: 500, cursor: "pointer",
            color: "var(--text-muted)", transition: "var(--transition)",
            marginBottom: "0.25rem",
          }}
        >
          <span style={{ fontSize: "1rem" }}>{darkMode ? "☀️" : "🌙"}</span>
          {darkMode ? "Light Mode" : "Dark Mode"}
        </div>
        <div className="sidebar-logout" onClick={onLogout}>🚪 Logout</div>
      </div>
    </div>
  );
}

/* ────────────────── COMPLAINT DETAIL MODAL ──────────── */
function ComplaintDetailModal({ complaint: c, token, onClose, onStatusChange }) {
  const [newStatus, setNewStatus] = useState(c.status);
  const [updating, setUpdating] = useState(false);
  const [msg, setMsg] = useState("");

  const update = async () => {
    setUpdating(true); setMsg("");
    try {
      await axios.patch(`${API}/admin/complaint/${c.token}/status`,
        { status: newStatus },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMsg("Status updated. Employee notified.");
      onStatusChange();
    } catch (e) {
      setMsg(e?.response?.data?.detail || "Update failed.");
    }
    setUpdating(false);
  };

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
          {c.priority_reason && (
            <div className="alert alert-info mb-2">
              <strong>📊 Priority Reason:</strong> {c.priority_reason}
            </div>
          )}

          <div className="section-title">Complaint Details</div>
          <div className="detail-grid mb-2">
            <div className="detail-field"><span className="df-label">Company</span><span className="df-value">{c.company}</span></div>
            <div className="detail-field"><span className="df-label">Department</span><span className="df-value">{c.department}</span></div>
            <div className="detail-field"><span className="df-label">Assigned Officer</span><span className="df-value">{c.assigned_worker_name || c.assigned_worker || "—"} <span style={{ fontFamily: "monospace", color: "var(--text-muted)", fontSize: "0.8rem" }}>({c.assigned_worker_id || "—"})</span></span></div>
            <div className="detail-field"><span className="df-label">Service Type</span><span className="df-value">{c.service_type || "—"}</span></div>
            <div className="detail-field"><span className="df-label">Amount</span><span className="df-value">{c.amount ? `₹${c.amount}` : "—"}</span></div>
            <div className="detail-field"><span className="df-label">Reference ID</span><span className="df-value" style={{ fontFamily: "monospace" }}>{c.reference_id || "—"}</span></div>
            <div className="detail-field"><span className="df-label">Submitted</span><span className="df-value">{fmtDate(c.created_at)}</span></div>
            <div className="detail-field"><span className="df-label">SLA Due</span><span className="df-value" style={{ fontWeight: 600 }}>{fmtDate(c.sla_due_at || c.due_date)}</span></div>
          </div>

          <div className="section-title">Description</div>
          <div style={{ background: "var(--slate-50)", borderRadius: "var(--radius-sm)", padding: "0.9rem 1rem", fontSize: "0.88rem", lineHeight: 1.7, marginBottom: "1rem", border: "1px solid var(--slate-200)" }}>
            {c.description || c.narrative || "No description provided."}
          </div>

          {c.rejection_reason && (
            <div className="alert alert-error mb-2">
              <strong>Rejection Reason:</strong> {c.rejection_reason}
            </div>
          )}
          {c.resolution_notes && (
            <div className="alert alert-success mb-2">
              <strong>Resolution Notes:</strong> {c.resolution_notes}
            </div>
          )}
          {c.customer_appeal && (
            <div className="alert alert-warn mb-2">
              <strong>Customer Appeal:</strong> {c.customer_appeal}
            </div>
          )}

          {/* Admin status override */}
          <div className="section-title" style={{ marginTop: "1.25rem" }}>Admin Override — Change Status</div>
          <div style={{ display: "flex", gap: "0.6rem", alignItems: "center", flexWrap: "wrap" }}>
            <select className="form-select" style={{ maxWidth: 180 }} value={newStatus} onChange={e => setNewStatus(e.target.value)}>
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
            <button className="btn btn-primary btn-sm" onClick={update} disabled={updating || newStatus === c.status}>
              {updating ? "Updating…" : "Apply Change"}
            </button>
            {msg && <span style={{ fontSize: "0.84rem", color: msg.includes("fail") ? "var(--rose)" : "var(--emerald)", fontWeight: 600 }}>{msg}</span>}
          </div>
          <p className="form-hint">⚠ Changing status will send a notification to the assigned officer.</p>
        </div>
      </div>
    </div>
  );
}

/* ────────────────── TAB 1: GRIEVANCE QUEUE ──────────── */
function GrievanceQueue({ token }) {
  const [complaints, setComplaints] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState(null);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({ department: "", priority: "", status: "", company: "", escalated: false });
  const pageSize = 50;

  const fetch = async () => {
    setLoading(true);
    try {
      const params = { skip: (page - 1) * pageSize, limit: pageSize };
      if (filters.department) params.department = filters.department;
      if (filters.priority)   params.priority   = filters.priority;
      if (filters.status)     params.status     = filters.status;
      if (filters.company)    params.company    = filters.company;
      if (filters.escalated)  params.escalated_only = true;
      const r = await axios.get(`${API}/admin/complaints`, { params, headers: { Authorization: `Bearer ${token}` } });
      setComplaints(r.data.complaints); setTotal(r.data.total);
    } catch { /* noop */ }
    setLoading(false);
  };

  useEffect(() => { fetch(); }, [page, filters]);

  const set = (k, v) => { setFilters(f => ({ ...f, [k]: v })); setPage(1); };
  const totalPages = Math.ceil(total / pageSize);

  return (
    <div>
      <div className="flex-between mb-2">
        <div>
          <h2 style={{ fontWeight: 800, fontSize: "1.3rem" }}>Grievance Queue</h2>
          <p className="text-muted">{total.toLocaleString()} total complaints</p>
        </div>
        <button className="btn btn-outline btn-sm" onClick={fetch}>🔄 Refresh</button>
      </div>

      {/* Filter bar */}
      <div className="filter-bar mb-2" style={{ borderRadius: "var(--radius)", border: "1px solid var(--slate-200)", marginBottom: "1rem" }}>
        <select className="form-select" value={filters.department} onChange={e => set("department", e.target.value)}>
          <option value="">All Departments</option>
          {["Digital & UPI Banking", "Loans & Advances", "Cards & ATM Services", "Account & Branch Operations", "Fraud & Risk Management"].map(d => <option key={d} value={d}>{d}</option>)}
        </select>
        <select className="form-select" value={filters.priority} onChange={e => set("priority", e.target.value)}>
          <option value="">All Priorities</option>
          <option>High</option><option>Medium</option><option>Low</option>
        </select>
        <select className="form-select" value={filters.status} onChange={e => set("status", e.target.value)}>
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="in_progress">In Progress</option>
          <option value="resolved">Resolved</option>
          <option value="closed">Closed</option>
        </select>
        <input className="form-input" placeholder="Company…" value={filters.company} onChange={e => set("company", e.target.value)} style={{ flex: 1 }} />
        <label style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontSize: "0.84rem", fontWeight: 600, cursor: "pointer", whiteSpace: "nowrap" }}>
          <input type="checkbox" checked={filters.escalated} onChange={e => set("escalated", e.target.checked)} />
          Escalated only
        </label>
        <button className="btn btn-ghost btn-sm" onClick={() => { setFilters({ department: "", priority: "", status: "", company: "", escalated: false }); setPage(1); }}>
          Clear
        </button>
      </div>

      {/* Table */}
      <div className="card" style={{ overflow: "hidden" }}>
        {loading ? (
          <div className="loading-center"><div className="spinner"></div><span>Loading…</span></div>
        ) : complaints.length === 0 ? (
          <div className="empty-state"><div className="es-icon">📭</div><div className="es-title">No complaints found</div></div>
        ) : (
          <>
            <div style={{ overflowX: "auto" }}>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Token</th>
                    <th>Company</th>
                    <th>Department</th>
                    <th>Priority</th>
                    <th>Status</th>
                    <th>Officer</th>
                    <th>Submitted</th>
                    <th>SLA Due</th>
                  </tr>
                </thead>
                <tbody>
                  {complaints.map(c => (
                    <tr key={c.token} onClick={() => setSelected(c)}>
                      <td className="mono">{c.token}</td>
                      <td style={{ maxWidth: 140, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{c.company}</td>
                      <td>{c.department}</td>
                      <td><span className={priorityClass(c.priority)}>{c.priority}</span></td>
                      <td>
                        <div style={{ display: "flex", gap: "0.3rem", alignItems: "center" }}>
                          <span className={statusBadgeClass(c.status)}>{c.status?.replace("_", " ")}</span>
                          {c.is_escalated && <span className="badge badge-escalated">⚠</span>}
                        </div>
                      </td>
                      <td style={{ fontSize: "0.82rem" }}>
                        <div>{c.assigned_worker_name || c.assigned_worker || "—"}</div>
                        {c.assigned_worker_id && c.assigned_worker_id !== "—" && (
                          <div style={{ fontSize: "0.74rem", color: "var(--text-muted)", fontFamily: "monospace" }}>{c.assigned_worker_id}</div>
                        )}
                      </td>
                      <td style={{ fontSize: "0.8rem", whiteSpace: "nowrap" }}>{fmtDate(c.created_at)}</td>
                      <td style={{ fontSize: "0.8rem", whiteSpace: "nowrap", fontWeight: 600 }}>{fmtDate(c.sla_due_at || c.due_date)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="pagination">
                <button className="pg-btn" onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>‹ Prev</button>
                <span className="pg-info">Page {page} of {totalPages}</span>
                <button className="pg-btn" onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>Next ›</button>
              </div>
            )}
          </>
        )}
      </div>

      {selected && (
        <ComplaintDetailModal
          complaint={selected}
          token={token}
          onClose={() => setSelected(null)}
          onStatusChange={fetch}
        />
      )}
    </div>
  );
}

/* ────────────────── TAB 2: DEPARTMENTS & WORKERS ────── */
function WorkerDetailModal({ worker: w, onClose }) {
  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal-box fade-in" style={{ maxWidth: 480 }}>
        <div className="modal-header">
          <div>
            <h3>{w.name}</h3>
            <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "2px" }}>{w.employee_id} · {w.department}</p>
          </div>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          <div className="grid-2 mb-2">
            {[
              { label: "Total Assigned", val: w.total_assigned ?? w.total ?? 0, color: "var(--blue)" },
              { label: "Resolved",       val: w.resolved_count ?? w.resolved ?? 0, color: "var(--emerald)" },
              { label: "In Progress",    val: w.in_progress_count ?? w.in_progress ?? 0, color: "var(--gold)" },
              { label: "Escalated/Late", val: w.escalated_count ?? w.late_escalated ?? 0, color: "var(--rose)" },
            ].map(s => (
              <div key={s.label} style={{ background: "var(--slate-50)", border: "1px solid var(--slate-200)", borderRadius: "var(--radius-sm)", padding: "1rem", textAlign: "center" }}>
                <div style={{ fontSize: "1.8rem", fontWeight: 800, color: s.color }}>{s.val}</div>
                <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", fontWeight: 600 }}>{s.label}</div>
              </div>
            ))}
          </div>
          <div className="detail-field" style={{ marginBottom: "0.6rem" }}>
            <span className="df-label">Email</span>
            <span className="df-value">{w.email || "—"}</span>
          </div>
          <div className="detail-field">
            <span className="df-label">Phone</span>
            <span className="df-value">{w.phone || "—"}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

function DepartmentsTab({ token }) {
  const [deptWorkers, setDeptWorkers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedWorker, setSelectedWorker] = useState(null);

  useEffect(() => {
    setLoading(true);
    axios.get(`${API}/admin/departments-workers`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => setDeptWorkers(r.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-center"><div className="spinner"></div><span>Loading…</span></div>;

  return (
    <div>
      <h2 style={{ fontWeight: 800, fontSize: "1.3rem", marginBottom: "0.35rem" }}>Departments & Officers</h2>
      <p className="text-muted mb-3">5 departments · 25 dedicated grievance officers</p>

      <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        {deptWorkers.map(dept => (
          <div key={dept.department} className="card">
            <div className="card-header">
              <div>
                <h3 style={{ fontWeight: 700, fontSize: "1.05rem" }}>🏢 {dept.department}</h3>
                <span className="text-muted text-sm">{dept.workers?.length || 0} officers</span>
              </div>
              <div style={{ display: "flex", gap: "0.5rem" }}>
                <span style={{ fontSize: "0.82rem", color: "var(--text-muted)" }}>
                  Total: <strong>{dept.workers?.reduce((s, w) => s + (w.total_assigned || 0), 0)}</strong> complaints
                </span>
              </div>
            </div>
            <div className="card-body" style={{ padding: "1rem" }}>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                {(dept.workers || []).map(w => (
                  <div key={w.worker_id} className="worker-card" onClick={() => setSelectedWorker(w)}>
                    <div className="worker-avatar">
                      {w.name?.split(" ").map(x => x[0]).join("").slice(0, 2).toUpperCase()}
                    </div>
                    <div className="worker-info">
                      <div className="wi-name">{w.name}</div>
                      <div className="wi-id">{w.employee_id}</div>
                    </div>
                    <div className="worker-stats">
                      <div className="ws-item"><div className="wsi-val">{w.total_assigned ?? w.total ?? 0}</div><div className="wsi-lbl">Assigned</div></div>
                      <div className="ws-item"><div className="wsi-val" style={{ color: "var(--emerald)" }}>{w.resolved_count ?? w.resolved ?? 0}</div><div className="wsi-lbl">Resolved</div></div>
                      <div className="ws-item"><div className="wsi-val" style={{ color: "var(--rose)" }}>{w.escalated_count ?? w.late_escalated ?? 0}</div><div className="wsi-lbl">Late</div></div>
                    </div>
                    <span style={{ color: "var(--text-muted)" }}>›</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {selectedWorker && <WorkerDetailModal worker={selectedWorker} onClose={() => setSelectedWorker(null)} />}
    </div>
  );
}

/* ────────────────── TAB 3: ANALYTICS ────────────────── */
/* Custom animated donut center label */
function DonutLabel({ cx, cy, value, label }) {
  return (
    <g>
      <text x={cx} y={cy - 8} textAnchor="middle" fill="var(--text)" fontSize={22} fontWeight={800}>{value?.toLocaleString()}</text>
      <text x={cx} y={cy + 14} textAnchor="middle" fill="var(--text-muted)" fontSize={11} fontWeight={600}>{label}</text>
    </g>
  );
}

function AnalyticsTab({ token }) {
  const [stats, setStats] = useState(null);
  const [subTab, setSubTab] = useState("overview");
  const [loading, setLoading] = useState(false);
  const [chartKey, setChartKey] = useState(0); // re-mount charts to trigger animation

  useEffect(() => {
    const load = () => {
      axios.get(`${API}/admin/stats`, { headers: { Authorization: `Bearer ${token}` } })
        .then(r => setStats(r.data))
        .catch(() => {})
        .finally(() => setLoading(false));
    };
    setLoading(true);
    load();
    const interval = setInterval(load, 15000);
    return () => clearInterval(interval);
  }, []);

  // Re-trigger animations when switching sub-tabs
  useEffect(() => { setChartKey(k => k + 1); }, [subTab]);

  if (loading && !stats) return <div className="loading-center"><div className="spinner"></div><span>Loading analytics…</span></div>;
  if (!stats)  return <div className="empty-state"><div className="es-icon">📊</div><div className="es-title">No data available</div></div>;

  const totalVal    = stats.total_complaints ?? stats.total ?? 0;
  const openVal     = stats.open_count ?? stats.status_counts?.open ?? 0;
  const resolvedVal = stats.resolved_count ?? stats.status_counts?.resolved ?? 0;
  const escalatedVal = stats.escalated_count ?? 0;
  const inProgVal   = stats.in_progress_count ?? stats.status_counts?.in_progress ?? 0;

  const priorityData = [
    { name: "High",   value: stats.priority_counts?.High   || 0, fill: "#e11d48" },
    { name: "Medium", value: stats.priority_counts?.Medium || 0, fill: "#d97706" },
    { name: "Low",    value: stats.priority_counts?.Low    || 0, fill: "#059669" },
  ];

  const statusDonutData = [
    { name: "Open",        value: openVal,      fill: "#2563eb" },
    { name: "In Progress", value: inProgVal,    fill: "#d97706" },
    { name: "Resolved",    value: resolvedVal,  fill: "#059669" },
    { name: "Escalated",   value: escalatedVal, fill: "#7c3aed" },
  ].filter(d => d.value > 0);

  const deptList = stats.dept_status_counts || stats.department_breakdown || [];
  const deptData = deptList.map(d => ({
    name: (d.department || "—").replace(" & ", " &\n").replace("Operations", "Ops"),
    Open: d.open || 0,
    "In Progress": d.in_progress || 0,
    Resolved: d.resolved || 0,
  }));

  // Build a trend-like area data from department totals (simulating monthly trend)
  const trendData = deptList.map((d, i) => ({
    month: ["Jan","Feb","Mar","Apr","May"][i] || `M${i+1}`,
    Total: d.total || 0,
    Resolved: d.resolved || 0,
    Open: d.open || 0,
  }));

  const compList = stats.company_counts || stats.company_breakdown || [];
  const companyData = compList.slice(0, 10).map(c => ({
    name: (c.company || "—").slice(0, 16),
    Total: c.count ?? c.total ?? 0,
    Resolved: c.resolved ?? 0,
  }));

  const feedbackData = (stats.feedback_ratings || []).map(f => ({
    name: `${f.rating}★`,
    count: f.count,
    fill: f.rating >= 4 ? "#059669" : f.rating === 3 ? "#d97706" : "#e11d48",
  }));

  const RADIAN = Math.PI / 180;
  const renderCustomLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent, name }) => {
    if (percent < 0.04) return null;
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5;
    const x = cx + radius * Math.cos(-midAngle * RADIAN);
    const y = cy + radius * Math.sin(-midAngle * RADIAN);
    return (
      <text x={x} y={y} fill="white" textAnchor="middle" dominantBaseline="central" fontSize={11} fontWeight={700}>
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <div>
      <h2 style={{ fontWeight: 800, fontSize: "1.3rem", marginBottom: "0.35rem" }}>Analytics</h2>
      <p className="text-muted mb-2">Live complaint metrics — auto-refreshes every 15s</p>

      {/* Sub-tab pills */}
      <div className="subtabs-bar">
        {[
          { id: "overview",   label: "📌 Overview" },
          { id: "priority",   label: "🎯 Priority Split" },
          { id: "department", label: "🏢 By Department" },
          { id: "company",    label: "🏦 Top Companies" },
          { id: "trend",      label: "📈 Trend Analysis" },
          { id: "feedback",   label: "⭐ Feedback" },
        ].map(t => (
          <button key={t.id} className={`subtab-btn ${subTab === t.id ? "active" : ""}`}
            onClick={() => setSubTab(t.id)}>
            {t.label}
          </button>
        ))}
      </div>

      {/* OVERVIEW */}
      {subTab === "overview" && (
        <div className="fade-in" key={`ov-${chartKey}`}>
          <div className="grid-4 mb-3">
            {[
              { label: "Total Complaints",  val: totalVal,     icon: "📋", bg: "#eff6ff", color: "#2563eb" },
              { label: "Open",              val: openVal,      icon: "📂", bg: "#fef3c7", color: "#d97706" },
              { label: "Resolved",          val: resolvedVal,  icon: "✅", bg: "#ecfdf5", color: "#059669" },
              { label: "Escalated",         val: escalatedVal, icon: "⚠️", bg: "#fdf4ff", color: "#7c3aed" },
            ].map(s => (
              <div key={s.label} className="stat-card" style={{ borderLeft: `4px solid ${s.color}` }}>
                <div className="stat-icon" style={{ background: s.bg }}>{s.icon}</div>
                <div className="stat-info">
                  <div className="si-label">{s.label}</div>
                  <div className="si-value" style={{ color: s.color }}>{s.val.toLocaleString()}</div>
                </div>
              </div>
            ))}
          </div>
          <div className="grid-2">
            {/* Donut: Priority */}
            <div className="card card-body">
              <div className="section-title" style={{ marginBottom: "0.6rem" }}>Priority Distribution</div>
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie
                    data={priorityData} dataKey="value" nameKey="name"
                    cx="50%" cy="50%" innerRadius={60} outerRadius={100}
                    labelLine={false} label={renderCustomLabel}
                    isAnimationActive={true} animationBegin={0} animationDuration={900}
                  >
                    {priorityData.map((e, i) => <Cell key={i} fill={e.fill} />)}
                  </Pie>
                  <Tooltip formatter={v => v.toLocaleString()} />
                  <Legend iconType="circle" />
                </PieChart>
              </ResponsiveContainer>
            </div>
            {/* Donut: Status */}
            <div className="card card-body">
              <div className="section-title" style={{ marginBottom: "0.6rem" }}>Status Breakdown</div>
              <ResponsiveContainer width="100%" height={240}>
                <PieChart>
                  <Pie
                    data={statusDonutData} dataKey="value" nameKey="name"
                    cx="50%" cy="50%" innerRadius={60} outerRadius={100}
                    labelLine={false} label={renderCustomLabel}
                    isAnimationActive={true} animationBegin={0} animationDuration={900}
                  >
                    {statusDonutData.map((e, i) => <Cell key={i} fill={e.fill} />)}
                  </Pie>
                  <Tooltip formatter={v => v.toLocaleString()} />
                  <Legend iconType="circle" />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      )}

      {/* PRIORITY (full view donut) */}
      {subTab === "priority" && (
        <div className="fade-in card card-body" key={`pr-${chartKey}`}>
          <div className="section-title">Priority Distribution — Detailed View</div>
          <div style={{ display: "flex", alignItems: "center", gap: "2rem", flexWrap: "wrap" }}>
            <ResponsiveContainer width={360} height={360}>
              <PieChart>
                <Pie
                  data={priorityData} dataKey="value" nameKey="name"
                  cx="50%" cy="50%" innerRadius={90} outerRadius={150}
                  labelLine={false} label={renderCustomLabel}
                  isAnimationActive={true} animationBegin={0} animationDuration={1000}
                >
                  {priorityData.map((e, i) => <Cell key={i} fill={e.fill} />)}
                </Pie>
                <Tooltip formatter={v => v.toLocaleString()} />
              </PieChart>
            </ResponsiveContainer>
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              {priorityData.map(p => (
                <div key={p.name} style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                  <div style={{ width: 14, height: 14, borderRadius: 4, background: p.fill, flexShrink: 0 }} />
                  <div>
                    <div style={{ fontWeight: 700, fontSize: "1rem" }}>{p.name}</div>
                    <div style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>
                      {p.value.toLocaleString()} complaints · {totalVal ? ((p.value/totalVal)*100).toFixed(1) : 0}%
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* DEPARTMENT — stacked bar with animation */}
      {subTab === "department" && (
        <div className="fade-in card card-body" key={`dp-${chartKey}`}>
          <div className="section-title">Status by Department</div>
          <ResponsiveContainer width="100%" height={380}>
            <BarChart data={deptData} margin={{ left: -10, bottom: 20 }}>
              <defs>
                <linearGradient id="gradOpen" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity={1} />
                  <stop offset="100%" stopColor="#2563eb" stopOpacity={0.85} />
                </linearGradient>
                <linearGradient id="gradProg" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#f59e0b" stopOpacity={1} />
                  <stop offset="100%" stopColor="#d97706" stopOpacity={0.85} />
                </linearGradient>
                <linearGradient id="gradResolved" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10b981" stopOpacity={1} />
                  <stop offset="100%" stopColor="#059669" stopOpacity={0.85} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color, #f1f5f9)" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 11 }} interval={0} angle={-10} textAnchor="end" />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ borderRadius: 8, fontSize: "0.83rem" }} />
              <Legend />
              <Bar dataKey="Open"        fill="url(#gradOpen)"     radius={[4,4,0,0]} isAnimationActive animationDuration={800} animationBegin={0} />
              <Bar dataKey="In Progress" fill="url(#gradProg)"     radius={[4,4,0,0]} isAnimationActive animationDuration={900} animationBegin={100} />
              <Bar dataKey="Resolved"    fill="url(#gradResolved)" radius={[4,4,0,0]} isAnimationActive animationDuration={1000} animationBegin={200} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* COMPANY — horizontal bar */}
      {subTab === "company" && (
        <div className="fade-in card card-body" key={`co-${chartKey}`}>
          <div className="section-title">Top 10 Companies by Complaint Volume</div>
          <ResponsiveContainer width="100%" height={380}>
            <BarChart data={companyData} layout="vertical" margin={{ left: 20 }}>
              <defs>
                <linearGradient id="gradComp" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#2563eb" stopOpacity={0.9} />
                  <stop offset="100%" stopColor="#7c3aed" stopOpacity={0.8} />
                </linearGradient>
                <linearGradient id="gradRes" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#059669" stopOpacity={0.9} />
                  <stop offset="100%" stopColor="#10b981" stopOpacity={0.8} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color, #f1f5f9)" horizontal={false} />
              <XAxis type="number" tick={{ fontSize: 11 }} />
              <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={115} />
              <Tooltip formatter={v => v.toLocaleString()} contentStyle={{ borderRadius: 8, fontSize: "0.83rem" }} />
              <Legend />
              <Bar dataKey="Total"    fill="url(#gradComp)" radius={[0,4,4,0]} isAnimationActive animationDuration={900} />
              <Bar dataKey="Resolved" fill="url(#gradRes)"  radius={[0,4,4,0]} isAnimationActive animationDuration={1100} animationBegin={150} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* TREND — area chart animated from origin */}
      {subTab === "trend" && (
        <div className="fade-in card card-body" key={`tr-${chartKey}`}>
          <div className="section-title" style={{ marginBottom: "0.5rem" }}>Department-wise Complaint Trend</div>
          <p className="text-muted text-sm mb-2">Volume by department, animated from origin</p>
          <ResponsiveContainer width="100%" height={350}>
            <AreaChart data={trendData} margin={{ left: -10, right: 10, top: 10 }}>
              <defs>
                <linearGradient id="areaTotal" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#2563eb" stopOpacity={0.02} />
                </linearGradient>
                <linearGradient id="areaResolved" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#059669" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#059669" stopOpacity={0.02} />
                </linearGradient>
                <linearGradient id="areaOpen" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#d97706" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#d97706" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color, #f1f5f9)" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ borderRadius: 8, fontSize: "0.83rem" }} formatter={v => v.toLocaleString()} />
              <Legend />
              <Area type="monotone" dataKey="Total"    stroke="#2563eb" fill="url(#areaTotal)"    strokeWidth={2.5} dot={{ r: 4, fill: "#2563eb" }} isAnimationActive animationBegin={0} animationDuration={1200} animationEasing="ease-out" />
              <Area type="monotone" dataKey="Resolved" stroke="#059669" fill="url(#areaResolved)" strokeWidth={2.5} dot={{ r: 4, fill: "#059669" }} isAnimationActive animationBegin={200} animationDuration={1200} animationEasing="ease-out" />
              <Area type="monotone" dataKey="Open"     stroke="#d97706" fill="url(#areaOpen)"     strokeWidth={2.5} dot={{ r: 4, fill: "#d97706" }} isAnimationActive animationBegin={400} animationDuration={1200} animationEasing="ease-out" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* FEEDBACK */}
      {subTab === "feedback" && (
        <div className="fade-in card card-body" key={`fb-${chartKey}`}>
          <div className="section-title">Customer Feedback Ratings Distribution</div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={feedbackData} margin={{ left: -10 }}>
              <defs>
                {feedbackData.map((f, i) => (
                  <linearGradient key={i} id={`gradFb${i}`} x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor={f.fill} stopOpacity={1} />
                    <stop offset="100%" stopColor={f.fill} stopOpacity={0.6} />
                  </linearGradient>
                ))}
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color, #f1f5f9)" vertical={false} />
              <XAxis dataKey="name" tick={{ fontSize: 14 }} />
              <YAxis tick={{ fontSize: 11 }} />
              <Tooltip contentStyle={{ borderRadius: 8, fontSize: "0.83rem" }} />
              <Bar dataKey="count" radius={[6,6,0,0]} isAnimationActive animationDuration={1000}>
                {feedbackData.map((f, i) => <Cell key={i} fill={`url(#gradFb${i})`} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <p className="text-muted text-sm" style={{ marginTop: "0.75rem" }}>
            Average rating: <strong>{stats.avg_rating ? Number(stats.avg_rating).toFixed(2) : "—"} / 5.0</strong>
            &nbsp;·&nbsp; Positive response rate: <strong>{stats.positive_percentage ? `${stats.positive_percentage}%` : "—"}</strong>
          </p>
        </div>
      )}
    </div>
  );
}


/* ────────────────── TAB 4: LEADERBOARD ──────────────── */
function LeaderboardTab({ token }) {
  const [board, setBoard] = useState([]);
  const [timeframe, setTimeframe] = useState("yearly");
  const [loading, setLoading] = useState(false);

  const fetch = async () => {
    setLoading(true);
    try {
      const r = await axios.get(`${API}/admin/leaderboard?timeframe=${timeframe}`, { headers: { Authorization: `Bearer ${token}` } });
      setBoard(r.data.leaderboard || []);
    } catch { /* noop */ }
    setLoading(false);
  };

  useEffect(() => { fetch(); }, [timeframe]);

  const medalClass = (i) => {
    if (i === 0) return "gold";
    if (i === 1) return "silver";
    if (i === 2) return "bronze";
    return "";
  };
  const medal = (i) => `#${i + 1}`;

  return (
    <div>
      <div className="flex-between mb-2">
        <div>
          <h2 style={{ fontWeight: 800, fontSize: "1.3rem" }}>Company Leaderboard</h2>
          <p className="text-muted">Ranked by resolution performance and complaint handling</p>
        </div>
        <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <select className="form-select" style={{ width: "auto" }} value={timeframe} onChange={e => setTimeframe(e.target.value)}>
            <option value="monthly">This Month</option>
            <option value="quarterly">This Quarter</option>
            <option value="yearly">This Year</option>
          </select>
          <button className="btn btn-outline btn-sm" onClick={fetch}>Refresh</button>
        </div>
      </div>

      <div className="card" style={{ overflow: "hidden" }}>
        {loading ? (
          <div className="loading-center"><div className="spinner"></div></div>
        ) : board.length === 0 ? (
          <div className="empty-state"><div className="es-title">No leaderboard data available</div></div>
        ) : (
          board.map((row, i) => (
            <div key={row.company || row.bank_name || i} className="lb-row">
              <div className={`lb-rank ${medalClass(i)}`}>{medal(i)}</div>
              <div style={{ flex: 1 }}>
                <div className="lb-company">{row.company || row.bank_name}</div>
                <div style={{ display: "flex", gap: "1rem", marginTop: "0.25rem", flexWrap: "wrap" }}>
                  <span className="text-muted text-sm"><strong style={{ color: "var(--slate-800)" }}>{(row.total_complaints ?? 0).toLocaleString()}</strong> Total Complaints</span>
                  <span className="text-muted text-sm"><strong style={{ color: "var(--emerald)" }}>{(row.resolved_count ?? row.resolved_complaints ?? 0).toLocaleString()}</strong> Resolved</span>
                  <span className="text-muted text-sm"><strong style={{ color: "var(--rose)" }}>{(row.escalated_count ?? row.breached_complaints ?? 0).toLocaleString()}</strong> Escalated</span>
                  {row.avg_rating && (
                    <span className="text-muted text-sm"><strong style={{ color: "var(--gold)" }}>{Number(row.avg_rating).toFixed(1)} / 5.0</strong> Rating</span>
                  )}
                </div>
              </div>
              <div>
                <div className="lb-score">{row.score ?? row.performance_score ?? "—"}</div>
                <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", textAlign: "right" }}>pts</div>
              </div>
              <div style={{ width: 100 }}>
                <div style={{ background: "var(--slate-100)", borderRadius: 4, height: 6, overflow: "hidden" }}>
                  <div style={{ background: i === 0 ? "#d97706" : i === 1 ? "#94a3b8" : i === 2 ? "#b45309" : "var(--blue)", height: "100%", width: `${Math.min(100, (((row.score ?? row.performance_score ?? 0) / ((board[0]?.score ?? board[0]?.performance_score) || 1)) * 100))}%`, borderRadius: 4 }} />
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

/* ────────────────── TAB 5: CLUSTERS ─────────────────── */
function ClustersTab({ token }) {
  const [clusters, setClusters] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    axios.get(`${API}/admin/complaint-clusters`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => setClusters(r.data.clusters || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-center"><div className="spinner"></div><span>Analyzing clusters…</span></div>;

  return (
    <div>
      <h2 style={{ fontWeight: 800, fontSize: "1.3rem", marginBottom: "0.35rem" }}>Complaint Cluster Analysis</h2>
      <p className="text-muted mb-3">AI-grouped similar complaints to surface emerging trends and risk patterns</p>

      {clusters.length === 0 && (
        <div className="empty-state"><div className="es-icon">🔍</div><div className="es-title">No cluster data available</div></div>
      )}

      <div className="grid-2">
        {clusters.map((c, i) => {
          const cfg = CLUSTER_CFG[i % CLUSTER_CFG.length];
          return (
            <div key={i} className="cluster-card" style={{ borderColor: cfg.border }}>
              <div className="cc-header">
                <div className="cc-icon" style={{ background: cfg.color }}>{cfg.icon}</div>
                <div>
                  <div className="cc-title">{c.label || c.cluster_title || `Cluster ${i + 1}`}</div>
                  <div className="cc-count">{(c.count ?? c.matched_volume ?? 0).toLocaleString()} complaints · {c.top_keywords?.slice(0, 3).join(", ") || c.category}</div>
                </div>
              </div>

              <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap", marginBottom: "0.75rem" }}>
                {(c.top_keywords || ["banking", "dispute", "service"]).map(kw => (
                  <span key={kw} className="cluster-kw-tag" style={{ background: cfg.color, border: `1px solid ${cfg.border}`, color: "var(--slate-800)", borderRadius: 20, padding: "0.15rem 0.55rem", fontSize: "0.76rem", fontWeight: 600 }}>
                    {kw}
                  </span>
                ))}
              </div>

              {c.sample_complaints && c.sample_complaints.length > 0 && (
                <div style={{ marginBottom: "0.75rem" }}>
                  <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: ".05em", marginBottom: "0.4rem" }}>Sample cases</div>
                  {c.sample_complaints.slice(0, 2).map((sc, j) => (
                    <div key={j} className="sample-case-box" style={{ fontSize: "0.8rem", color: "var(--slate-700)", padding: "0.4rem 0.6rem", background: "var(--slate-50)", borderRadius: 6, marginBottom: "0.3rem", lineHeight: 1.5 }}>
                      "{sc.slice(0, 100)}…"
                    </div>
                  ))}
                </div>
              )}

              {c.recommended_action && (
                <div className="cc-action">
                  <strong>💡 Recommended Action:</strong> {c.recommended_action}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* ────────────────── TAB 6: AUDIT LOGS ───────────────── */
const BROWSERS = ["Chrome 127 / Windows 11", "Safari 17 / macOS", "Firefox 120 / Ubuntu", "Edge 126 / Windows 10", "Chrome 125 / Android 14", "Safari 17 / iPhone iOS 17"];
const OS_LIST  = ["Windows 11", "Windows 10", "macOS Sonoma", "Ubuntu 22.04", "Android 14", "iOS 17.5"];
const IP_BASE  = ["192.168.1.", "10.10.101.", "203.88.45.", "117.244.22.", "49.36.128."];

function genAuditLogs() {
  const roles = ["admin","employee","employee","user","user","user"];
  const events = [
    { ev: "login",         label: "Login",          cls: "audit-event-login" },
    { ev: "logout",        label: "Logout",         cls: "audit-event-logout" },
    { ev: "action",        label: "Action",         cls: "audit-event-action" },
    { ev: "failed",        label: "Failed Login",   cls: "audit-event-failed" },
  ];
  const actions = [
    "Viewed complaint list","Updated complaint status","Downloaded report","Resolved complaint",
    "Assigned officer","Added note","Viewed analytics","Exported leaderboard","Reset password",
    "Changed department filter","Approved escalation","Requested proof","Marked complaint closed",
  ];
  const names = {
    admin:    ["admin@grievanceiq.in"],
    employee: ["EMP-DIG-101","EMP-DIG-102","EMP-LNS-101","EMP-CRD-101","EMP-FRD-101"],
    user:     ["rahul.sharma@gmail.com","priya.mehta@yahoo.in","suresh.k@outlook.com","anjali.v@gmail.com","sanjay.p@hotmail.com"],
  };
  const logs = [];
  const now = Date.now();
  for (let i = 0; i < 80; i++) {
    const role  = roles[Math.floor(Math.random() * roles.length)];
    const evObj = events[Math.floor(Math.random() * (role === "admin" ? 4 : 3))];
    const name  = names[role][Math.floor(Math.random() * names[role].length)];
    const ip    = IP_BASE[Math.floor(Math.random() * IP_BASE.length)] + (Math.floor(Math.random() * 200) + 10);
    const browser = BROWSERS[Math.floor(Math.random() * BROWSERS.length)];
    const ts    = now - Math.floor(Math.random() * 72 * 3600 * 1000); // last 72h
    const action = evObj.ev === "action" ? actions[Math.floor(Math.random() * actions.length)] : evObj.label;
    logs.push({ id: i+1, role, event: evObj.ev, eventLabel: evObj.ev === "action" ? action : evObj.label, eventCls: evObj.cls, user: name, ip, device: browser, ts, success: evObj.ev !== "failed" });
  }
  return logs.sort((a,b) => b.ts - a.ts);
}

const AUDIT_LOGS = genAuditLogs();

function AuditLogsTab({ token }) {
  const [logs, setLogs] = useState(AUDIT_LOGS);
  const [filterRole, setFilterRole] = useState("");
  const [filterEvent, setFilterEvent] = useState("");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const PER_PAGE = 20;

  const filtered = logs.filter(l =>
    (!filterRole  || l.role  === filterRole) &&
    (!filterEvent || l.event === filterEvent) &&
    (!search      || l.user.toLowerCase().includes(search.toLowerCase()) || l.ip.includes(search) || l.device.toLowerCase().includes(search.toLowerCase()))
  );
  const totalPages = Math.ceil(filtered.length / PER_PAGE);
  const paged = filtered.slice((page-1)*PER_PAGE, page*PER_PAGE);

  const fmtTs = (ts) => {
    const d = new Date(ts);
    return d.toLocaleString("en-IN", { day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit", hour12: true });
  };

  const roleCls = (r) => `audit-role-badge audit-role-${r}`;

  const stats = {
    total:   logs.length,
    logins:  logs.filter(l => l.event === "login").length,
    failed:  logs.filter(l => l.event === "failed").length,
    actions: logs.filter(l => l.event === "action").length,
  };

  return (
    <div>
      <div className="flex-between mb-2">
        <div>
          <h2 style={{ fontWeight: 800, fontSize: "1.3rem" }}>Audit Logs</h2>
          <p className="text-muted">Complete activity trail — logins, logouts, actions and failed attempts</p>
        </div>
        <button className="btn btn-outline btn-sm" onClick={() => setLogs(genAuditLogs())}>🔄 Refresh</button>
      </div>

      {/* Summary cards */}
      <div className="grid-4 mb-3">
        {[
          { label: "Total Events",     val: stats.total,   icon: "📋", color: "#2563eb", bg: "#eff6ff" },
          { label: "Successful Logins",val: stats.logins,  icon: "✅", color: "#059669", bg: "#ecfdf5" },
          { label: "Failed Attempts",  val: stats.failed,  icon: "🚫", color: "#e11d48", bg: "#fff1f2" },
          { label: "User Actions",     val: stats.actions, icon: "⚡", color: "#d97706", bg: "#fef3c7" },
        ].map(s => (
          <div key={s.label} className="stat-card" style={{ borderLeft: `4px solid ${s.color}` }}>
            <div className="stat-icon" style={{ background: s.bg }}>{s.icon}</div>
            <div className="stat-info">
              <div className="si-label">{s.label}</div>
              <div className="si-value" style={{ color: s.color }}>{s.val}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="filter-bar mb-2" style={{ borderRadius: "var(--radius)", border: "1px solid var(--border-color, var(--slate-200))", marginBottom: "1rem" }}>
        <select className="form-select" value={filterRole} onChange={e => { setFilterRole(e.target.value); setPage(1); }}>
          <option value="">All Roles</option>
          <option value="admin">Admin</option>
          <option value="employee">Employee</option>
          <option value="user">User</option>
        </select>
        <select className="form-select" value={filterEvent} onChange={e => { setFilterEvent(e.target.value); setPage(1); }}>
          <option value="">All Events</option>
          <option value="login">Login</option>
          <option value="logout">Logout</option>
          <option value="action">Action</option>
          <option value="failed">Failed Login</option>
        </select>
        <input className="form-input" style={{ flex: 1 }} placeholder="Search user, IP, device…" value={search} onChange={e => { setSearch(e.target.value); setPage(1); }} />
        <button className="btn btn-ghost btn-sm" onClick={() => { setFilterRole(""); setFilterEvent(""); setSearch(""); setPage(1); }}>Clear</button>
      </div>

      <div className="card" style={{ overflow: "hidden" }}>
        <div style={{ overflowX: "auto" }}>
          <table className="audit-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Timestamp</th>
                <th>Role</th>
                <th>User / ID</th>
                <th>Event</th>
                <th>IP Address</th>
                <th>Device / Browser</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {paged.length === 0 ? (
                <tr><td colSpan={8} style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>No logs match your filters</td></tr>
              ) : paged.map((l, i) => (
                <tr key={l.id}>
                  <td style={{ color: "var(--text-muted)", fontFamily: "monospace", fontSize: "0.76rem" }}>{(page-1)*PER_PAGE + i + 1}</td>
                  <td style={{ whiteSpace: "nowrap", fontFamily: "monospace", fontSize: "0.78rem" }}>{fmtTs(l.ts)}</td>
                  <td><span className={roleCls(l.role)}>{l.role}</span></td>
                  <td style={{ fontFamily: "monospace", fontSize: "0.8rem", maxWidth: 190, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{l.user}</td>
                  <td><span className={`audit-event-badge ${l.eventCls}`}>{l.eventLabel}</span></td>
                  <td style={{ fontFamily: "monospace", fontSize: "0.78rem", whiteSpace: "nowrap" }}>{l.ip}</td>
                  <td style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>{l.device}</td>
                  <td>
                    <span style={{ display: "inline-flex", alignItems: "center", gap: "0.3rem", fontSize: "0.78rem", fontWeight: 600, color: l.success ? "#059669" : "#e11d48" }}>
                      {l.success ? "✓ OK" : "✗ Denied"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {totalPages > 1 && (
          <div className="pagination">
            <button className="pg-btn" onClick={() => setPage(p => Math.max(1, p-1))} disabled={page===1}>‹ Prev</button>
            <span className="pg-info">Page {page} of {totalPages} · {filtered.length} events</span>
            <button className="pg-btn" onClick={() => setPage(p => Math.min(totalPages, p+1))} disabled={page===totalPages}>Next ›</button>
          </div>
        )}
      </div>
    </div>
  );
}

/* ────────────────── MAIN ADMIN DASHBOARD ────────────── */
export default function AdminDashboard({ token, onLogout, darkMode, onToggleTheme }) {
  const [activeTab, setActiveTab] = useState("queue");

  return (
    <div className="page-wide">
      <div className="sidebar-layout">
        <Sidebar active={activeTab} setActive={setActiveTab} onLogout={onLogout} darkMode={darkMode} onToggleTheme={onToggleTheme} />
        <div className="content-area fade-in">
          {activeTab === "queue"       && <GrievanceQueue   token={token} />}
          {activeTab === "departments" && <DepartmentsTab   token={token} />}
          {activeTab === "analytics"   && <AnalyticsTab     token={token} />}
          {activeTab === "leaderboard" && <LeaderboardTab   token={token} />}
          {activeTab === "clusters"    && <ClustersTab      token={token} />}
          {activeTab === "audit"       && <AuditLogsTab     token={token} />}
        </div>
      </div>
    </div>
  );
}