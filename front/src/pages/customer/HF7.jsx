// src/pages/customer/HF7.jsx - Digital Receipt Screen
import React from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./HF7.css";
import { IoMdArrowBack } from "react-icons/io";
import { FiHome, FiPrinter } from "react-icons/fi";

function HF7() {
  const navigate = useNavigate();
  const location = useLocation();

  // Extract data from navigation state
  const {
    items = [],
    total = 0,
    paymentMethod = "Credit Card",
    orderId = `ORD-${Date.now()}`
  } = location.state || {};

  const handleGoHome = () => {
    navigate("/");
  };

  const handlePrint = () => {
    window.print();
  };

  // Calculations for display
  const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const tax = subtotal * 0.1;

  return (
    <div className="hf7-receipt">
      {/* Header Bar */}
      <div className="hf7-receipt-header">
        <button className="receipt-back-btn" onClick={handleGoHome}>
          <IoMdArrowBack />
        </button>
        <h2 className="hf7-receipt-heading">Digital Receipt</h2>
      </div>

      {/* Content */}
      <div className="receipt-content">
        <div className="receipt-card">
          <div className="success-banner">
            <span className="success-icon">✅</span>
            <h2>Payment Successful</h2>
            <p>Thank you for shopping with QuickCart!</p>
          </div>

          <div className="receipt-info">
            <div className="info-row">
              <span>Order ID:</span>
              <span>{orderId}</span>
            </div>
            <div className="info-row">
              <span>Date:</span>
              <span>{new Date().toLocaleDateString()}</span>
            </div>
            <div className="info-row">
              <span>Time:</span>
              <span>{new Date().toLocaleTimeString()}</span>
            </div>
            <div className="info-row">
              <span>Payment Type:</span>
              <span>{paymentMethod}</span>
            </div>
          </div>

          <div className="receipt-items">
            <h3>Purchased Items</h3>
            {items.map((item, index) => (
              <div key={index} className="receipt-item-row">
                <div className="item-name-qty">
                  <span className="item-name">{item.name}</span>
                  <span className="item-qty">Qty: {item.quantity} x Rs {item.price.toFixed(2)}</span>
                </div>
                <span className="item-price">Rs {(item.price * item.quantity).toFixed(2)}</span>
              </div>
            ))}
          </div>

          <div className="receipt-totals">
            <div className="total-row">
              <span>Subtotal:</span>
              <span>Rs {subtotal.toFixed(2)}</span>
            </div>
            <div className="total-row">
              <span>Tax (10%):</span>
              <span>Rs {tax.toFixed(2)}</span>
            </div>
            <div className="grand-total-row">
              <span>Total Amount:</span>
              <span>Rs {total || (subtotal + tax).toFixed(2)}</span>
            </div>
          </div>

          <div className="receipt-actions">
            <button className="home-btn" onClick={handleGoHome}>
              <FiHome style={{ marginRight: "8px" }} />
              Back to Home
            </button>
            <button className="print-btn" onClick={handlePrint}>
              <FiPrinter style={{ marginRight: "8px" }} />
              Print Receipt
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HF7;
