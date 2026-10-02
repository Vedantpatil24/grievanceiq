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

function Home() {
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
            Complaint Intelligence for BFSI
          </div>
          <h1 style={{ fontSize: "2.5rem", fontWeight: 800, color: "#16222E", marginBottom: "1rem", letterSpacing: "-0.02em", lineHeight: 1.2 }}>
            Every complaint, routed with precision.
          </h1>
          <p style={{ fontSize: "1.08rem", color: "#5c564e", maxWidth: "520px", margin: "0 auto 1.8rem", lineHeight: 1.6 }}>
            GrievanceIQ classifies, prioritizes, and tracks every complaint automatically —
            giving your customers clarity and your team control.
          </p>
        <div style={{ display: "flex", gap: "0.85rem", justifyContent: "center", flexWrap: "wrap" }}>
  <Link to="/submit">
    <button style={{ padding: "0.85rem 1.8rem", fontSize: "1rem" }}>
      Submit a Complaint
    </button>
  </Link>
  <Link to="/track">
    <button style={{ padding: "0.85rem 1.8rem", fontSize: "1rem" }}>
      Track Your Complaint
    </button>
  </Link>
</div>
        </div>
      </div>

      <div style={{ display: "flex", gap: "1.1rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
        <div className="feature-card" style={{ flex: 1, minWidth: "220px" }}>
          <div className="icon-badge"><TagIcon /></div>
          <h3 style={{ fontSize: "1.05rem", marginBottom: "0.4rem", color: "#16222E", fontWeight: 700 }}>
            Smart Categorization
          </h3>
          <p style={{ color: "#6b655c", fontSize: "0.9rem", lineHeight: 1.5 }}>
            Every complaint is automatically sorted into the right department — no manual triage needed.
          </p>
        </div>

        <div className="feature-card" style={{ flex: 1, minWidth: "220px" }}>
          <div className="icon-badge"><BoltIcon /></div>
          <h3 style={{ fontSize: "1.05rem", marginBottom: "0.4rem", color: "#16222E", fontWeight: 700 }}>
            Priority Routing
          </h3>
          <p style={{ color: "#6b655c", fontSize: "0.9rem", lineHeight: 1.5 }}>
            Urgent issues are flagged instantly, so the most critical complaints get seen first.
          </p>
        </div>

        <div className="feature-card" style={{ flex: 1, minWidth: "220px" }}>
          <div className="icon-badge"><ShieldIcon /></div>
          <h3 style={{ fontSize: "1.05rem", marginBottom: "0.4rem", color: "#16222E", fontWeight: 700 }}>
            Full Transparency
          </h3>
          <p style={{ color: "#6b655c", fontSize: "0.9rem", lineHeight: 1.5 }}>
            Use your tracking token anytime to see your complaint's status, department, and priority.
          </p>
        </div>
      </div>

      <div className="card card-accent">
        <h2 style={{ fontSize: "1.25rem", marginBottom: "1.2rem", color: "#16222E", fontWeight: 700 }}>
          How it works
        </h2>
        <div style={{ display: "flex", gap: "1.5rem", flexWrap: "wrap" }}>
          {[
            ["1", "Submit your complaint"],
            ["2", "Receive a tracking token"],
            ["3", "We classify and prioritize it"],
            ["4", "Track progress anytime"],
          ].map(([num, text]) => (
            <div key={num} style={{ flex: 1, minWidth: "140px", display: "flex", gap: "0.75rem", alignItems: "flex-start" }}>
              <div
                style={{
                  width: "28px",
                  height: "28px",
                  borderRadius: "50%",
                  backgroundColor: "#16222E",
                  color: "#F7F3EC",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  fontWeight: 700,
                  fontSize: "0.85rem",
                  flexShrink: 0,
                }}
              >
                {num}
              </div>
              <p style={{ color: "#5c564e", fontSize: "0.9rem", paddingTop: "0.3rem" }}>{text}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default Home;