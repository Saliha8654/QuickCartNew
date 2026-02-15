// src/pages/customer/HF6.jsx - Payment Selection Screen
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./HF6.css";
import logo from "../../assets/logo.png";
import { FiMenu } from "react-icons/fi";
import { IoMdArrowBack } from "react-icons/io";
import { FaCreditCard, FaMoneyBillWave, FaGift, FaIdCard } from "react-icons/fa";
import { MdPayment } from "react-icons/md";
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
    { id: 1, name: "Card Payment", icon: <FaCreditCard /> },
    // You can add more payment methods here in the future
    // { id: 2, name: "Cash", icon: <FaMoneyBillWave /> },
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
      {/* Skin Color Header Bar */}
      <div className="hf6-header-bar">
        <button className="hf6-back-btn" onClick={handleBack}>
          <IoMdArrowBack />
        </button>
        <h2 className="hf6-heading">Payment Selection</h2>
      </div>

      {/* Main Content */}
      <div className="hf6-content">
        <h2 className="payment-title">Select Payment Method</h2>

        {loading && <p style={{ textAlign: 'center' }}>Loading payment options...</p>}
        {error && <p style={{ textAlign: 'center', color: 'red' }}>{error}</p>}

        {!loading && !error && (
          <div className="hf6-main-grid">
            {/* Left Column - Payment Methods */}
            <div className="payment-methods">
              {paymentMethods.map((method) => (
                <button
                  key={method.id}
                  className={`payment-method-btn ${
                    selectedPayment === method.id ? "selected" : ""
                  }`}
                  onClick={() => handlePaymentSelect(method.id)}
                >
                  <div className="payment-icon">{method.icon}</div>
                  <span className="payment-name">{method.name}</span>
                </button>
              ))}
            </div>

            {/* Right Column - Order Summary */}
            <div className="order-summary">
              <h3 className="summary-title">Order Summary</h3>
              <div className="summary-details">
                <div className="summary-row">
                  <span>Subtotal:</span>
                  <span>PKR {getSubtotal().toFixed(2)}</span>
                </div>
                <div className="summary-row">
                  <span>Tax (10%):</span>
                  <span>PKR {getTax().toFixed(2)}</span>
                </div>
                <div className="summary-row total-row">
                  <span>Total:</span>
                  <span>PKR {getTotal().toFixed(2)}</span>
                </div>
              </div>
              
              {/* Payment Info */}
              <div className="payment-info">
                <h4>Secure Payment</h4>
                <p>All payments are processed securely through Stripe.</p>
                <div className="security-icons">
                  <span>🔒 SSL Encrypted</span>
                  <span>💳 PCI Compliant</span>
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
