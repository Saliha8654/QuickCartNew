import React from "react";
import { useNavigate } from "react-router-dom";
import "./Admin1.css";
import logo from "../../assets/logo.png";
import { FaShieldAlt, FaChartBar, FaBox, FaArrowRight, FaLock } from "react-icons/fa";

function Admin1() {
  const navigate = useNavigate();

  const features = [
    {
      icon: <FaChartBar />,
      title: "Analytics",
      description: "View sales and inventory"
    },
    {
      icon: <FaBox />,
      title: "Products",
      description: "Manage product catalog"
    },
    {
      icon: <FaLock />,
      title: "Security",
      description: "Secure admin controls"
    }
  ];

  return (
    <div className="admin1">
      {/* Hero Section */}
      <div className="admin1-hero">
        <div className="hero-content">
          {/* Logo */}
          <div className="hero-logo">
            <img src={logo} alt="Quick Cart Logo" />
          </div>

          {/* Main Tagline */}
          <div className="hero-tagline">
            <h1 className="hero-title">Admin Control Center</h1>
          </div>

          {/* Description */}
          <p className="hero-description">
            Manage your QuickCart system with powerful admin tools
          </p>

          {/* CTA Buttons */}
          <div className="admin1-buttons">
            <button 
              className="hero-btn login-btn"
              onClick={() => navigate('/admin/login')}
            >
              Log-in
              <FaArrowRight className="btn-icon" />
            </button>
            <button 
              className="hero-btn signup-btn"
              onClick={() => navigate('/admin/signup')}
            >
              Sign-up
              <FaArrowRight className="btn-icon" />
            </button>
          </div>

          {/* Mini Features */}
          <div className="hero-features">
            <div className="feature-item">
              <FaShieldAlt className="feature-icon" />
              <span>Admin Protected</span>
            </div>
            <div className="feature-item">
              <FaChartBar className="feature-icon" />
              <span>Real-time Stats</span>
            </div>
            <div className="feature-item">
              <FaBox className="feature-icon" />
              <span>Full Control</span>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="admin1-features">
        <div className="features-wrapper">
          <h3 className="features-title">Admin Features</h3>
          <div className="features-container">
            {features.map((feature, index) => (
              <div key={index} className="feature-card">
                <div className="feature-number">{index + 1}</div>
                <div className="feature-card-icon">{feature.icon}</div>
                <h4 className="feature-card-title">{feature.title}</h4>
                <p className="feature-card-description">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Admin1;
