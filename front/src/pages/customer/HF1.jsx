// src/pages/customer/HF1.jsx - Place Item in Basket Screen
import React from "react";
import { useNavigate } from "react-router-dom";
import "./HF1.css";
import { FaShoppingCart } from "react-icons/fa";

function HF1() {
  const navigate = useNavigate();

  const handleProceed = () => {
    navigate("/detect-items");
  };

  return (
    <div className="hf1">
      <div className="hf1-card">
        <div className="hf1-icon-container">
          <FaShoppingCart className="hf1-icon" />
        </div>
        <h1 className="hf1-text">Start Your Smart Checkout</h1>
        <p className="hf1-subtitle">Place your item in the basket to begin scanning</p>
        <button className="proceed-button" onClick={handleProceed}>
          Proceed via Camera
        </button>
      </div>
    </div>
  );
}

export default HF1;
