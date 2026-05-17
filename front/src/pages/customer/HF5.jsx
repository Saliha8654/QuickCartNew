// src/pages/customer/HF5.jsx - Weight Verification Screen
import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./HF5.css";
import { MdCheckCircle, MdWarning, MdRefresh } from "react-icons/md";
import { HiOutlineScale } from "react-icons/hi";
import { FaShoppingCart } from "react-icons/fa";
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
      setActualWeight(actualWeightValue);
      
      // Calculate total expected weight
      const totalExpected = items.reduce((sum, item) => sum + item.expectedWeight, 0);
      
      // Update items with detected weight and status
      const updatedItems = items.map(item => {
        // For simplicity, distribute the actual weight proportionally
        const proportion = item.expectedWeight / totalExpected;
        const detectedWeight = actualWeightValue * proportion;
        
        // Check if weight matches (with 5% tolerance)
        const tolerance = item.expectedWeight * 0.05;
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

  const handleRescanItems = () => {
    navigate("/detect-items");
  };

  const handleProceedToCheckout = () => {
    navigate("/payment-selection");
  };

  return (
    <div className="hf5">
      {/* Page Header Section */}
      <div className="hf5-header">
        <div className="header-icon">
          <HiOutlineScale />
        </div>
        <h2 className="hf5-page-title">Weight Verification</h2>
        <p className="hf5-page-subtitle">Verify your items match the expected weight</p>
      </div>

      {/* Main Content */}
      <div className="hf5-content">
        <div className="verification-container">
          {items.length === 0 ? (
            <div className="loading-state">
              <FaShoppingCart className="loading-icon" />
              <p>Loading cart items...</p>
            </div>
          ) : (
            <>
              <div className="items-section">
                <div className="items-header">
                  <h3 className="section-title">Items to Verify</h3>
                  <span className="items-badge">{items.length}</span>
                </div>

                <div className="verification-items">
                  {items.map((item, index) => {
                    const status = item.status || 'Pending';
                    const statusClass = status.toLowerCase();
                    const isMatched = status === 'Matched';
                    const isPending = status === 'Pending';
                    
                    return (
                      <div key={item.id} className="item-card" style={{
                        animation: `slideUpCard 0.4s ease-out ${index * 0.1}s backwards`
                      }}>
                        <div className="item-header">
                          <div className="item-icon">📦</div>
                          <div className="item-name-section">
                            <h4 className="item-name">{item.name || 'Unknown Product'}</h4>
                            <p className="item-qty">Qty: {item.quantity}</p>
                          </div>
                          <div className={`status-badge ${statusClass}`}>
                            {isPending && <span className="badge-icon">⏳</span>}
                            {isMatched && <MdCheckCircle className="badge-icon check" />}
                            {!isPending && !isMatched && <MdWarning className="badge-icon warning" />}
                            <span>{status}</span>
                          </div>
                        </div>

                        <div className="item-weights">
                          <div className="weight-info">
                            <span className="weight-label">Expected</span>
                            <span className="weight-value">{item.expectedWeight.toFixed(1)}g</span>
                          </div>
                          <div className="weight-arrow">→</div>
                          <div className="weight-info">
                            <span className="weight-label">Detected</span>
                            <span className={`weight-value ${statusClass}`}>
                              {item.detectedWeight.toFixed(1)}g
                            </span>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Verification Summary */}
              {verificationStatus && (
                <div className={`verification-summary ${verificationStatus}`}>
                  <div className="summary-content">
                    <div className="summary-icon">
                      {verificationStatus === 'matched' ? (
                        <MdCheckCircle />
                      ) : (
                        <MdWarning />
                      )}
                    </div>
                    <div className="summary-text">
                      <h3 className="summary-title">
                        {verificationStatus === 'matched' ? 'Perfect! All verified' : 'Weight Mismatch'}
                      </h3>
                      <p className="summary-message">
                        {verificationStatus === 'matched'
                          ? 'All items match the expected weight. Ready to proceed!'
                          : 'Some items do not match. Please verify and rescan if needed.'}
                      </p>
                    </div>
                  </div>
                </div>
              )}

              <div className="action-buttons-section">
                <button 
                  className="action-btn verify-btn" 
                  onClick={verifyWeight}
                  disabled={isVerifying}
                  title="Verify the weight of your items"
                >
                  <HiOutlineScale className="btn-icon" />
                  {isVerifying ? 'Verifying...' : 'Verify Weight'}
                </button>
                <button className="action-btn rescan-btn" onClick={handleRescanItems} title="Go back and rescan items">
                  <MdRefresh className="btn-icon" />
                  Rescan Items
                </button>
                <button 
                  className="action-btn proceed-btn" 
                  onClick={handleProceedToCheckout}
                  title="Proceed to payment"
                >
                  <FaShoppingCart className="btn-icon" />
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
