import { useState, useEffect, useRef } from "react";
import axios from "axios";
import SubmitComplaint from "./SubmitComplaint";

const API = "http://127.0.0.1:8000";

const STAGES = ["Submitted", "Triage", "Investigation", "Resolution", "Closed"];

function stageIndex(status) {
  if (!status) return 0;
  const s = status.toLowerCase();
  if (s === "submitted") return 0;
  if (s === "open")      return 1;
  if (s === "in_progress" || s === "investigation") return 2;
  if (s === "resolved")  return 3;
  if (s === "closed")    return 4;
  return 0;
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

function priorityClass(p) {
  if (p === "High")   return "badge badge-high";
  if (p === "Medium") return "badge badge-medium";
  return "badge badge-low";
}

function fmtDate(d) {
  if (!d) return "—";
  return new Date(d).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" });
}

/* ─── Top Nav ────────────────────────────────────────── */
function TopNav({ user, onLogout, onOpenProfile, darkMode, onToggleTheme }) {
  const [open, setOpen] = useState(false);
  const ref = useRef();
  useEffect(() => {
    const fn = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", fn);
    return () => document.removeEventListener("mousedown", fn);
  }, []);

  const initials = (user?.name || "U").split(" ").map(w => w[0]).join("").toUpperCase().slice(0, 2);

  return (
    <nav className="topnav">
      <div className="topnav-brand">
        <span className="brand-name">GrievanceIQ</span>
        <span className="brand-tag">Customer Portal</span>
      </div>
      <div className="topnav-right">
        <span className="topnav-badge">🏦 Banking Grievance System</span>
        <button className="theme-toggle" onClick={onToggleTheme} title="Toggle theme">
          {darkMode ? "☀️ Light" : "🌙 Dark"}
        </button>
        <div className="dropdown-container" ref={ref}>
          <div className="avatar-btn" onClick={() => setOpen(o => !o)}>
            {user?.avatar_url
              ? <img src={`${API}${user.avatar_url}`} alt="avatar" />
              : initials}
          </div>
          {open && (
            <div className="dropdown-menu">
              <div className="dropdown-header">
                <div className="dh-name">{user?.name || "User"}</div>
                <div className="dh-email">{user?.email}</div>
              </div>
              <div className="dropdown-item" onClick={() => { setOpen(false); onOpenProfile(); }}>
                ⚙️ Profile Settings
              </div>
              <hr className="dropdown-divider" />
              <div className="dropdown-item danger" onClick={onLogout}>🚪 Logout</div>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}

/* ─── Stage Tracker ─────────────────────────────────── */
function StageTracker({ status }) {
  const current = stageIndex(status);
  return (
    <div className="stage-tracker">
      {STAGES.map((s, i) => (
        <div key={s} className={`stage-step ${i < current ? "done" : i === current ? "active" : ""}`}>
          <div className="stage-circle">
            {i < current ? "✓" : i + 1}
          </div>
          <div className="stage-label">{s}</div>
        </div>
      ))}
    </div>
  );
}

/* ─── Complaint Detail Modal ─────────────────────────── */
function ComplaintDetailModal({ complaint: c, onClose, onAppeal, onEvidence, userToken }) {
  const [appealText, setAppealText] = useState("");
  const [submittingAppeal, setSubmittingAppeal] = useState(false);
  const [appealDone, setAppealDone] = useState(false);
  const [evidenceFile, setEvidenceFile] = useState(null);
  const [uploadingEvidence, setUploadingEvidence] = useState(false);
  const [evidenceDone, setEvidenceDone] = useState(false);
  const [appealErr, setAppealErr] = useState("");

  const submitAppeal = async () => {
    if (!appealText.trim()) return;
    setSubmittingAppeal(true); setAppealErr("");
    try {
      await axios.post(`${API}/complaint/${c.token}/appeal`,
        { appeal_text: appealText, is_satisfied: false },
        { headers: { Authorization: `Bearer ${userToken}` } }
      );
      setAppealDone(true);
      if (onAppeal) onAppeal();
    } catch (err) {
      setAppealErr(err?.response?.data?.detail || "Failed to submit appeal.");
    }
    setSubmittingAppeal(false);
  };

  const markSatisfied = async () => {
    try {
      await axios.post(`${API}/complaint/${c.token}/appeal`,
        { appeal_text: "Customer marked as satisfied.", is_satisfied: true },
        { headers: { Authorization: `Bearer ${userToken}` } }
      );
      if (onAppeal) onAppeal();
      onClose();
    } catch (err) { /* noop */ }
  };

  const submitEvidence = async () => {
    if (!evidenceFile) return;
    setUploadingEvidence(true);
    const fd = new FormData();
    fd.append("file", evidenceFile);
    try {
      await axios.post(`${API}/complaint/${c.token}/evidence`, fd,
        { headers: { Authorization: `Bearer ${userToken}`, "Content-Type": "multipart/form-data" } }
      );
      setEvidenceDone(true);
    } catch { /* noop */ }
    setUploadingEvidence(false);
  };

  const status = c.status?.toLowerCase();
  const isResolved = status === "resolved" || status === "closed";
  const isRejected = status === "rejected";
  const needsMoreProof = c.requires_more_proof;

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal-box modal-wide fade-in">
        <div className="modal-header">
          <h3>Grievance Details — <span style={{ fontFamily: "monospace", color: "var(--text-muted)" }}>{c.token}</span></h3>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>

        <div className="modal-body">
          {/* Stage Tracker */}
          <StageTracker status={c.status} />

          {/* Status banners */}
          {isRejected && c.rejection_reason && (
            <div className="alert alert-error mb-2">
              <div><strong>❌ Complaint Rejected</strong><br />{c.rejection_reason}</div>
            </div>
          )}
          {needsMoreProof && c.requires_more_proof && (
            <div className="alert alert-warn mb-2">
              <div><strong>📎 Additional Evidence Required</strong><br />{c.requires_more_proof}</div>
            </div>
          )}
          {isResolved && c.resolution_notes && (
            <div className="alert alert-success mb-2">
              <div><strong>✅ Resolved</strong><br />{c.resolution_notes}</div>
            </div>
          )}

          {/* Core details */}
          <div className="section-title" style={{ marginTop: "1rem" }}>Grievance Information</div>
          <div className="detail-grid mb-2">
            <div className="detail-field"><span className="df-label">Company</span><span className="df-value">{c.company || "—"}</span></div>
            <div className="detail-field"><span className="df-label">Department</span><span className="df-value">{c.department || "—"}</span></div>
            <div className="detail-field"><span className="df-label">Priority</span>
              <span><span className={priorityClass(c.priority)}>{c.priority}</span></span>
            </div>
            <div className="detail-field"><span className="df-label">Status</span>
              <span><span className={statusBadgeClass(c.status)}>{c.status}</span></span>
            </div>
            <div className="detail-field"><span className="df-label">Service Type</span><span className="df-value">{c.service_type || "—"}</span></div>
            <div className="detail-field"><span className="df-label">Amount</span><span className="df-value">{c.amount ? `₹${c.amount}` : "—"}</span></div>
            <div className="detail-field"><span className="df-label">Reference ID</span><span className="df-value" style={{ fontFamily: "monospace" }}>{c.reference_id || "—"}</span></div>
            <div className="detail-field"><span className="df-label">Branch</span><span className="df-value">{c.branch || "—"}</span></div>
            <div className="detail-field"><span className="df-label">Transaction Date</span><span className="df-value">{c.transaction_date || "—"}</span></div>
            <div className="detail-field"><span className="df-label">Submitted On</span><span className="df-value">{fmtDate(c.created_at)}</span></div>
          </div>

          {c.priority_reason && (
            <>
              <div className="section-title">Why this priority?</div>
              <p style={{ fontSize: "0.86rem", color: "var(--slate-700)", marginBottom: "1rem", lineHeight: 1.6 }}>{c.priority_reason}</p>
            </>
          )}

          <div className="section-title">Description</div>
          <div style={{ background: "var(--slate-50)", borderRadius: "var(--radius-sm)", padding: "0.9rem 1rem", fontSize: "0.88rem", lineHeight: 1.7, marginBottom: "1rem", border: "1px solid var(--slate-200)" }}>
            {c.description || "No description provided."}
          </div>

          {c.proof_url && (
            <>
              <div className="section-title">Files Submitted</div>
              <a href={`${API}${c.proof_url}`} target="_blank" rel="noreferrer" className="btn btn-outline btn-sm mb-2">
                📎 View Proof Document
              </a>
            </>
          )}

          {c.resolution_proof_url && (
            <>
              <div className="section-title">Resolution Proof</div>
              <a href={`${API}${c.resolution_proof_url}`} target="_blank" rel="noreferrer" className="btn btn-outline btn-sm mb-2">
                📄 View Resolution Document
              </a>
            </>
          )}

          {/* Upload additional evidence if requested */}
          {needsMoreProof && !evidenceDone && (
            <div style={{ marginTop: "1rem" }}>
              <div className="section-title">Upload Additional Evidence</div>
              <div style={{ display: "flex", gap: "0.6rem", alignItems: "center", flexWrap: "wrap" }}>
                <input type="file" className="form-input" style={{ flex: 1 }}
                  onChange={e => setEvidenceFile(e.target.files[0])} />
                <button className="btn btn-primary btn-sm" onClick={submitEvidence} disabled={uploadingEvidence || !evidenceFile}>
                  {uploadingEvidence ? "Uploading…" : "Upload"}
                </button>
              </div>
            </div>
          )}
          {evidenceDone && <div className="alert alert-success mt-1">Evidence uploaded successfully!</div>}

          {/* Satisfied / Appeal after resolution */}
          {isResolved && !c.customer_appeal && !c.satisfaction_status && (
            <div style={{ marginTop: "1.25rem" }}>
              <div className="section-title">Your Response</div>
              <p style={{ fontSize: "0.86rem", color: "var(--text-muted)", marginBottom: "0.75rem" }}>
                Are you satisfied with the resolution? If not, you can raise an appeal.
              </p>
              {!appealDone ? (
                <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                  <textarea className="form-textarea" placeholder="Describe why the resolution was insufficient…"
                    value={appealText} onChange={e => setAppealText(e.target.value)} rows={3} />
                  {appealErr && <div className="alert alert-error">{appealErr}</div>}
                  <div style={{ display: "flex", gap: "0.6rem" }}>
                    <button className="btn btn-rose btn-sm" onClick={submitAppeal} disabled={submittingAppeal || !appealText.trim()}>
                      {submittingAppeal ? "Submitting…" : "🔁 Raise Appeal"}
                    </button>
                    <button className="btn btn-emerald btn-sm" onClick={markSatisfied}>
                      ✅ I'm Satisfied
                    </button>
                  </div>
                </div>
              ) : (
                <div className="alert alert-info">Appeal submitted. Our team will review it.</div>
              )}
            </div>
          )}

          {c.customer_appeal && (
            <div style={{ marginTop: "1rem" }}>
              <div className="section-title">Your Appeal</div>
              <div style={{ background: "var(--rose-light)", borderRadius: "var(--radius-sm)", padding: "0.9rem 1rem", fontSize: "0.86rem", border: "1px solid #fecaca" }}>
                {c.customer_appeal}
              </div>
            </div>
          )}

          {c.satisfaction_status === "satisfied" && (
            <div className="alert alert-success mt-2">✅ You marked this grievance as resolved and satisfactory.</div>
          )}
        </div>
      </div>
    </div>
  );
}

/* ─── Profile Modal ──────────────────────────────────── */
function ProfileModal({ user, userToken, onClose, onUpdate }) {
  const [form, setForm] = useState({
    name: user?.name || "",
    phone: user?.phone || "",
    address: user?.address || "",
    birthdate: user?.birthdate || "",
  });
  const [avatarFile, setAvatarFile] = useState(null);
  const [saving, setSaving] = useState(false);
  const [uploadingAvatar, setUploadingAvatar] = useState(false);
  const [msg, setMsg] = useState("");

  const save = async () => {
    setSaving(true); setMsg("");
    try {
      const r = await axios.put(`${API}/user/profile`, form,
        { headers: { Authorization: `Bearer ${userToken}` } }
      );
      onUpdate(prev => ({ ...prev, ...r.data }));
      setMsg("Profile updated!");
    } catch { setMsg("Failed to update."); }
    setSaving(false);
  };

  const uploadAvatar = async () => {
    if (!avatarFile) return;
    setUploadingAvatar(true);
    const fd = new FormData(); fd.append("file", avatarFile);
    try {
      const r = await axios.post(`${API}/user/avatar`, fd,
        { headers: { Authorization: `Bearer ${userToken}`, "Content-Type": "multipart/form-data" } }
      );
      onUpdate(prev => ({ ...prev, avatar_url: r.data.avatar_url }));
      setMsg("Avatar updated!");
    } catch { setMsg("Avatar upload failed."); }
    setUploadingAvatar(false);
  };

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }));

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal-box fade-in">
        <div className="modal-header">
          <h3>⚙️ Profile Settings</h3>
          <button className="modal-close" onClick={onClose}>✕</button>
        </div>
        <div className="modal-body">
          {/* Avatar */}
          <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "1.5rem" }}>
            <div className="avatar-btn" style={{ width: 60, height: 60, fontSize: "1.3rem", flexShrink: 0 }}>
              {user?.avatar_url
                ? <img src={`${API}${user.avatar_url}`} alt="avatar" style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                : (user?.name || "U").split(" ").map(w => w[0]).join("").toUpperCase().slice(0, 2)}
            </div>
            <div style={{ flex: 1 }}>
              <input type="file" accept="image/*" className="form-input" onChange={e => setAvatarFile(e.target.files[0])} />
              <button className="btn btn-outline btn-sm" style={{ marginTop: "0.4rem" }}
                onClick={uploadAvatar} disabled={uploadingAvatar || !avatarFile}>
                {uploadingAvatar ? "Uploading…" : "Upload Photo"}
              </button>
            </div>
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input className="form-input" value={form.name} onChange={e => set("name", e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label">Email</label>
              <input className="form-input" value={user?.email || ""} disabled style={{ opacity: 0.6 }} />
            </div>
            <div className="form-group">
              <label className="form-label">Phone</label>
              <input className="form-input" value={form.phone} onChange={e => set("phone", e.target.value)} placeholder="+91 9XXXXXXXXX" />
            </div>
            <div className="form-group">
              <label className="form-label">Date of Birth</label>
              <input className="form-input" type="date" value={form.birthdate} onChange={e => set("birthdate", e.target.value)} />
            </div>
          </div>
          <div className="form-group">
            <label className="form-label">Address</label>
            <textarea className="form-textarea" rows={2} value={form.address}
              onChange={e => set("address", e.target.value)} placeholder="Street, City, State, PIN" />
          </div>

          {msg && <div className={`alert ${msg.includes("fail") ? "alert-error" : "alert-success"} mb-2`}>{msg}</div>}
        </div>
        <div className="modal-footer">
          <button className="btn btn-outline" onClick={onClose}>Cancel</button>
          <button className="btn btn-primary" onClick={save} disabled={saving}>
            {saving ? "Saving…" : "Save Changes"}
          </button>
        </div>
      </div>
    </div>
  );
}

