// src/pages/customer/HF6.jsx - Payment Selection Screen
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./HF6.css";
import { IoMdArrowBack } from "react-icons/io";
import { FaCreditCard, FaMoneyBillWave, FaApple, FaGoogle } from "react-icons/fa";
import { MdLock, MdVerifiedUser, MdShield } from "react-icons/md";
import axios from "axios";

const API_URL = "http://localhost:5000/api";

function HF6() {
  const navigate = useNavigate();
  const [selectedPayment, setSelectedPayment] = useState(null);
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // Fetch cart items on component mount
  useEffect(() => {
    fetchCartItems();
  }, []);

  const fetchCartItems = async () => {
    try {
      const response = await axios.get(`${API_URL}/cart`);
      setItems(response.data.items || []);
      setLoading(false);
    } catch (err) {
      console.error("Error fetching cart:", err);
      setError("Failed to load cart items");
      setLoading(false);
    }
  };

  const getSubtotal = () => {
    return items.reduce((total, item) => total + (item.price || 0) * (item.quantity || 1), 0);
  };

  const getTax = () => {
    return getSubtotal() * 0.1; // 10% tax
  };

  const getTotal = () => {
    return getSubtotal() + getTax();
  };

  const paymentMethods = [
    { id: 1, name: "Card Payment", icon: <FaCreditCard />, description: "Credit/Debit Card" },
    { id: 2, name: "Cash Payment", icon: <FaMoneyBillWave />, description: "Pay at counter" },
    // More payment methods can be added here
  ];

  const handleBack = () => {
    navigate("/weight-verification");
  };

  const handlePaymentSelect = (methodId) => {
    setSelectedPayment(methodId);
    setTimeout(() => {
      if (methodId === 1) { // Credit Card
        // Navigate to Stripe payment page with items and total
        navigate("/stripe-payment", { state: { items, total: getTotal() } });
      } else {
        navigate("/receipt", { state: { items, total: getTotal() } });
      }
    }, 500);
  };

  return (
    <div className="hf6">
      {/* Navigation Bar */}
      <div className="hf6-navbar">
        <div className="navbar-content">
          <button className="navbar-back-btn" onClick={handleBack}>
            <IoMdArrowBack />
          </button>
          <h1 className="navbar-title">quickcart</h1>
          <div style={{ width: '40px' }}></div>
        </div>
      </div>

      {/* Header Section */}
      <div className="hf6-header">
        <div className="header-icon">
          <MdShield />
        </div>
        <h2 className="hf6-page-title">Secure Payment</h2>
        <p className="hf6-page-subtitle">Choose your preferred payment method</p>
      </div>

      {/* Main Content */}
      <div className="hf6-content">
        {loading && (
          <div className="loading-state">
            <p>Loading payment options...</p>
          </div>
        )}
        {error && (
          <div className="error-state">
            <p>{error}</p>
          </div>
        )}

        {!loading && !error && (
          <div className="hf6-main-grid">
            {/* Left Column - Payment Methods */}
            <div className="payment-methods-section">
              <div className="methods-header">
                <h3 className="methods-title">Payment Methods</h3>
                <span className="methods-badge">{paymentMethods.length}</span>
              </div>
              
              <div className="payment-methods">
                {paymentMethods.map((method, index) => (
                  <button
                    key={method.id}
                    className={`payment-method-btn ${
                      selectedPayment === method.id ? "selected" : ""
                    }`}
                    onClick={() => handlePaymentSelect(method.id)}
                    style={{
                      animation: `slideUpCard 0.4s ease-out ${index * 0.1}s backwards`
                    }}
                  >
                    <div className="method-icon">{method.icon}</div>
                    <div className="method-info">
                      <h4 className="method-name">{method.name}</h4>
                      <p className="method-description">{method.description}</p>
                    </div>
                    {selectedPayment === method.id && (
                      <div className="check-mark">✓</div>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Right Column - Order Summary & Security */}
            <div className="right-section">
              {/* Order Summary Card */}
              <div className="order-summary-card">
                <h3 className="summary-title">Order Summary</h3>
                
                <div className="summary-divider"></div>
                
                <div className="summary-details">
                  <div className="summary-row">
                    <span className="summary-label">Subtotal</span>
                    <span className="summary-value">PKR {getSubtotal().toFixed(2)}</span>
                  </div>
                  <div className="summary-row">
                    <span className="summary-label">Tax (10%)</span>
                    <span className="summary-value">PKR {getTax().toFixed(2)}</span>
                  </div>
                  <div className="summary-row total-row">
                    <span className="summary-label-total">Total Amount</span>
                    <span className="summary-total">PKR {getTotal().toFixed(2)}</span>
                  </div>
                </div>

                <div className="summary-divider"></div>

                {/* Security Section */}
                <div className="security-section">
                  <h4 className="security-title">
                    <MdLock className="lock-icon" />
                    Secure & Verified
                  </h4>
                  <div className="security-features">
                    <div className="security-feature">
                      <MdVerifiedUser className="feature-icon" />
                      <span>SSL Encrypted</span>
                    </div>
                    <div className="security-feature">
                      <MdShield className="feature-icon" />
                      <span>PCI Compliant</span>
                    </div>
                  </div>
                  <p className="security-text">
                    All payments are processed securely through Stripe
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default HF6;
