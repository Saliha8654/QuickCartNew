// src/pages/customer/HF0.jsx
import React from "react";
import { useNavigate } from "react-router-dom";
import "./HF0.css";
import logo from "../../assets/logo.png";
import { FaShoppingCart, FaCamera, FaCheckCircle, FaCreditCard, FaArrowRight } from "react-icons/fa";

function HF0() {
  const navigate = useNavigate();

  const handleStart = () => {
    navigate("/place-item");
  };

  const steps = [
    {
      icon: <FaShoppingCart />,
      title: "Add Items",
      description: "Place items in basket"
    },
    {
      icon: <FaCamera />,
      title: "Scan & Detect",
      description: "Camera detects products"
    },
    {
      icon: <FaCheckCircle />,
      title: "Review",
      description: "Verify your items"
    },
    {
      icon: <FaCreditCard />,
      title: "Pay",
      description: "Complete payment"
    }
  ];

  return (
    <div className="hf0">
      {/* Hero Section */}
      <div className="hf0-hero">
        <div className="hero-content">
          {/* Logo */}
          <div className="hero-logo">
            <img src={logo} alt="Quick Cart Logo" />
          </div>

          {/* Main Tagline */}
          <div className="hero-tagline">
            <h1 className="hero-title">Fast. Smart. Checkout.</h1>
          </div>

          {/* Description */}
          <p className="hero-description">
            Experience the future of retail with AI-powered product detection
          </p>

          {/* CTA Button */}
          <button className="hero-btn" onClick={handleStart}>
            Start Shopping
            <FaArrowRight className="btn-icon" />
          </button>

          {/* Mini Icons */}
          <div className="hero-features">
            <div className="feature-item">
              <FaCamera className="feature-icon" />
              <span>Smart Detection</span>
            </div>
            <div className="feature-item">
              <FaShoppingCart className="feature-icon" />
              <span>Quick Checkout</span>
            </div>
            <div className="feature-item">
              <FaCreditCard className="feature-icon" />
              <span>Secure Payment</span>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="hf0-steps">
        <div className="steps-wrapper">
          <h3 className="steps-title">How It Works</h3>
          <div className="steps-container">
            {steps.map((step, index) => (
              <div key={index} className="step-card">
                <div className="step-number">{index + 1}</div>
                <div className="step-icon">{step.icon}</div>
                <h4 className="step-title">{step.title}</h4>
                <p className="step-description">{step.description}</p>
              </div>
            ))}
          </div>
          {/* Connection Lines */}
          <div className="steps-progress">
            {[0, 1, 2].map((i) => (
              <div key={i} className="progress-line"></div>
            ))}
          </div>
        </div>
      </div>

      {/* Bottom Blue Bar */}
      <div className="hf0-bottom-bar"></div>
    </div>
  );
}

export default HF0;
