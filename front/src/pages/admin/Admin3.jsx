import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./Admin3.css";

function Admin3() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSignup = async () => {
    if (!email || !username || !password) {
      setError("Please fill in all fields");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await axios.post("http://localhost:5000/api/admin/signup", {
        email,
        username,
        password
      });

      // Save token to localStorage
      localStorage.setItem("adminToken", response.data.token);
      localStorage.setItem("adminData", JSON.stringify(response.data.admin));

      // Navigate to dashboard
      navigate("/admin/dashboard");
    } catch (err) {
      setError(err.response?.data?.error || "Signup failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin3-container">
      {/* Signup Form */}
      <div className="admin3-form-container">
        <h3 className="admin3-form-heading">Create Admin Account</h3>

        <div className="admin3-form-group">
          <label className="admin3-label">Email:</label>
          <input
            type="email"
            className="admin3-input"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Enter your email"
          />
        </div>

        <div className="admin3-form-group">
          <label className="admin3-label">Username:</label>
          <input
            type="text"
            className="admin3-input"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Choose a username"
          />
        </div>

        <div className="admin3-form-group">
          <label className="admin3-label">Password:</label>
          <input
            type="password"
            className="admin3-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Create a password"
          />
        </div>

        {error && <p className="admin3-error">{error}</p>}

        <p className="admin3-login-text">
          Already have an account?{" "}
          <span 
            className="admin3-link"
            onClick={() => navigate('/admin/login')}
          >
            Log in here
          </span>
        </p>

        <div className="admin3-buttons">
          <button 
            className="admin3-btn admin3-btn-cancel"
            onClick={() => navigate('/admin')}
          >
            Cancel
          </button>
          <button 
            className="admin3-btn admin3-btn-signup"
            onClick={handleSignup}
            disabled={loading}
          >
            {loading ? "Signing up..." : "Sign Up"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Admin3;
