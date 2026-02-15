// src/pages/customer/HF7.jsx - Weight Verification Screen
import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./HF7.css";
import logo from "../../assets/logo.png";
import { FiMenu } from "react-icons/fi";
import { IoMdArrowBack } from "react-icons/io";
import axios from "axios";

const API_URL = "http://localhost:5000/api";

function HF7() {
  const navigate = useNavigate();
  const location = useLocation();
  const { items } = location.state || { items: [] };
  
  const [currentWeight, setCurrentWeight] = useState(0);
  const [expectedWeight, setExpectedWeight] = useState(0);
  const [isVerified, setIsVerified] = useState(false);
  const [verificationResult, setVerificationResult] = useState(null);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isReading, setIsReading] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState("disconnected");
  const [error, setError] = useState("");

  // Calculate expected weight from items
  useEffect(() => {
    const totalExpected = items.reduce((total, item) => {
      const itemExpected = item.expected_weight_g ? item.expected_weight_g * item.quantity : 0;
      return total + itemExpected;
    }, 0);
    setExpectedWeight(totalExpected);
  }, [items]);

  const connectToWeightSensor = async () => {
    setIsConnecting(true);
    setError("");
    
    try {
      // In a real implementation, you would specify the port
      // For now, we'll let the backend try common ports
      const response = await axios.post(`${API_URL}/weight_sensor/connect`);
      if (response.data.status === "connected") {
        setConnectionStatus("connected");
      } else {
        setError("Failed to connect to weight sensor");
      }
    } catch (err) {
      setError("Error connecting to weight sensor: " + (err.response?.data?.message || err.message));
    } finally {
      setIsConnecting(false);
    }
  };

  const readWeight = async () => {
    if (connectionStatus !== "connected") {
      setError("Please connect to weight sensor first");
      return;
    }
    
    setIsReading(true);
    setError("");
    
    try {
      const response = await axios.get(`${API_URL}/weight_sensor/read`);
      setCurrentWeight(response.data.weight_g);
    } catch (err) {
      setError("Error reading weight: " + (err.response?.data?.message || err.message));
    } finally {
      setIsReading(false);
    }
  };

  const verifyWeight = async () => {
    if (connectionStatus !== "connected") {
      setError("Please connect to weight sensor first");
      return;
    }
    
    setIsReading(true);
    setError("");
    
    try {
      const response = await axios.post(`${API_URL}/weight_sensor/verify_cart`, {
        tolerance: 0.05 // 5% tolerance
      });
      
      setVerificationResult(response.data);
      setIsVerified(response.data.verified);
    } catch (err) {
      setError("Error verifying weight: " + (err.response?.data?.message || err.message));
    } finally {
      setIsReading(false);
    }
  };

  const handleBack = () => {
    navigate("/product-confirmation");
  };

  const handleProceed = () => {
    // In a real implementation, you might want to save the verification result
    // and proceed to payment
    navigate("/payment");
  };

  return (
    <div className="hf7">
      {/* Top Blue Bar with Logo and Menu */}
      <div className="hf7-top-bar">
        <div className="hf7-logo">
          <img src={logo} alt="Quick Cart" />
        </div>
        <button className="hf7-menu-btn">
          <FiMenu />
        </button>
      </div>

      {/* Skin Color Bar with Back Arrow and Heading */}
      <div className="hf7-header-bar">
        <button className="hf7-back-btn" onClick={handleBack}>
          <IoMdArrowBack />
        </button>
        <h2 className="hf7-heading">Weight Verification</h2>
      </div>

      {/* Main Content */}
      <div className="hf7-content">
        <div className="weight-verification-container">
          {/* Connection Section */}
          <div className="connection-section">
            <h3>Weight Sensor Connection</h3>
            <div className="connection-status">
              <span className={`status-indicator ${connectionStatus}`}></span>
              <span className="status-text">
                {connectionStatus === "connected" ? "Connected" : "Disconnected"}
              </span>
            </div>
            <button 
              className="connect-btn" 
              onClick={connectToWeightSensor}
              disabled={isConnecting || connectionStatus === "connected"}
            >
              {isConnecting ? "Connecting..." : "Connect to Weight Sensor"}
            </button>
          </div>

          {/* Weight Display */}
          <div className="weight-display-section">
            <h3>Weight Measurement</h3>
            <div className="weight-display">
              <div className="weight-value">
                <span className="current-weight">{currentWeight.toFixed(2)}</span>
                <span className="weight-unit">g</span>
              </div>
              <div className="expected-weight">
                Expected: {expectedWeight.toFixed(2)}g
              </div>
            </div>
            <button 
              className="read-weight-btn" 
              onClick={readWeight}
              disabled={isReading || connectionStatus !== "connected"}
            >
              {isReading ? "Reading..." : "Read Weight"}
            </button>
          </div>

          {/* Verification Section */}
          <div className="verification-section">
            <h3>Verification</h3>
            {verificationResult ? (
              <div className={`verification-result ${isVerified ? 'verified' : 'not-verified'}`}>
                <div className="verification-status">
                  {isVerified ? "✅ Verified" : "❌ Not Verified"}
                </div>
                <div className="verification-details">
                  <p>Expected: {verificationResult.expected_total_g.toFixed(2)}g</p>
                  <p>Actual: {verificationResult.actual_weight_g.toFixed(2)}g</p>
                  <p>Tolerance: ±{verificationResult.tolerance_percent}%</p>
                  <p>Range: {verificationResult.lower_bound_g.toFixed(2)}g - {verificationResult.upper_bound_g.toFixed(2)}g</p>
                </div>
              </div>
            ) : (
              <p className="verification-instruction">
                Click "Verify Weight" to check if the actual weight matches expected weight
              </p>
            )}
            <button 
              className="verify-btn" 
              onClick={verifyWeight}
              disabled={isReading || connectionStatus !== "connected"}
            >
              {isReading ? "Verifying..." : "Verify Weight"}
            </button>
          </div>

          {/* Items List */}
          <div className="items-section">
            <h3>Items in Cart</h3>
            <div className="items-list">
              {items.length === 0 ? (
                <p>No items in cart</p>
              ) : (
                items.map((item) => (
                  <div key={item.id} className="item-row">
                    <span className="item-name">{item.name}</span>
                    <span className="item-quantity">Qty: {item.quantity}</span>
                    <span className="item-weight">
                      {item.expected_weight_g ? `${(item.expected_weight_g * item.quantity).toFixed(2)}g` : "N/A"}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="error-message">
              {error}
            </div>
          )}

          {/* Action Buttons */}
          <div className="action-buttons">
            <button 
              className="proceed-btn" 
              onClick={handleProceed}
              disabled={!isVerified}
            >
              Proceed to Payment
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HF7;