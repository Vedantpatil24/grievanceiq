import { useState } from "react";
import axios from "axios";

function UserAuth({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    setError("");

    if (!email || !password || (isRegister && !name)) {
      setError("Please fill in all required fields.");
      return;
    }

    setLoading(true);
    try {
      if (isRegister) {
        const res = await axios.post("http://127.0.0.1:8000/auth/register", {
          name,
          email,
          password,
        });
        onLogin(res.data.access_token, res.data.user);
      } else {
        const res = await axios.post("http://127.0.0.1:8000/auth/user/login", {
          email,
          password,
        });
        onLogin(res.data.access_token, {
          id: res.data.id,
          name: res.data.name,
          email: res.data.email,
          role: res.data.role,
        });
      }
    } catch (err) {
      if (err.response && err.response.data && err.response.data.detail) {
        setError(typeof err.response.data.detail === "string" ? err.response.data.detail : "Authentication failed.");
      } else {
        setError("Invalid email or password.");
      }
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: "400px", margin: "2.5rem auto" }}>
      <div style={{ textAlign: "center", marginBottom: "1.5rem" }}>
        <h1 style={{ fontSize: "1.6rem", color: "#16222E", fontWeight: 700 }}>
          {isRegister ? "Create Customer Account" : "Customer Login"}
        </h1>
        <p style={{ color: "#6b655c", fontSize: "0.9rem", marginTop: "0.4rem" }}>
          {isRegister
            ? "Register to lodge grievances and view past resolutions."
            : "Sign in to track your grievances, SLA timers, and submit issues."}
        </p>
      </div>

      <div className="card" style={{ padding: "1.8rem" }}>
        <form onSubmit={handleSubmit}>
          {isRegister && (
            <div style={{ marginBottom: "1rem" }}>
              <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: 600, fontSize: "0.9rem" }}>
                Full Name
              </label>
              <input
                type="text"
                placeholder="e.g. Ramesh Kumar"
                value={name}
                onChange={(e) => setName(e.target.value)}
                style={{ width: "100%" }}
                required
              />
            </div>
          )}

          <div style={{ marginBottom: "1rem" }}>
            <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: 600, fontSize: "0.9rem" }}>
              Email Address
            </label>
            <input
              type="email"
              placeholder="ramesh@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              style={{ width: "100%" }}
              required
            />
          </div>

          <div style={{ marginBottom: "1.2rem" }}>
            <label style={{ display: "block", marginBottom: "0.3rem", fontWeight: 600, fontSize: "0.9rem" }}>
              Password
            </label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ width: "100%" }}
              required
            />
          </div>

          {error && (
            <div
              style={{
                backgroundColor: "#fef2f2",
                border: "1px solid #fecaca",
                color: "#991b1b",
                padding: "0.6rem 0.8rem",
                borderRadius: "6px",
                fontSize: "0.85rem",
                marginBottom: "1rem",
              }}
            >
              {error}
            </div>
          )}

          <button type="submit" disabled={loading} style={{ width: "100%", padding: "0.75rem", fontSize: "0.95rem" }}>
            {loading ? "Processing..." : isRegister ? "Register Account" : "Sign In to Portal"}
          </button>
        </form>

        <div style={{ textAlign: "center", marginTop: "1.2rem", paddingTop: "1rem", borderTop: "1px solid #e5e0d8", fontSize: "0.88rem" }}>
          {isRegister ? (
            <span>
              Already registered?{" "}
              <button
                type="button"
                onClick={() => { setIsRegister(false); setError(""); }}
                style={{ background: "none", border: "none", color: "#16222E", fontWeight: 700, cursor: "pointer", textDecoration: "underline", padding: 0 }}
              >
                Sign in here
              </button>
            </span>
          ) : (
            <span>
              Don't have an account yet?{" "}
              <button
                type="button"
                onClick={() => { setIsRegister(true); setError(""); }}
                style={{ background: "none", border: "none", color: "#16222E", fontWeight: 700, cursor: "pointer", textDecoration: "underline", padding: 0 }}
              >
                Create an account
              </button>
            </span>
          )}
        </div>
      </div>
    </div>
  );
}

export default UserAuth;
