import { useState } from "react";
import axios from "axios";

const API = "http://127.0.0.1:8000";

/* ── Left panel feature bullets ─────────────────────── */
const FEATURES = [
  { icon: "🏦", title: "5 Banking Departments", desc: "Digital/UPI, Loans, Cards, Accounts & Fraud — auto-classified by SVM ML model." },
  { icon: "⚡", title: "Fair Auto-Assignment", desc: "Least-loaded bot officer assignment across 25 dedicated grievance officers." },
  { icon: "🛡️", title: "Regulatory SLA Tracking", desc: "24h High, 7d Medium, 30d Low. Auto-escalation on breach." },
  { icon: "📊", title: "Real-time Analytics", desc: "Company leaderboard, cluster analysis, and department-level insights." },
];

/* ── Unified Login Page ──────────────────────────────── */
export default function LoginPage({ onUserLogin, onAdminLogin, onEmpLogin }) {
  const [tab, setTab] = useState("user"); // "user" | "employee" | "admin"

  return (
    <div className="login-page">
      {/* Left branding panel */}
      <div className="login-left">
        <div>
          <div className="login-brand-name">GrievanceIQ</div>
          <div className="login-brand-tagline">Your banking grievances, resolved with precision.</div>
        </div>

        <div className="login-features">
          {FEATURES.map(f => (
            <div key={f.title} className="lf-item">
              <div className="lf-icon">{f.icon}</div>
              <div className="lf-text">
                <div className="lft-title">{f.title}</div>
                <div className="lft-desc">{f.desc}</div>
              </div>
            </div>
          ))}
        </div>

        <div className="login-footer">
          © 2025 GrievanceIQ · BFSI Grievance Triage Platform
        </div>
      </div>

      {/* Right login card */}
      <div className="login-right">
        <div className="login-box fade-in">
          <h2>Welcome back</h2>
          <p className="lb-sub">Select your portal to sign in</p>

          {/* Tab toggle */}
          <div className="login-tabs">
            <button className={`login-tab-btn ${tab === "user" ? "active" : ""}`} onClick={() => setTab("user")}>
              Customer
            </button>
            <button className={`login-tab-btn ${tab === "employee" ? "active" : ""}`} onClick={() => setTab("employee")}>
              Officer
            </button>
            <button className={`login-tab-btn ${tab === "admin" ? "active" : ""}`} onClick={() => setTab("admin")}>
              Admin
            </button>
          </div>

          {tab === "user"     && <UserLoginForm     onLogin={onUserLogin} />}
          {tab === "employee" && <EmployeeLoginForm  onLogin={onEmpLogin} />}
          {tab === "admin"    && <AdminLoginForm     onLogin={onAdminLogin} />}
        </div>
      </div>
    </div>
  );
}

/* ── CUSTOMER login / register form ─────────────────── */
function UserLoginForm({ onLogin }) {
  const [mode, setMode] = useState("login"); // "login" | "register"
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setError(""); setSuccessMsg(""); setLoading(true);
    try {
      if (mode === "register") {
        await axios.post(`${API}/auth/register`, { name, email, password });
        setSuccessMsg("Account successfully created! Please enter your credentials to sign in.");
        setMode("login");
        setPassword("");
      } else {
        const r = await axios.post(`${API}/auth/user/login`, { email, password });
        onLogin(r.data.access_token, { id: r.data.id, name: r.data.name, email: r.data.email, role: r.data.role });
      }
    } catch (err) {
      setError(err?.response?.data?.detail || "Authentication failed. Please check your credentials.");
    }
    setLoading(false);
  };

  return (
    <form onSubmit={submit}>
      {mode === "register" && (
        <div className="form-group">
          <label className="form-label">Full Name <span className="required">*</span></label>
          <input className="form-input" type="text" placeholder="e.g. Ramesh Kumar" value={name}
            onChange={e => setName(e.target.value)} required />
        </div>
      )}

      <div className="form-group">
        <label className="form-label">Email Address <span className="required">*</span></label>
        <input className="form-input" type="email" placeholder="ramesh@example.com" value={email}
          onChange={e => setEmail(e.target.value)} required />
      </div>

      <div className="form-group">
        <label className="form-label">Password <span className="required">*</span></label>
        <input className="form-input" type="password" placeholder="••••••••" value={password}
          onChange={e => setPassword(e.target.value)} required />
      </div>

      {successMsg && <div className="alert alert-success mb-2">{successMsg}</div>}
      {error && <div className="alert alert-error mb-2">{error}</div>}

      <button type="submit" className="btn btn-primary btn-lg btn-full" disabled={loading}>
        {loading ? "Please wait…" : mode === "register" ? "Create Account" : "Sign In"}
      </button>

      <div style={{ textAlign: "center", marginTop: "1.1rem", fontSize: "0.85rem", color: "var(--text-muted)" }}>
        {mode === "login" ? (
          <>No account? <button type="button" style={{ background: "none", border: "none", color: "var(--blue)", fontWeight: 700, cursor: "pointer" }} onClick={() => { setMode("register"); setError(""); }}>Register here</button></>
        ) : (
          <>Already registered? <button type="button" style={{ background: "none", border: "none", color: "var(--blue)", fontWeight: 700, cursor: "pointer" }} onClick={() => { setMode("login"); setError(""); }}>Sign in</button></>
        )}
      </div>
    </form>
  );
}

