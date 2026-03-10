// src/pages/customer/HF5.jsx - Weight Verification Screen
import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./HF5.css";
import { FiMenu } from "react-icons/fi";
import { IoMdArrowBack } from "react-icons/io";
import axios from "axios";

const API_URL = "http://localhost:5000/api";

function HF5() {
  const navigate = useNavigate();
  const location = useLocation();
  const [items, setItems] = useState([]);
  const [actualWeight, setActualWeight] = useState(0);
  const [isVerifying, setIsVerifying] = useState(false);
  const [verificationStatus, setVerificationStatus] = useState(null); // null, 'matched', 'unmatched'

  // Fetch cart items and their expected weights
  useEffect(() => {
    fetchCartItems();
  }, []);

  const fetchCartItems = async () => {
    try {
      const response = await axios.get(`${API_URL}/cart`);
      const cartItems = response.data.items || [];

      // Map cart items to include expected weight
      const itemsWithWeights = cartItems.map(item => ({
        id: item.id,
        name: item.name,
        quantity: item.quantity,
        expectedWeight: (item.expected_weight_g || 0) * item.quantity, // Total expected weight
        detectedWeight: 0, // Will be set during verification
        status: "Pending"
      }));

      setItems(itemsWithWeights);
    } catch (error) {
      console.error("Error fetching cart items:", error);
    }
  };

  const verifyWeight = async () => {
    setIsVerifying(true);
    try {
      // Get actual weight from weight sensor
      const weightResponse = await axios.get(`${API_URL}/weight_sensor/read`);
      const actualWeightValue = weightResponse.data.weight_g || 0;
      console.log(`[Weight Sensor] Actual Reading: ${actualWeightValue}g`);

      if (actualWeightValue === -999) {
        alert("Scale Error: Your Arduino scale needs to be calibrated. Please run the calibration command 'c500' in the Arduino Serial Monitor or a test script.");
        setActualWeight(0);
        return;
      }

      setActualWeight(actualWeightValue);

      // Calculate total expected weight
      const totalExpected = items.reduce((sum, item) => sum + item.expectedWeight, 0);
      console.log(`[Weight Sensor] Total Expected: ${totalExpected}g`);

      // Update items with detected weight and status
      const updatedItems = items.map(item => {
        // For simplicity, distribute the actual weight proportionally
        const proportion = item.expectedWeight / totalExpected;
        const detectedWeight = actualWeightValue * proportion;

        // Check if weight matches (with 10% tolerance for lightweight items)
        const tolerance = item.expectedWeight * 0.10;
        const matched = Math.abs(detectedWeight - item.expectedWeight) <= tolerance;

        return {
          ...item,
          detectedWeight: detectedWeight,
          status: matched ? "Matched" : "Unmatched"
        };
      });

      setItems(updatedItems);

      // Overall verification status
      const allMatched = updatedItems.every(item => item.status === "Matched");
      setVerificationStatus(allMatched ? 'matched' : 'unmatched');

    } catch (error) {
      console.error("Error verifying weight:", error);
      alert("Failed to verify weight. Please ensure weight sensor is connected.");
    } finally {
      setIsVerifying(false);
    }
  };

  const handleBack = () => {
    navigate("/product-confirmation");
  };

  const handleRescanItems = () => {
    navigate("/detect-items");
  };

  const handleProceedToCheckout = () => {
    navigate("/payment-selection");
  };

  return (
    <div className="hf5">
      {/* Skin Color Header Bar */}
      <div className="hf5-header-bar">
        <button className="hf5-back-btn" onClick={handleBack}>
          <IoMdArrowBack />
        </button>
        <h2 className="hf5-heading">Weight Verification</h2>
      </div>

      {/* Main Content */}
      <div className="hf5-content">
        <div className="verification-table-container">
          {items.length === 0 ? (
            <p style={{ textAlign: 'center', padding: '20px' }}>Loading cart items...</p>
          ) : (
            <>
              <div className="verification-table">
                <div className="table-header">
                  <div className="header-cell">Product</div>
                  <div className="header-cell">Qty</div>
                  <div className="header-cell">Expected Weight (g)</div>
                  <div className="header-cell">Detected Weight (g)</div>
                  <div className="header-cell">Status</div>
                </div>

                <div className="table-body">
                  {items.map((item) => {
                    const status = item.status || 'Pending';
                    const statusClass = status.toLowerCase();
                    return (
                      <div key={item.id} className="table-row">
                        <div className="product-cell">
                          <div className="product-image">🛒</div>
                          <span className="product-name">{item.name || 'Unknown Product'}</span>
                        </div>
                        <div className="cell">{item.quantity}</div>
                        <div className="cell">{item.expectedWeight.toFixed(1)}g</div>
                        <div className="cell">{item.detectedWeight.toFixed(1)}g</div>
                        <div className="cell">
                          <span className={`status-badge ${statusClass}`}>
                            {status}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Verification Summary */}
              {verificationStatus && (
                <div className={`verification-summary ${verificationStatus}`}>
                  {verificationStatus === 'matched' ? (
                    <>
                      <span className="summary-icon">✅</span>
                      <span>All items verified successfully!</span>
                    </>
                  ) : (
                    <>
                      <span className="summary-icon">⚠️</span>
                      <span>Weight mismatch detected. Please check items.</span>
                    </>
                  )}
                </div>
              )}

              <div className="action-buttons">
                <button
                  className="action-btn verify-btn"
                  onClick={verifyWeight}
                  disabled={isVerifying}
                >
                  {isVerifying ? 'Verifying...' : 'Verify Weight'}
                </button>
                <button className="action-btn rescan-btn" onClick={handleRescanItems}>
                  Rescan Items
                </button>
                <button
                  className="action-btn proceed-btn"
                  onClick={handleProceedToCheckout}
                >
                  Proceed to Checkout
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default HF5;
