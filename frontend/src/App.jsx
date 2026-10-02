import { useState } from "react";
import { BrowserRouter, Routes, Route, Link, useNavigate } from "react-router-dom";
import Home from "./pages/Home";
import UserDashboard from "./pages/UserDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import AdminLogin from "./pages/AdminLogin";
import SubmitComplaint from "./pages/SubmitComplaint";
import "./App.css";

function AppContent() {
  const [token, setToken] = useState(localStorage.getItem("admin_token") || null);
  const navigate = useNavigate();

  const handleLogin = (newToken) => {
    localStorage.setItem("admin_token", newToken);
    setToken(newToken);
    navigate("/");
  };

  const handleLogout = () => {
    localStorage.removeItem("admin_token");
    setToken(null);
    navigate("/");
  };

  return (
    <div className="app">
      <nav className="navbar">
        <Link to="/" className="brand">GrievanceIQ</Link>
        <div className="nav-links">
          <Link to="/">Home</Link>
          <Link to="/submit">Submit Complaint</Link>
          <Link to="/track">Track Complaint</Link>
          <Link to="/admin">Admin</Link>
          {token && <a href="#" onClick={handleLogout}>Logout</a>}
        </div>
      </nav>

      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/submit" element={<SubmitComplaint />} />
          <Route path="/track" element={<UserDashboard />} />
          <Route
            path="/admin"
            element={token ? <AdminDashboard token={token} /> : <AdminLogin onLogin={handleLogin} />}
          />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App;