import { useState } from "react";
import axios from "axios";

function AdminLogin({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setError("");
    if (!email || !password) {
      setError("Please enter both email and password.");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post("http://127.0.0.1:8000/login", { email, password });
      onLogin(response.data.access_token);
    } catch (err) {
      setError("Invalid email or password.");
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: "360px", margin: "3rem auto" }}>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1rem", color: "#1a1a1a", textAlign: "center" }}>
        Admin Login
      </h1>
      <div className="card">
        <label style={{ display: "block", marginBottom: "0.4rem", fontWeight: 500 }}>Email</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="admin@grievanceiq.com"
          style={{ marginBottom: "1rem" }}
        />

        <label style={{ display: "block", marginBottom: "0.4rem", fontWeight: 500 }}>Password</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          placeholder="••••••••"
          style={{ marginBottom: "1rem" }}
        />

        {error && <p style={{ color: "#991b1b", marginBottom: "1rem" }}>{error}</p>}

        <button onClick={handleSubmit} disabled={loading} style={{ width: "100%" }}>
          {loading ? "Logging in..." : "Log In"}
        </button>
      </div>
    </div>
  );
}

export default AdminLogin;