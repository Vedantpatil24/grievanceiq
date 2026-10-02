import { useState } from "react";
import axios from "axios";

function SubmitComplaint() {
  const [narrative, setNarrative] = useState("");
  const [company, setCompany] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setError("");
    setResult(null);

    if (narrative.trim().length < 20) {
      setError("Please describe your complaint in a bit more detail (at least 20 characters).");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.post("http://127.0.0.1:8000/complaint", {
        narrative: narrative.trim(),
        company: company.trim() || null,
      });
      setResult(response.data);
      setNarrative("");
      setCompany("");
    } catch (err) {
      setError("Something went wrong submitting your complaint. Please try again.");
    }
    setLoading(false);
  };

  const priorityColor = (p) => {
    if (p === "High") return "#dc2626";
    if (p === "Medium") return "#d97706";
    return "#16a34a";
  };

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "0.5rem", color: "#1a1a1a" }}>Submit a Complaint</h1>
      <p style={{ color: "#666", marginBottom: "1.5rem" }}>
        Describe your issue below. We'll automatically route it to the right department and give you
        a tracking token.
      </p>

      {!result && (
        <div className="card">
          <label style={{ display: "block", marginBottom: "0.4rem", fontWeight: 500 }}>
            Company (optional)
          </label>
          <input
            type="text"
            placeholder="e.g. ABC Bank"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            style={{ marginBottom: "1rem" }}
          />

          <label style={{ display: "block", marginBottom: "0.4rem", fontWeight: 500 }}>
            Describe your complaint
          </label>
          <textarea
            placeholder="Explain what happened, when it occurred, and any relevant details..."
            value={narrative}
            onChange={(e) => setNarrative(e.target.value)}
            rows={6}
            style={{
              width: "100%",
              padding: "0.6rem",
              borderRadius: "6px",
              border: "1px solid #d1d5db",
              fontFamily: "inherit",
              fontSize: "0.95rem",
              marginBottom: "1rem",
            }}
          />

          {error && (
            <p style={{ color: "#991b1b", marginBottom: "1rem" }}>{error}</p>
          )}

          <button onClick={handleSubmit} disabled={loading}>
            {loading ? "Submitting..." : "Submit Complaint"}
          </button>
        </div>
      )}

      {result && (
        <div className="card" style={{ borderColor: "#bbf7d0", backgroundColor: "#f0fdf4" }}>
          <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem", color: "#166534" }}>
            Complaint submitted successfully!
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "140px 1fr", rowGap: "0.75rem" }}>
            <strong>Your Token</strong>
            <span style={{ fontWeight: 700 }}>{result.token}</span>

            <strong>Department</strong>
            <span>{result.department}</span>

            <strong>Priority</strong>
            <span style={{ color: priorityColor(result.priority), fontWeight: 600 }}>
              {result.priority}
            </span>

            <strong>Status</strong>
            <span style={{ textTransform: "capitalize" }}>{result.status}</span>
          </div>
          <p style={{ marginTop: "1rem", color: "#166534", fontSize: "0.9rem" }}>
            Save this token — you'll need it to track your complaint's progress.
          </p>
          <button onClick={() => setResult(null)} style={{ marginTop: "1rem" }}>
            Submit Another Complaint
          </button>
        </div>
      )}
    </div>
  );
}

export default SubmitComplaint;