// src/pages/customer/HF1.jsx - Place Item in Basket Screen
import React from "react";
import { useNavigate } from "react-router-dom";
import "./HF1.css";

function HF1() {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate("/detect-items");
  };

  return (
    <div className="hf1" onClick={handleClick}>
      <div className="hf1-content">
        <h1 className="hf1-text">Place your item in the basket</h1>
      </div>
    </div>
  );
}

export default HF1;
