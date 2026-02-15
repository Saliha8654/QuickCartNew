// src/pages/customer/QRPayment.jsx - QR Code Payment Screen
import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import "./QRPayment.css";
import { FiMenu } from "react-icons/fi";
import { IoMdArrowBack } from "react-icons/io";
import { FaQrcode } from "react-icons/fa";
import axios from "axios";
import qrCodeImage from "../../assets/qrcode.jpeg";

const API_URL = "http://localhost:5000/api";

function QRPayment() {
  const navigate = useNavigate();
  const location = useLocation();
  const { items, total } = location.state || { items: [], total: 0 };
  
  const [orderId, setOrderId] = useState("");
  const [qrCodeData, setQrCodeData] = useState("");
  const [paymentStatus, setPaymentStatus] = useState("pending"); // pending, success, failed
  const [timeLeft, setTimeLeft] = useState(300); // 5 minutes in seconds
  const [isGenerating, setIsGenerating] = useState(false);
  const [merchantConfig, setMerchantConfig] = useState(null);

  // Generate order ID and QR code on component mount
  useEffect(() => {
    fetchMerchantConfig();
    generateOrder();
    const timer = setInterval(() => {
      setTimeLeft(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
        });
    }, 1000);
    
    return () => clearInterval(timer);
  }, []);

  // Fetch merchant configuration from backend
  const fetchMerchantConfig = async () => {
    try {
      const response = await axios.get(`${API_URL}/payment/config`);
      setMerchantConfig(response.data);
      console.log("Merchant Config:", response.data);
      
      if (!response.data.is_valid) {
        console.warn("Payment config warning:", response.data.message);
      }
    } catch (error) {
      console.error("Error fetching merchant config:", error);
    }
  };

  // Format time for display
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Generate order and QR code
  const generateOrder = async () => {
    setIsGenerating(true);
    try {
      // Generate a unique order ID
      const newOrderId = `ORD-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
      setOrderId(newOrderId);
      
      // Wait for merchant config if not loaded yet
      let config = merchantConfig;
      if (!config) {
        const response = await axios.get(`${API_URL}/payment/config`);
        config = response.data;
      }
      
      // Standard format for Pakistani payment QR codes (based on EMVCo standard)
      const qrData = JSON.stringify({
        merchant: config?.merchant_name || "QuickCart Store",
        merchantId: config?.merchant_id || "TEST-MERCHANT",
        account: config?.account_number || "03001234567",
        amount: total.toFixed(2),
        currency: "PKR",
        orderId: newOrderId,
        description: `QuickCart Order ${newOrderId}`,
        callbackUrl: `http://localhost:5000/api/payment/webhook`,
        testMode: config?.test_mode || true,
      });
      
      setQrCodeData(qrData);
      
      // Simulate QR code generation delay
      await new Promise(resolve => setTimeout(resolve, 1000));
    } catch (error) {
      console.error("Error generating order:", error);
    } finally {
      setIsGenerating(false);
    }
  };

  // Simulate payment verification
  const checkPaymentStatus = () => {
    // In a real implementation, this would call an API to check payment status
    // For demo, we'll simulate a random success/failure
    const isSuccess = Math.random() > 0.3; // 70% success rate for demo
    setPaymentStatus(isSuccess ? "success" : "failed");
  };

  // Handle manual payment verification
  const verifyPayment = async () => {
    try {
      // In a real implementation, you would call your backend to verify payment
      // For now, we'll simulate this
      const response = await axios.post(`${API_URL}/payment/verify`, {
        orderId: orderId,
        amount: total
      });
      
      if (response.data.success) {
        setPaymentStatus("success");
      } else {
        setPaymentStatus("failed");
      }
    } catch (error) {
      console.error("Error verifying payment:", error);
      setPaymentStatus("failed");
    }
  };

  // Handle back navigation
  const handleBack = () => {
    navigate("/payment-selection");
  };

  // Handle retry payment
  const handleRetry = () => {
    setPaymentStatus("pending");
    setTimeLeft(300);
    generateOrder();
  };

  // Handle proceed to receipt
  const handleProceed = () => {
    navigate("/receipt", { state: { items, total, paymentMethod: "QR Code" } });
  };

  return (
    <div className="qr-payment">
      {/* Skin Color Bar with Back Arrow and Heading */}
      <div className="qr-header-bar">
        <button className="qr-back-btn" onClick={handleBack}>
          <IoMdArrowBack />
        </button>
        <h2 className="qr-heading">QR Code Payment</h2>
      </div>

      {/* Main Content */}
      <div className="qr-content">
        <div className="qr-payment-container">
          {/* Order Info */}
          <div className="order-info">
            <h3>Order Details</h3>
            <div className="order-id">Order ID: {orderId || "Generating..."}</div>
            <div className="order-amount">Amount: PKR {total.toFixed(2)}</div>
            <div className="merchant-info">
              <p className="info-label">EasyPaisa Account:</p>
              <p className="info-value">03157507311</p>
              <p className="info-label">IBAN:</p>
              <p className="info-value">PK93TMF0000000069184980</p>
            </div>
          </div>

          {/* QR Code Display */}
          <div className="qr-code-section">
            <h3>Scan to Pay</h3>
            <div className="qr-display">
              {/* Display actual QR code image */}
              <div className="qr-code-container">
                <img 
                  src={qrCodeImage} 
                  alt="EasyPaisa QR Code" 
                  className="qr-code-image"
                  style={{
                    width: '250px',
                    height: '250px',
                    objectFit: 'contain',
                    border: '2px solid #0c2e4d',
                    borderRadius: '10px',
                    padding: '10px',
                    backgroundColor: 'white'
                  }}
                />
              </div>
              <p className="qr-instruction">Scan with EasyPaisa app</p>
              <div className="timer">
                <span className={`timer-text ${timeLeft < 60 ? 'expiring' : ''}`}>
                  Time left: {formatTime(timeLeft)}
                </span>
              </div>
            </div>
          </div>

          {/* Payment Instructions */}
          <div className="payment-instructions">
            <h3>How to Pay</h3>
            <ol>
              <li>Open EasyPaisa app on your phone</li>
              <li>Tap on "Scan QR" option</li>
              <li>Scan the QR code above</li>
              <li>Confirm payment amount: PKR {total.toFixed(2)}</li>
              <li>Complete transaction with your PIN</li>
            </ol>
            <div className="manual-transfer">
              <p><strong>Or transfer manually to:</strong></p>
              <p>Account: 03157507311</p>
              <p>IBAN: PK93TMF0000000069184980</p>
            </div>
          </div>

          {/* Payment Status */}
          {paymentStatus === "pending" && (
            <div className="payment-actions">
              <button className="verify-btn" onClick={verifyPayment}>
                Verify Payment
              </button>
              <p className="status-text">Waiting for payment confirmation...</p>
            </div>
          )}

          {paymentStatus === "success" && (
            <div className="payment-success">
              <div className="success-icon">✅</div>
              <h3>Payment Successful!</h3>
              <p>Your payment has been confirmed.</p>
              <button className="proceed-btn" onClick={handleProceed}>
                View Receipt
              </button>
            </div>
          )}

          {paymentStatus === "failed" && (
            <div className="payment-failed">
              <div className="failed-icon">❌</div>
              <h3>Payment Failed</h3>
              <p>We couldn't confirm your payment.</p>
              <div className="failed-actions">
                <button className="retry-btn" onClick={handleRetry}>
                  Try Again
                </button>
                <button className="cancel-btn" onClick={handleBack}>
                  Choose Another Method
                </button>
              </div>
            </div>
          )}

          {/* Items Summary */}
          <div className="items-summary">
            <h3>Order Summary</h3>
            <div className="items-list">
              {items.slice(0, 3).map((item, index) => (
                <div key={index} className="item-row">
                  <span className="item-name">{item.name}</span>
                  <span className="item-quantity">x{item.quantity}</span>
                  <span className="item-price">PKR {(item.price * item.quantity).toFixed(2)}</span>
                </div>
              ))}
              {items.length > 3 && (
                <div className="more-items">+ {items.length - 3} more items</div>
              )}
            </div>
            <div className="total-row">
              <span>Total:</span>
              <span>PKR {total.toFixed(2)}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default QRPayment;