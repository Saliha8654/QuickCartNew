import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./Admin2.css";

function Admin2() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    if (!email || !password) {
      setError("Please fill in all fields");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await axios.post("http://localhost:5000/api/admin/login", {
        email,
        password
      });

      // Save token to localStorage
      localStorage.setItem("adminToken", response.data.token);
      localStorage.setItem("adminData", JSON.stringify(response.data.admin));

      // Navigate to dashboard
      navigate("/admin/dashboard");
    } catch (err) {
      setError(err.response?.data?.error || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin2-container">
      {/* Top Blue Bar */}
      <div className="admin2-top-bar">
        <div className="admin2-menu-icon">
          <div className="menu-line"></div>
          <div className="menu-line"></div>
          <div className="menu-line"></div>
        </div>
      </div>

      {/* Heading */}
      <h2 className="admin2-page-heading">Sign in to Admin Account</h2>

      {/* Login Form */}
      <div className="admin2-form-container">
        <h3 className="admin2-form-heading">Sign in</h3>

        <div className="admin2-form-group">
          <label className="admin2-label">Email:</label>
          <input
            type="email"
            className="admin2-input"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
          />
        </div>

        <div className="admin2-form-group">
          <label className="admin2-label">Password:</label>
          <input
            type="password"
            className="admin2-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter your password"
          />
        </div>

        {error && <p className="admin2-error">{error}</p>}

        <p className="admin2-signup-text">
          Don't have an account?{" "}
          <span 
            className="admin2-link"
            onClick={() => navigate('/admin/signup')}
          >
            Signup
          </span>
        </p>

        <div className="admin2-buttons">
          <button 
            className="admin2-btn admin2-btn-cancel"
            onClick={() => navigate('/admin')}
          >
            Cancel
          </button>
          <button 
            className="admin2-btn admin2-btn-login"
            onClick={handleLogin}
            disabled={loading}
          >
            {loading ? "Logging in..." : "Log-in"}
          </button>
        </div>
      </div>

      {/* Bottom Blue Bar */}
      <div className="admin2-bottom-bar"></div>
    </div>
  );
}

export default Admin2;