/* ── EMPLOYEE login (Employee ID + Password → OTP) ──── */
function EmployeeLoginForm({ onLogin }) {
  const [step, setStep] = useState(1); // 1 = credentials, 2 = OTP
  const [empId, setEmpId] = useState("");
  const [password, setPassword] = useState("");
  const [otp, setOtp] = useState("");
  const [demoOtp, setDemoOtp] = useState(""); // shown in dev mode
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submitStep1 = async (e) => {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      const r = await axios.post(`${API}/auth/employee/login-step1`, { employee_id: empId, password });
      setDemoOtp(r.data.demo_otp || "");
      setStep(2);
    } catch (err) {
      setError(err?.response?.data?.detail || "Invalid Employee ID or password.");
    }
    setLoading(false);
  };

  const submitOtp = async (e) => {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      const r = await axios.post(`${API}/auth/employee/verify-otp`, { employee_id: empId, otp_code: otp });
      const emp = r.data.employee || {};
      onLogin(r.data.access_token, {
        worker_id: emp.worker_id || r.data.worker_id,
        employee_id: emp.employee_id || r.data.employee_id,
        name: emp.name || r.data.name,
        department: emp.department || r.data.department,
        email: emp.email || r.data.email,
        phone: emp.phone,
      });
    } catch (err) {
      setError(err?.response?.data?.detail || "Invalid or expired OTP.");
    }
    setLoading(false);
  };

  if (step === 1) {
    return (
      <form onSubmit={submitStep1}>
        <div className="form-group">
          <label className="form-label">Employee ID <span className="required">*</span></label>
          <input className="form-input" type="text" placeholder="e.g. EMP-DIG-101" value={empId}
            onChange={e => setEmpId(e.target.value)} required />
        </div>
        <div className="form-group">
          <label className="form-label">Password <span className="required">*</span></label>
          <input className="form-input" type="password" placeholder="••••••••" value={password}
            onChange={e => setPassword(e.target.value)} required />
        </div>
        {error && <div className="alert alert-error mb-2">{error}</div>}
        <button type="submit" className="btn btn-primary btn-lg btn-full" disabled={loading}>
          {loading ? "Verifying…" : "Continue →"}
        </button>
        <p className="form-hint" style={{ textAlign: "center", marginTop: "0.75rem" }}>
          Default password for all officers: <code>emp123</code>
        </p>
      </form>
    );
  }

  return (
    <form onSubmit={submitOtp}>
      <div className="alert alert-info mb-2">
        📱 OTP sent to your registered mobile number.
      </div>
      {demoOtp && (
        <div className="alert alert-warn mb-2">
          <strong>Demo OTP:</strong> {demoOtp}
        </div>
      )}
      <div className="form-group">
        <label className="form-label">Enter OTP <span className="required">*</span></label>
        <input className="form-input" type="text" maxLength={6} placeholder="6-digit code" value={otp}
          onChange={e => setOtp(e.target.value)} style={{ letterSpacing: "0.2em", fontSize: "1.1rem" }} required />
      </div>
      {error && <div className="alert alert-error mb-2">{error}</div>}
      <button type="submit" className="btn btn-primary btn-lg btn-full" disabled={loading}>
        {loading ? "Verifying…" : "Verify & Sign In"}
      </button>
      <button type="button" className="btn btn-ghost btn-full mt-1" onClick={() => { setStep(1); setError(""); }}>
        ← Back
      </button>
    </form>
  );
}

/* ── ADMIN login form ───────────────────────────────── */
function AdminLoginForm({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setError(""); setLoading(true);
    try {
      const r = await axios.post(`${API}/auth/admin/login`, { email, password });
      onLogin(r.data.access_token);
    } catch (err) {
      setError(err?.response?.data?.detail || "Invalid admin credentials.");
    }
    setLoading(false);
  };

  return (
    <form onSubmit={submit}>
      <div className="alert alert-info mb-2">
        🛡️ Restricted access. Admin credentials required.
      </div>
      <div className="form-group">
        <label className="form-label">Admin Email <span className="required">*</span></label>
        <input className="form-input" type="email" placeholder="admin@grievanceiq.in" value={email}
          onChange={e => setEmail(e.target.value)} required />
      </div>
      <div className="form-group">
        <label className="form-label">Password <span className="required">*</span></label>
        <input className="form-input" type="password" placeholder="••••••••" value={password}
          onChange={e => setPassword(e.target.value)} required />
      </div>
      {error && <div className="alert alert-error mb-2">{error}</div>}
      <button type="submit" className="btn btn-primary btn-lg btn-full" disabled={loading}>
        {loading ? "Authenticating…" : "Sign In to Admin Panel"}
      </button>
    </form>
  );
}