/* ─── Main UserDashboard ─────────────────────────────── */
export default function UserDashboard({ userToken, user, onLogout, onUserUpdate, darkMode, onToggleTheme }) {
  const [tab, setTab] = useState("complaints"); // "complaints" | "submit"
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [showProfile, setShowProfile] = useState(false);
  const [currentUser, setCurrentUser] = useState(user);

  const fetchComplaints = async () => {
    if (!userToken) return;
    setLoading(true);
    try {
      const r = await axios.get(`${API}/user/complaints`, {
        headers: { Authorization: `Bearer ${userToken}` }
      });
      setComplaints(r.data);
    } catch { /* noop */ }
    setLoading(false);
  };

  useEffect(() => {
    fetchComplaints();
    const iv = setInterval(fetchComplaints, 20000);
    return () => clearInterval(iv);
  }, [userToken]);

  const updateUser = (updater) => {
    setCurrentUser(prev => {
      const next = typeof updater === "function" ? updater(prev) : updater;
      localStorage.setItem("user_info", JSON.stringify(next));
      onUserUpdate(next);
      return next;
    });
  };

  return (
    <>
      <TopNav
        user={currentUser}
        onLogout={onLogout}
        onOpenProfile={() => setShowProfile(true)}
        darkMode={darkMode}
        onToggleTheme={onToggleTheme}
      />

      {/* Tab bar */}
      <div className="tabs-bar">
        <button className={`tab-btn ${tab === "submit" ? "active" : ""}`} onClick={() => setTab("submit")}>
          📝 Lodge Complaint
        </button>
        <button className={`tab-btn ${tab === "complaints" ? "active" : ""}`} onClick={() => { setTab("complaints"); fetchComplaints(); }}>
          📋 My Grievances {complaints.length > 0 && <span style={{ background: "var(--slate-200)", borderRadius: "10px", padding: "0 6px", marginLeft: 4, fontSize: "0.78rem" }}>{complaints.length}</span>}
        </button>
      </div>

      <div className="page" style={{ paddingTop: "1.5rem" }}>
        {/* SUBMIT TAB */}
        {tab === "submit" && (
          <SubmitComplaint
            user={currentUser}
            userToken={userToken}
            onSuccess={(token) => {
              fetchComplaints();
              setTab("complaints");
            }}
          />
        )}

        {/* MY COMPLAINTS TAB */}
        {tab === "complaints" && (
          <div className="fade-in">
            <div className="flex-between mb-2">
              <div>
                <h2 style={{ fontWeight: 800, fontSize: "1.3rem" }}>My Grievances</h2>
                <p className="text-muted">{complaints.length} complaint{complaints.length !== 1 ? "s" : ""} found</p>
              </div>
              <button className="btn btn-outline btn-sm" onClick={fetchComplaints}>🔄 Refresh</button>
            </div>

            {loading && (
              <div className="loading-center"><div className="spinner"></div><span>Loading…</span></div>
            )}

            {!loading && complaints.length === 0 && (
              <div className="empty-state">
                <div className="es-icon">📭</div>
                <div className="es-title">No grievances yet</div>
                <div className="es-text">Click "Lodge Complaint" to submit your first banking grievance.</div>
              </div>
            )}

            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {complaints.map(c => (
                <div key={c.token} className="complaint-card" onClick={() => setSelectedComplaint(c)}>
                  <div className="cc-left">
                    <div className="cc-token">#{c.token}</div>
                    <div className="cc-title">{c.description?.slice(0, 80) || "No description"}…</div>
                    <div className="cc-meta">{c.company} · {c.department} · {fmtDate(c.created_at)}</div>
                  </div>
                  <div className="cc-right">
                    <span className={priorityClass(c.priority)}>{c.priority}</span>
                    <span className={statusBadgeClass(c.status)}>{c.status?.replace("_", " ")}</span>
                    {c.is_escalated && <span className="badge badge-escalated">⚠ Escalated</span>}
                    <span style={{ color: "var(--text-muted)", fontSize: "1.1rem" }}>›</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Complaint detail modal */}
      {selectedComplaint && (
        <ComplaintDetailModal
          complaint={selectedComplaint}
          userToken={userToken}
          onClose={() => setSelectedComplaint(null)}
          onAppeal={fetchComplaints}
        />
      )}

      {/* Profile modal */}
      {showProfile && (
        <ProfileModal
          user={currentUser}
          userToken={userToken}
          onClose={() => setShowProfile(false)}
          onUpdate={updateUser}
        />
      )}
    </>
  );
}