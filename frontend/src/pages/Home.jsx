import { Link } from "react-router-dom";

const TagIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F7F3EC" strokeWidth="1.8">
    <path d="M20.59 13.41L13.41 20.59a2 2 0 01-2.83 0L2 12.5V4a2 2 0 012-2h8.5l8.09 8.09a2 2 0 010 2.83z" strokeLinecap="round" strokeLinejoin="round"/>
    <circle cx="7" cy="7" r="1.3" fill="#F7F3EC" stroke="none"/>
  </svg>
);

const BoltIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F7F3EC" strokeWidth="1.8">
    <path d="M13 2L4.5 14h6.2l-1.2 8L19.5 10h-6.2L13 2z" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const ShieldIcon = () => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#F7F3EC" strokeWidth="1.8">
    <path d="M12 2l8 3v6c0 5-3.4 8.7-8 11-4.6-2.3-8-6-8-11V5l8-3z" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M9 12l2 2 4-4" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

function Home({ userToken, adminToken }) {
  return (
    <div>
      <div className="hero-section">
        <div style={{ textAlign: "center" }}>
          <div style={{
            display: "inline-block",
            fontSize: "0.78rem",
            fontWeight: 600,
            color: "#B5793A",
            letterSpacing: "0.06em",
            textTransform: "uppercase",
            marginBottom: "0.9rem",
          }}>
            Automated BFSI Grievance Triage & Resolution
          </div>
          <h1 style={{ fontSize: "2.6rem", fontWeight: 800, color: "#16222E", marginBottom: "1rem", letterSpacing: "-0.02em", lineHeight: 1.2 }}>
            Every banking complaint, triaged with machine precision.
          </h1>
          <p style={{ fontSize: "1.08rem", color: "#5c564e", maxWidth: "600px", margin: "0 auto 2rem", lineHeight: 1.6 }}>
            Powered by high-accuracy SVM classification across Indian banking departments, 
            fair bot-worker load distribution, and automated regulatory SLA tracking.
          </p>

          {/* TWO DEDICATED LOGIN PORTALS */}
          <div style={{ display: "flex", gap: "1.2rem", justifyContent: "center", flexWrap: "wrap", marginBottom: "1.5rem" }}>
            <div style={{
              backgroundColor: "#ffffff",
              padding: "1.4rem 1.6rem",
              borderRadius: "10px",
              border: "1px solid #d1d5db",
              boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
              minWidth: "260px",
              textAlign: "left"
            }}>
              <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#166534", textTransform: "uppercase", marginBottom: "0.3rem" }}>
                Customer Portal
              </div>
              <h3 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#16222E", marginBottom: "0.4rem" }}>
                User Access
              </h3>
              <p style={{ fontSize: "0.85rem", color: "#6b655c", marginBottom: "1rem" }}>
                Lodge new grievances, check resolution stages, and see full past history.
              </p>
              {userToken ? (
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <Link to="/submit"><button style={{ padding: "0.55rem 1rem", fontSize: "0.85rem" }}>Submit Grievance</button></Link>
                  <Link to="/user/dashboard"><button style={{ padding: "0.55rem 1rem", fontSize: "0.85rem", backgroundColor: "#f3f4f6", color: "#1f2937", border: "1px solid #d1d5db" }}>My Dashboard</button></Link>
                </div>
              ) : (
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <Link to="/user/login">
                    <button style={{ padding: "0.6rem 1.2rem", fontSize: "0.9rem", width: "100%" }}>
                      User Sign In / Register
                    </button>
                  </Link>
                </div>
              )}
            </div>

            <div style={{
              backgroundColor: "#ffffff",
              padding: "1.4rem 1.6rem",
              borderRadius: "10px",
              border: "1px solid #d1d5db",
              boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
              minWidth: "260px",
              textAlign: "left"
            }}>
              <div style={{ fontSize: "0.8rem", fontWeight: 700, color: "#B5793A", textTransform: "uppercase", marginBottom: "0.3rem" }}>
                Operations & Governance
              </div>
              <h3 style={{ fontSize: "1.15rem", fontWeight: 700, color: "#16222E", marginBottom: "0.4rem" }}>
                Admin & Officer Login
              </h3>
              <p style={{ fontSize: "0.85rem", color: "#6b655c", marginBottom: "1rem" }}>
                Monitor 25 bot workers, SLA breaches, triage queue, and bank rankings.
              </p>
              <Link to="/admin">
                <button
                  style={{
                    padding: "0.75rem 1.4rem",
                    fontSize: "0.95rem",
                    width: "100%",
                    backgroundColor: "#16222E",
                    color: "#FFFFFF",
                    border: "1.5px solid #16222E",
                    fontWeight: 700,
                    cursor: "pointer"
                  }}
                >
                  {adminToken ? "Open Admin Dashboard" : "Admin Sign In"}
                </button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: "flex", gap: "1.1rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
        <div className="feature-card" style={{ flex: 1, minWidth: "220px" }}>
          <div className="icon-badge"><TagIcon /></div>
          <h3 style={{ fontSize: "1.05rem", marginBottom: "0.4rem", color: "#16222E", fontWeight: 700 }}>
            5 Core Banking Departments
          </h3>
          <p style={{ color: "#6b655c", fontSize: "0.9rem", lineHeight: 1.5 }}>
            Trained on 20,000 Indian banking complaints with high precision across Digital/UPI, Loans, Cards, Accounts, and Fraud.
          </p>
        </div>

        <div className="feature-card" style={{ flex: 1, minWidth: "220px" }}>
          <div className="icon-badge"><BoltIcon /></div>
          <h3 style={{ fontSize: "1.05rem", marginBottom: "0.4rem", color: "#16222E", fontWeight: 700 }}>
            Fair Bot Auto-Assignment
          </h3>
          <p style={{ color: "#6b655c", fontSize: "0.9rem", lineHeight: 1.5 }}>
            Every validated grievance is automatically routed to one of 5 dedicated bots per department with least-loaded balancing.
          </p>
        </div>

        <div className="feature-card" style={{ flex: 1, minWidth: "220px" }}>
          <div className="icon-badge"><ShieldIcon /></div>
          <h3 style={{ fontSize: "1.05rem", marginBottom: "0.4rem", color: "#16222E", fontWeight: 700 }}>
            Strict Regulatory SLAs
          </h3>
          <p style={{ color: "#6b655c", fontSize: "0.9rem", lineHeight: 1.5 }}>
            24h for High, 7d for Medium, 30d for Low urgency. Automatic escalation and higher authority reporting upon breach.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Home;