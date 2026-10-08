import { useState } from "react";
import axios from "axios";

const COMPANIES = [
  "State Bank of India",
  "HDFC Bank",
  "ICICI Bank",
  "Axis Bank",
  "Kotak Mahindra Bank",
  "Punjab National Bank",
  "Bank of Baroda",
  "Canara Bank",
  "IndusInd Bank",
  "IDFC FIRST Bank",
  "Federal Bank",
  "Yes Bank",
];

const SERVICE_TYPES = [
  "UPI / Digital Payments",
  "Credit Card",
  "Debit Card / ATM",
  "Personal / Home Loan",
  "Savings / Current Account",
  "Net Banking / Mobile App",
  "KYC / Account Verification",
  "Remittance / Wire Transfer",
  "Fraud / Unauthorized Transaction",
  "Other",
];

function SubmitComplaint({ user, userToken, onSuccess }) {
  const [narrative, setNarrative] = useState("");
  const [company, setCompany] = useState("");
  const [otherCompany, setOtherCompany] = useState("");
  const [transactionDate, setTransactionDate] = useState("");
  const [referenceId, setReferenceId] = useState("");
  const [amount, setAmount] = useState("");
  const [branch, setBranch] = useState("");
  const [serviceType, setServiceType] = useState("");
  const [proofFile, setProofFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setError("");
    setResult(null);

    if (!company) {
      setError("Please select a bank/financial institution.");
      return;
    }
    if (company === "Other" && otherCompany.trim().length === 0) {
      setError("Please enter the institution name.");
      return;
    }
    if (narrative.trim().length < 25) {
      setError("Please describe your complaint in factual detail (at least 25 characters).");
      return;
    }
    if (!proofFile) {
      setError("Supporting proof (screenshot, statement, receipt, or SMS) is mandatory to validate your complaint.");
      return;
    }

    const finalCompany = company === "Other" ? otherCompany.trim() : company;

    const formData = new FormData();
    formData.append("narrative", narrative.trim());
    formData.append("company", finalCompany);
    if (transactionDate) formData.append("transaction_date", transactionDate);
    if (referenceId) formData.append("reference_id", referenceId);
    if (amount) formData.append("amount", amount);
    if (branch) formData.append("branch", branch);
    if (serviceType) formData.append("service_type", serviceType);
    let currentUserId = user?.id;
    if (!currentUserId) {
      try {
        const stored = JSON.parse(localStorage.getItem("user_info") || "{}");
        if (stored?.id) currentUserId = stored.id;
      } catch (e) {}
    }
    if (currentUserId) formData.append("user_id", currentUserId);
    formData.append("proof", proofFile);

    setLoading(true);
    try {
      const headers = { "Content-Type": "multipart/form-data" };
      const token = userToken || localStorage.getItem("user_token");
      if (token) headers["Authorization"] = `Bearer ${token}`;
      const response = await axios.post("http://127.0.0.1:8000/complaint", formData, { headers });
      setResult(response.data);
      setNarrative("");
      setCompany("");
      setOtherCompany("");
      setTransactionDate("");
      setReferenceId("");
      setAmount("");
      setBranch("");
      setServiceType("");
      setProofFile(null);
      if (onSuccess) onSuccess(response.data.token);
    } catch (err) {

      if (err.response && err.response.status === 422) {
        const detail = err.response.data.detail;
        if (typeof detail === "object" && detail.checklist) {
          const missing = Object.entries(detail.checklist)
            .filter(([, passed]) => !passed)
            .map(([key]) => key.replace(/_/g, " "))
            .join(", ");
          setError(
            `${detail.message} (Score: ${detail.validity_score}/100. Failed checks: ${missing || "Factual details required"})`
          );
        } else {
          setError(detail.message || "Complaint rejected by pre-token validity check.");
        }
      } else {
        setError("Something went wrong submitting your complaint. Please try again.");
      }
    }
    setLoading(false);
  };

  const priorityColor = (p) => {
    if (p === "High") return "#dc2626";
    if (p === "Medium") return "#d97706";
    return "#16a34a";
  };

  return (
    <div style={{ maxWidth: "760px", margin: "1.5rem auto" }}>
      <h1 style={{ fontSize: "1.7rem", marginBottom: "0.5rem", color: "#16222E", fontWeight: 700 }}>
        Lodge a Formal Grievance
      </h1>
      <p style={{ color: "#6b655c", marginBottom: "1.5rem", fontSize: "0.95rem" }}>
        Every grievance is rigorously validated, scored, routed to its specialized department, and assigned to a dedicated resolution bot with strict SLA resolution timelines.
      </p>

      {!result && (
        <div className="card" style={{ padding: "1.8rem" }}>
          <div style={{ marginBottom: "1.2rem" }}>
            <label style={{ display: "block", marginBottom: "0.4rem", fontWeight: 600, color: "#16222E" }}>
              Bank / Financial Institution *
            </label>
            <select
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              style={{ width: "100%", padding: "0.6rem", borderRadius: "6px", border: "1px solid #d1d5db" }}
            >
              <option value="">Select your bank</option>
              {COMPANIES.map((name) => (
                <option key={name} value={name}>{name}</option>
              ))}
              <option value="Other">Other Bank / NBFC</option>
            </select>
          </div>

          {company === "Other" && (
            <div style={{ marginBottom: "1.2rem" }}>
              <input
                type="text"
                placeholder="Enter financial institution name"
                value={otherCompany}
                onChange={(e) => setOtherCompany(e.target.value)}
                style={{ width: "100%", padding: "0.6rem", borderRadius: "6px", border: "1px solid #d1d5db" }}
              />
            </div>
          )}

          <div style={{ marginBottom: "1.2rem" }}>
            <label style={{ display: "block", marginBottom: "0.4rem", fontWeight: 600, color: "#16222E" }}>
              Service Category
            </label>
            <select
              value={serviceType}
              onChange={(e) => setServiceType(e.target.value)}
              style={{ width: "100%", padding: "0.6rem", borderRadius: "6px", border: "1px solid #d1d5db" }}
            >
              <option value="">Select service type</option>
              {SERVICE_TYPES.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1.2rem" }}>
            <div>
              <label style={{ display: "block", marginBottom: "0.4rem", fontWeight: 600, color: "#16222E" }}>
                Transaction Date *
              </label>
              <input
                type="date"
                max={new Date().toISOString().split("T")[0]}
                value={transactionDate}
                onChange={(e) => setTransactionDate(e.target.value)}
                style={{ width: "100%", padding: "0.6rem", borderRadius: "6px", border: "1px solid #d1d5db" }}
              />
              <span style={{ fontSize: "0.78rem", color: "#6b655c" }}>Must not be a future date.</span>
            </div>
            <div>
              <label style={{ display: "block", marginBottom: "0.4rem", fontWeight: 600, color: "#16222E" }}>
                Amount Involved (₹) *
              </label>
              <input
                type="number"
                placeholder="e.g. 15000"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                style={{ width: "100%", padding: "0.6rem", borderRadius: "6px", border: "1px solid #d1d5db" }}
              />
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1.2rem" }}>
            <div>
              <label style={{ display: "block", marginBottom: "0.4rem", fontWeight: 600, color: "#16222E" }}>
                Transaction / Reference / UTR ID *
              </label>
              <input
                type="text"
                placeholder="e.g. UPI/2026/091244 or TXN981"
                value={referenceId}
                onChange={(e) => setReferenceId(e.target.value)}
                style={{ width: "100%", padding: "0.6rem", borderRadius: "6px", border: "1px solid #d1d5db" }}
              />
            </div>
            <div>
              <label style={{ display: "block", marginBottom: "0.4rem", fontWeight: 600, color: "#16222E" }}>
                Branch / City
              </label>
              <input
                type="text"
                placeholder="e.g. Bengaluru Main Branch"
                value={branch}
                onChange={(e) => setBranch(e.target.value)}
                style={{ width: "100%", padding: "0.6rem", borderRadius: "6px", border: "1px solid #d1d5db" }}
              />
            </div>
          </div>

          <div style={{ marginBottom: "1.2rem" }}>
            <label style={{ display: "block", marginBottom: "0.4rem", fontWeight: 600, color: "#16222E" }}>
              Factual Grievance Description *
            </label>
            <textarea
              placeholder="Provide a clear, factual account of what happened (e.g. unauthorized debit, debited but not credited, loan foreclosure delay, wrong charge). Avoid only emotional venting; factual banking context is strictly verified by our validity engine."
              value={narrative}
              onChange={(e) => setNarrative(e.target.value)}
              rows={5}
              style={{
                width: "100%",
                padding: "0.7rem",
                borderRadius: "6px",
                border: "1px solid #d1d5db",
                fontFamily: "inherit",
                fontSize: "0.95rem",
              }}
            />
          </div>

          <div style={{ marginBottom: "1.5rem" }}>
            <label style={{ display: "block", marginBottom: "0.4rem", fontWeight: 600, color: "#16222E" }}>
              Mandatory Evidence / Supporting Proof *
            </label>
            <input
              type="file"
              required
              accept="image/*,.pdf,.doc,.docx"
              onChange={(e) => setProofFile(e.target.files[0])}
              style={{ width: "100%", padding: "0.5rem" }}
            />
            <span style={{ fontSize: "0.8rem", color: "#6b655c" }}>
              Bank statement PDF, transaction receipt, UPI debit screenshot, or SMS copy.
            </span>
          </div>

          {error && (
            <div
              style={{
                backgroundColor: "#fef2f2",
                border: "1px solid #fecaca",
                color: "#991b1b",
                padding: "0.8rem 1rem",
                borderRadius: "6px",
                fontSize: "0.9rem",
                marginBottom: "1.2rem",
              }}
            >
              {error}
            </div>
          )}

          <button
            type="button"
            className="btn btn-primary btn-lg"
            onClick={handleSubmit}
            disabled={loading}
            style={{ width: "100%", marginTop: "1rem" }}
          >
            {loading ? "Validating & Submitting..." : "Submit Grievance"}
          </button>
        </div>
      )}

      {result && (
        <div className="card" style={{ borderColor: "#bbf7d0", backgroundColor: "#f0fdf4", padding: "1.8rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "1rem" }}>
            <span style={{ fontSize: "1.4rem" }}>✅</span>
            <h2 style={{ fontSize: "1.25rem", color: "#166534", margin: 0, fontWeight: 700 }}>
              Grievance Accepted & Token Generated!
            </h2>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "180px 1fr", rowGap: "0.85rem", fontSize: "0.95rem" }}>
            <strong>Tracking Token:</strong>
            <span style={{ fontWeight: 800, color: "#16222E", fontSize: "1.1rem" }}>{result.token}</span>

            <strong>Assigned Department:</strong>
            <span style={{ fontWeight: 600 }}>{result.department}</span>

            <strong>Assigned Bot Worker:</strong>
            <span style={{ color: "#1e40af", fontWeight: 600 }}>{result.assigned_worker}</span>

            <strong>Priority Tier:</strong>
            <span style={{ color: priorityColor(result.priority), fontWeight: 700 }}>
              {result.priority} Priority
            </span>

            <strong>Current Stage:</strong>
            <span style={{ fontWeight: 600 }}>{result.stage}</span>

            <strong>SLA Deadline:</strong>
            <span>{new Date(result.due_date).toLocaleString()}</span>

            <strong>Pre-Token Score:</strong>
            <span style={{ color: "#15803d", fontWeight: 600 }}>{result.validity_score} / 100 ({result.decision})</span>

            <strong>SBERT Semantic Match:</strong>
            <span style={{ color: "#1e40af", fontWeight: 600 }}>
              {result.sbert_score ? `${Math.round(result.sbert_score * 100)}% Banking Grievance Alignment` : "Verified"}
            </span>

            <strong>Proof Document Alignment:</strong>
            <span style={{ color: "#166534", fontWeight: 600 }}>
              {result.proof_similarity ? `${Math.round(result.proof_similarity * 100)}% Context Match` : "Verified"}
            </span>
          </div>

          <p style={{ marginTop: "1.2rem", color: "#166534", fontSize: "0.9rem" }}>
            Keep your token safe! You can monitor resolution milestones in real time on your dashboard.
          </p>

          <button onClick={() => setResult(null)} style={{ marginTop: "0.5rem" }}>
            Submit Another Grievance
          </button>
        </div>
      )}
    </div>
  );
}

export default SubmitComplaint;