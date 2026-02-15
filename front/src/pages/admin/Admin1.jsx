import React from "react";
import { useNavigate } from "react-router-dom";
import "./Admin1.css";

function Admin1() {
  const navigate = useNavigate();

  return (
    <div className="admin1-container">
      {/* Top Blue Bar */}
      <div className="admin1-top-bar">
        <div className="admin1-menu-icon" onClick={() => navigate('/admin/dashboard')}>
          <div className="menu-line"></div>
          <div className="menu-line"></div>
          <div className="menu-line"></div>
        </div>
      </div>

      {/* Logo */}
      <div className="admin1-logo">
        <h1 className="logo-text">QUICK</h1>
        <h1 className="logo-text-cart">CART</h1>
      </div>

      {/* Heading */}
      <h2 className="admin1-heading">Admin Dashboard</h2>

      {/* Buttons */}
      <div className="admin1-buttons">
        <button 
          className="admin1-btn"
          onClick={() => navigate('/admin/login')}
        >
          Log-in
        </button>
        <button 
          className="admin1-btn"
          onClick={() => navigate('/admin/signup')}
        >
          Sign-up
        </button>
      </div>

      {/* Bottom Blue Bar */}
      <div className="admin1-bottom-bar"></div>
    </div>
  );
}

export default Admin1;
