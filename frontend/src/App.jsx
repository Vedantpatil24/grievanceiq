import { useState, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./pages/LoginPage";
import UserDashboard from "./pages/UserDashboard";
import AdminDashboard from "./pages/AdminDashboard";
import EmployeeDashboard from "./pages/EmployeeDashboard";
import "./App.css";

function AppContent() {
  const [userToken, setUserToken] = useState(localStorage.getItem("user_token") || null);
  const [currentUser, setCurrentUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem("user_info")) || null; } catch { return null; }
  });

  const [adminToken, setAdminToken] = useState(localStorage.getItem("admin_token") || null);

  const [empToken, setEmpToken] = useState(localStorage.getItem("emp_token") || null);
  const [currentEmp, setCurrentEmp] = useState(() => {
    try { return JSON.parse(localStorage.getItem("emp_info")) || null; } catch { return null; }
  });

  // ── Dark / Light mode ─────────────────────────────
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem("theme") === "dark");

  useEffect(() => {
    const root = document.documentElement;
    if (darkMode) {
      root.setAttribute("data-theme", "dark");
      localStorage.setItem("theme", "dark");
    } else {
      root.removeAttribute("data-theme");
      localStorage.setItem("theme", "light");
    }
  }, [darkMode]);

  const toggleTheme = () => setDarkMode(d => !d);
  // ──────────────────────────────────────────────────

  const handleUserLogin = (token, userInfo) => {
    localStorage.setItem("user_token", token);
    localStorage.setItem("user_info", JSON.stringify(userInfo));
    setUserToken(token); setCurrentUser(userInfo);
  };

  const handleAdminLogin = (token) => {
    localStorage.setItem("admin_token", token);
    setAdminToken(token);
  };

  const handleEmpLogin = (token, empInfo) => {
    localStorage.setItem("emp_token", token);
    localStorage.setItem("emp_info", JSON.stringify(empInfo));
    setEmpToken(token); setCurrentEmp(empInfo);
  };

  const handleUserLogout = () => {
    localStorage.removeItem("user_token"); localStorage.removeItem("user_info");
    setUserToken(null); setCurrentUser(null);
  };
  const handleAdminLogout = () => {
    localStorage.removeItem("admin_token");
    setAdminToken(null);
  };
  const handleEmpLogout = () => {
    localStorage.removeItem("emp_token"); localStorage.removeItem("emp_info");
    setEmpToken(null); setCurrentEmp(null);
  };

  return (
    <div className="app">
      <Routes>
        {/* Root → redirect based on who's logged in */}
        <Route
          path="/"
          element={
            userToken ? <Navigate to="/user" /> :
            adminToken ? <Navigate to="/admin" /> :
            empToken ? <Navigate to="/employee" /> :
            <LoginPage
              onUserLogin={handleUserLogin}
              onAdminLogin={handleAdminLogin}
              onEmpLogin={handleEmpLogin}
              darkMode={darkMode}
              onToggleTheme={toggleTheme}
            />
          }
        />

        {/* User */}
        <Route
          path="/user/*"
          element={
            userToken
              ? <UserDashboard userToken={userToken} user={currentUser} onLogout={handleUserLogout} onUserUpdate={setCurrentUser} darkMode={darkMode} onToggleTheme={toggleTheme} />
              : <Navigate to="/" />
          }
        />

        {/* Admin */}
        <Route
          path="/admin/*"
          element={
            adminToken
              ? <AdminDashboard token={adminToken} onLogout={handleAdminLogout} darkMode={darkMode} onToggleTheme={toggleTheme} />
              : <Navigate to="/" />
          }
        />

        {/* Employee */}
        <Route
          path="/employee/*"
          element={
            empToken
              ? <EmployeeDashboard token={empToken} employee={currentEmp} onLogout={handleEmpLogout} darkMode={darkMode} onToggleTheme={toggleTheme} />
              : <Navigate to="/" />
          }
        />

        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
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