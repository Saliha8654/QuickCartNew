// src/pages/customer/HF0.jsx
import React from "react";
import { useNavigate } from "react-router-dom";
import "./HF0.css";
import logo from "../../assets/logo.png";
import barcode from "../../assets/barcode.png";

function HF0() {
  const navigate = useNavigate();

  const handleStart = () => {
    navigate("/place-item");
  };

  return (
    <div className="hf0">
      {/* Logo Section */}
      <div className="hf0-logo">
        <img src={logo} alt="Quick Cart Logo" />
      </div>

      {/* Barcode + Text Section */}
      <div className="hf0-scan">
        <img src={barcode} alt="Barcode" className="barcode-img" />
        <p className="scan-text">Scan as you shop</p>
      </div>

      {/* Start Button */}
      <button className="start-btn" onClick={handleStart}>
        Start
      </button>

      {/* Bottom Blue Bar */}
      <div className="hf0-bottom-bar"></div>
    </div>
  );
}

export default HF0;
