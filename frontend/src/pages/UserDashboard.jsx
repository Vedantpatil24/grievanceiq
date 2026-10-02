import { useState } from "react";
import axios from "axios";

function UserDashboard() {
  const [token, setToken] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState("");
  const [feedbackSubmitted, setFeedbackSubmitted] = useState(false);
  const [feedbackError, setFeedbackError] = useState("");

  const handleSearch = async () => {
    setError("");
    setResult(null);
    setFeedbackSubmitted(false);
    setFeedbackError("");
    setRating(0);
    setComment("");

    if (!token.trim()) {
      setError("Please enter a token number.");
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get(`http://127.0.0.1:8000/complaint/${token.trim()}`);
      setResult(response.data);
    } catch (err) {
      if (err.response && err.response.status === 404) {
        setError("No complaint found with that token. Please check and try again.");
      } else {
        setError("Something went wrong. Please try again.");
      }
    }
    setLoading(false);
  };

  const handleSubmitFeedback = async () => {
    setFeedbackError("");
    if (rating < 1 || rating > 5) {
      setFeedbackError("Please select a rating from 1 to 5.");
      return;
    }
    try {
      await axios.post(`http://127.0.0.1:8000/complaint/${result.token}/feedback`, {
        rating,
        comment: comment.trim() || null,
      });
      setFeedbackSubmitted(true);
    } catch (err) {
      if (err.response && err.response.status === 400) {
        setFeedbackError("Feedback has already been submitted for this complaint.");
      } else {
        setFeedbackError("Something went wrong submitting feedback. Please try again.");
      }
    }
  };

  const priorityColor = (priority) => {
    if (priority === "High") return "#dc2626";
    if (priority === "Medium") return "#d97706";
    return "#16a34a";
  };

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1rem", color: "#1a1a1a" }}>Track Your Complaint</h1>

      <div className="card">
        <label style={{ display: "block", marginBottom: "0.5rem", fontWeight: 500 }}>
          Enter your token number
        </label>
        <div style={{ display: "flex", gap: "0.75rem" }}>
          <input
            type="text"
            placeholder="e.g. GRV-2026-00001"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <button onClick={handleSearch} disabled={loading}>
            {loading ? "Searching..." : "Search"}
          </button>
        </div>
      </div>

      {error && (
        <div className="card" style={{ borderColor: "#fecaca", backgroundColor: "#fef2f2", color: "#991b1b" }}>
          {error}
        </div>
      )}

      {result && (
        <div className="card">
          <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem", color: "#1a1a1a" }}>Complaint Details</h2>
          <div style={{ display: "grid", gridTemplateColumns: "140px 1fr", rowGap: "0.75rem" }}>
            <strong>Token</strong>
            <span>{result.token}</span>

            <strong>Department</strong>
            <span>{result.department}</span>

            <strong>Priority</strong>
            <span style={{ color: priorityColor(result.priority), fontWeight: 600 }}>
              {result.priority}
            </span>

            <strong>Status</strong>
            <span style={{ textTransform: "capitalize" }}>{result.status.replace("_", " ")}</span>

            <strong>Submitted</strong>
            <span>{result.created_at}</span>
          </div>
        </div>
      )}

      {result && result.status === "resolved" && !feedbackSubmitted && (
        <div className="card">
          <h2 style={{ fontSize: "1.1rem", marginBottom: "1rem", color: "#1a1a1a" }}>
            How was your experience?
          </h2>

          <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1rem" }}>
            {[1, 2, 3, 4, 5].map((n) => (
              <button
                key={n}
                onClick={() => setRating(n)}
                style={{
                  backgroundColor: rating >= n ? "#f59e0b" : "#e5e7eb",
                  color: rating >= n ? "white" : "#6b7280",
                  width: "2.5rem",
                  height: "2.5rem",
                  borderRadius: "50%",
                  fontSize: "1.1rem",
                }}
              >
                {n}
              </button>
            ))}
          </div>

          <textarea
            placeholder="Any additional comments? (optional)"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            rows={3}
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

          {feedbackError && (
            <p style={{ color: "#991b1b", marginBottom: "1rem" }}>{feedbackError}</p>
          )}

          <button onClick={handleSubmitFeedback}>Submit Feedback</button>
        </div>
      )}

      {feedbackSubmitted && (
        <div className="card" style={{ borderColor: "#bbf7d0", backgroundColor: "#f0fdf4", color: "#166534" }}>
          Thank you for your feedback!
        </div>
      )}
    </div>
  );
}

export default UserDashboard;