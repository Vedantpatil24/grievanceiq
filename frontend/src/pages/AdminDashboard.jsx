import { useState, useEffect } from "react";
import axios from "axios";
import {
  PieChart, Pie, Cell, Tooltip, Legend,
  BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer
} from "recharts";

function AdminDashboard({ token }) {
  const [complaints, setComplaints] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [department, setDepartment] = useState("");
  const [priority, setPriority] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const [updatingToken, setUpdatingToken] = useState(null);
  const [stats, setStats] = useState(null);

  const pageSize = 100;
  const totalPages = Math.ceil(total / pageSize);

  const authHeader = { headers: { Authorization: `Bearer ${token}` } };

  const fetchComplaints = async () => {
    setLoading(true);
    try {
      const params = { skip: (page - 1) * pageSize, limit: pageSize };
      if (department) params.department = department;
      if (priority) params.priority = priority;
      if (status) params.status = status;

      const response = await axios.get("http://127.0.0.1:8000/admin/complaints", {
        params,
        ...authHeader,
      });
      setComplaints(response.data.complaints);
      setTotal(response.data.total);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/admin/stats", authHeader);
      setStats(response.data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchComplaints();
  }, [page, department, priority, status]);

  useEffect(() => {
    fetchStats();
  }, []);

  const handleFilterChange = (setter) => (e) => {
    setter(e.target.value);
    setPage(1);
  };

  const handleStatusChange = async (tok, newStatus) => {
    setUpdatingToken(tok);
    try {
      await axios.patch(
        `http://127.0.0.1:8000/admin/complaint/${tok}/status`,
        { status: newStatus },
        authHeader
      );
      setComplaints((prev) => prev.map((c) => (c.token === tok ? { ...c, status: newStatus } : c)));
      fetchStats();
    } catch (err) {
      console.error(err);
      alert("Failed to update status. Please try again.");
    }
    setUpdatingToken(null);
  };

  const priorityColor = (p) => {
    if (p === "High") return "#dc2626";
    if (p === "Medium") return "#d97706";
    return "#16a34a";
  };

  const pieColors = { High: "#dc2626", Medium: "#d97706", Low: "#16a34a" };

  const pieData = stats
    ? Object.entries(stats.priority_counts).map(([name, value]) => ({ name, value }))
    : [];

  const barData = stats
    ? stats.department_breakdown.map((d) => ({
        name: d.department.length > 15 ? d.department.slice(0, 15) + "…" : d.department,
        Open: d.open,
        "In Progress": d.in_progress,
        Resolved: d.resolved,
      }))
    : [];

  return (
    <div>
      <h1 style={{ fontSize: "1.5rem", marginBottom: "1rem", color: "#1a1a1a" }}>Admin Dashboard</h1>

      {stats && (
        <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem", flexWrap: "wrap" }}>
          <div className="card" style={{ flex: 1, minWidth: "150px", textAlign: "center" }}>
            <div style={{ fontSize: "1.6rem", fontWeight: 700 }}>{stats.total}</div>
            <div style={{ color: "#6b7280", fontSize: "0.9rem" }}>Total Complaints</div>
          </div>
          <div className="card" style={{ flex: 1, minWidth: "150px", textAlign: "center" }}>
            <div style={{ fontSize: "1.6rem", fontWeight: 700, color: "#6b7280" }}>{stats.status_counts.open}</div>
            <div style={{ color: "#6b7280", fontSize: "0.9rem" }}>Open</div>
          </div>
          <div className="card" style={{ flex: 1, minWidth: "150px", textAlign: "center" }}>
            <div style={{ fontSize: "1.6rem", fontWeight: 700, color: "#2563eb" }}>{stats.status_counts.in_progress}</div>
            <div style={{ color: "#6b7280", fontSize: "0.9rem" }}>In Progress</div>
          </div>
          <div className="card" style={{ flex: 1, minWidth: "150px", textAlign: "center" }}>
            <div style={{ fontSize: "1.6rem", fontWeight: 700, color: "#16a34a" }}>{stats.status_counts.resolved}</div>
            <div style={{ color: "#6b7280", fontSize: "0.9rem" }}>Resolved</div>
          </div>
          <div className="card" style={{ flex: 1, minWidth: "150px", textAlign: "center" }}>
            <div style={{ fontSize: "1.6rem", fontWeight: 700, color: "#f59e0b" }}>
              {stats.avg_rating !== null ? `${stats.avg_rating} ★` : "—"}
            </div>
            <div style={{ color: "#6b7280", fontSize: "0.9rem" }}>
              Avg Rating ({stats.feedback_count} review{stats.feedback_count !== 1 ? "s" : ""})
            </div>
          </div>
        </div>
      )}

      {stats && (
        <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem", flexWrap: "wrap" }}>
          <div className="card" style={{ flex: 1, minWidth: "320px" }}>
            <h3 style={{ marginBottom: "1rem", fontSize: "1rem", color: "#1a1a1a" }}>Priority Breakdown</h3>
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                  {pieData.map((entry, index) => (
                    <Cell key={index} fill={pieColors[entry.name]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="card" style={{ flex: 2, minWidth: "400px" }}>
            <h3 style={{ marginBottom: "1rem", fontSize: "1rem", color: "#1a1a1a" }}>Status by Category</h3>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={barData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="Open" stackId="a" fill="#9ca3af" />
                <Bar dataKey="In Progress" stackId="a" fill="#2563eb" />
                <Bar dataKey="Resolved" stackId="a" fill="#16a34a" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      <div className="card">
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
          <div style={{ flex: 1, minWidth: "180px" }}>
            <label style={{ display: "block", marginBottom: "0.3rem", fontSize: "0.9rem" }}>Category</label>
            <select value={department} onChange={handleFilterChange(setDepartment)}>
              <option value="">All Categories</option>
              <option value="Credit Reporting">Credit Reporting</option>
              <option value="Debt Collection">Debt Collection</option>
              <option value="Loans">Loans</option>
              <option value="Bank Accounts and Services">Bank Accounts and Services</option>
              <option value="Credit Card Services">Credit Card Services</option>
            </select>
          </div>

          <div style={{ flex: 1, minWidth: "180px" }}>
            <label style={{ display: "block", marginBottom: "0.3rem", fontSize: "0.9rem" }}>Priority</label>
            <select value={priority} onChange={handleFilterChange(setPriority)}>
              <option value="">All Priorities</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>

          <div style={{ flex: 1, minWidth: "180px" }}>
            <label style={{ display: "block", marginBottom: "0.3rem", fontSize: "0.9rem" }}>Status</label>
            <select value={status} onChange={handleFilterChange(setStatus)}>
              <option value="">All Statuses</option>
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
            </select>
          </div>
        </div>
      </div>

      <div className="card">
        <strong>{total}</strong> complaints match current filters
      </div>

      <div className="card" style={{ padding: 0, overflow: "hidden" }}>
        {loading ? (
          <p style={{ padding: "1rem" }}>Loading...</p>
        ) : (
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ backgroundColor: "#f3f4f6", textAlign: "left" }}>
                <th style={{ padding: "0.75rem" }}>Token</th>
                <th style={{ padding: "0.75rem" }}>Department</th>
                <th style={{ padding: "0.75rem" }}>Priority</th>
                <th style={{ padding: "0.75rem" }}>Status</th>
                <th style={{ padding: "0.75rem" }}>Created</th>
              </tr>
            </thead>
            <tbody>
              {complaints.map((c) => (
                <tr key={c.token} style={{ borderTop: "1px solid #e5e7eb" }}>
                  <td style={{ padding: "0.75rem" }}>{c.token}</td>
                  <td style={{ padding: "0.75rem" }}>{c.department}</td>
                  <td style={{ padding: "0.75rem", color: priorityColor(c.priority), fontWeight: 600 }}>
                    {c.priority}
                  </td>
                  <td style={{ padding: "0.75rem" }}>
                    <select
                      value={c.status}
                      disabled={updatingToken === c.token}
                      onChange={(e) => handleStatusChange(c.token, e.target.value)}
                      style={{ padding: "0.3rem", fontSize: "0.9rem", width: "auto" }}
                    >
                      <option value="open">Open</option>
                      <option value="in_progress">In Progress</option>
                      <option value="resolved">Resolved</option>
                    </select>
                  </td>
                  <td style={{ padding: "0.75rem" }}>{c.created_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "1rem" }}>
        <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>
          Previous
        </button>
        <span>Page {page} of {totalPages || 1}</span>
        <button onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}>
          Next
        </button>
      </div>
    </div>
  );
}

export default AdminDashboard;