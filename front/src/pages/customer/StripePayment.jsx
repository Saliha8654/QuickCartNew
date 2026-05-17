// src/pages/customer/StripePayment.jsx - Stripe Payment Screen
import React, { useState, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { loadStripe } from "@stripe/stripe-js";
import {
  Elements,
  CardElement,
  useStripe,
  useElements,
} from "@stripe/react-stripe-js";
import "./StripePayment.css";
import { MdCheckCircle, MdLock, MdError } from "react-icons/md";
import { FaCreditCard } from "react-icons/fa";
import axios from "axios";

const API_URL = "http://localhost:5000/api";

// Initialize Stripe with your publishable key
const stripePromise = loadStripe("pk_test_51T0LUOHaGEl6oDVfkjbxiBxGYjEaydHSQVQ2lBHSu71hD4yQMQOYcMKJ6XXoyhKzblA8BXSfsJKqNRZc7FeuTZVW00EhC5dsit");

function CheckoutForm({ items, total, onPaymentSuccess }) {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [orderId, setOrderId] = useState("");

  // Generate order ID on component mount
  useEffect(() => {
    const newOrderId = `ORD-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
    setOrderId(newOrderId);
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!stripe || !elements) {
      return;
    }

    setLoading(true);
    setError("");

    try {
      // Create payment intent on backend
      const response = await axios.post(`${API_URL}/payment/create-payment-intent`, {
        amount: Math.round(total * 100), // Convert to cents
        currency: "pkr",
        orderId: orderId,
        items: items
      });

      const { clientSecret } = response.data;

      // Confirm the payment with Stripe
      const result = await stripe.confirmCardPayment(clientSecret, {
        payment_method: {
          card: elements.getElement(CardElement),
          billing_details: {
            name: "Customer Name",
          },
        },
      });

      if (result.error) {
        setError(result.error.message);
        setLoading(false);
      } else {
        if (result.paymentIntent.status === "succeeded") {
          onPaymentSuccess(orderId, total);
        }
        setLoading(false);
      }
    } catch (err) {
      setError(err.response?.data?.message || "Payment failed. Please try again.");
      setLoading(false);
    }
  };

  const cardElementOptions = {
    style: {
      base: {
        fontSize: "16px",
        color: "#424770",
        "::placeholder": {
          color: "#aab7c4",
        },
      },
      invalid: {
        color: "#9e2146",
      },
    },
  };

  return (
    <form onSubmit={handleSubmit} className="stripe-payment-form">
      <div className="form-section order-summary-card">
        <div className="section-header">
          <h3 className="section-title">Order Summary</h3>
        </div>
        
        <div className="order-id-box">
          <span className="order-id-label">Order ID</span>
          <span className="order-id-value">{orderId}</span>
        </div>
        
        <div className="order-amount-display">
          <span className="amount-label">Total Amount</span>
          <span className="amount-value">PKR {total.toFixed(2)}</span>
        </div>
        
        <div className="items-summary-list">
          <h4 className="items-title">Items ({items.length})</h4>
          <div className="items-container">
            {items.slice(0, 3).map((item, index) => (
              <div key={index} className="item-row">
                <div className="item-info">
                  <span className="item-name">{item.name}</span>
                  <span className="item-qty">x{item.quantity}</span>
                </div>
                <span className="item-price">PKR {(item.price * item.quantity).toFixed(2)}</span>
              </div>
            ))}
            {items.length > 3 && (
              <div className="more-items-note">+ {items.length - 3} more items</div>
            )}
          </div>
        </div>
      </div>

      <div className="form-section card-info-section">
        <div className="section-header">
          <MdLock className="section-icon" />
          <h3 className="section-title">Card Information</h3>
        </div>
        <div className="card-input-wrapper">
          <CardElement className="stripe-card-element" options={cardElementOptions} />
        </div>
      </div>

      {error && (
        <div className="error-alert">
          <MdError className="error-icon" />
          <span className="error-text">{error}</span>
        </div>
      )}

      <button 
        type="submit" 
        disabled={!stripe || loading}
        className="pay-button"
      >
        {loading ? "Processing Payment..." : `Pay PKR ${total.toFixed(2)}`}
      </button>
    </form>
  );
}

function StripePayment() {
  const navigate = useNavigate();
  const location = useLocation();
  const { items, total } = location.state || { items: [], total: 0 };
  
  const [paymentStatus, setPaymentStatus] = useState("pending"); // pending, success, failed

  const handlePaymentSuccess = async (orderId, amount) => {
    setPaymentStatus("success");
    // In a real app, you might want to save the order ID and amount
    console.log("Payment successful!", { orderId, amount });
    
    // Clear the cart from the database after successful payment
    try {
      await axios.delete(`${API_URL}/cart`);
      console.log("Cart cleared successfully after payment");
    } catch (err) {
      console.error("Error clearing cart:", err);
    }
  };

  const handleProceed = () => {
    navigate("/receipt", { state: { items, total, paymentMethod: "Credit Card" } });
  };

  const handleRetry = () => {
    setPaymentStatus("pending");
    window.location.reload(); // Simple way to reset the form
  };

  if (paymentStatus === "success") {
    return (
      <div className="stripe-payment-success">
        <div className="success-content">
          <div className="success-card">
            <div className="success-icon-large">
              <MdCheckCircle />
            </div>
            <h2 className="success-title">Payment Successful!</h2>
            <p className="success-message">Your payment has been processed successfully</p>
            
            <div className="success-details">
              <div className="detail-row">
                <span className="detail-label">Order ID</span>
                <span className="detail-value">ORD-{Date.now()}-{Math.floor(Math.random() * 1000)}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Amount Paid</span>
                <span className="detail-value-amount">PKR {total.toFixed(2)}</span>
              </div>
            </div>
            
            <button className="proceed-btn" onClick={handleProceed}>
              View Receipt
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="stripe-payment">
      {/* Header Section */}
      <div className="stripe-page-header">
        <div className="header-icon">
          <MdLock />
        </div>
        <h2 className="page-title">Secure Payment</h2>
        <p className="page-subtitle">Complete your payment safely</p>
      </div>

      {/* Main Content */}
      <div className="stripe-content">
        <div className="payment-form-wrapper">
          <Elements stripe={stripePromise}>
            <CheckoutForm 
              items={items} 
              total={total} 
              onPaymentSuccess={handlePaymentSuccess}
            />
          </Elements>

          {paymentStatus === "failed" && (
            <div className="payment-failed-alert">
              <div className="failed-card">
                <div className="failed-icon">
                  <MdError />
                </div>
                <h3>Payment Failed</h3>
                <p>Something went wrong with your payment. Please try again.</p>
                <button className="retry-btn" onClick={handleRetry}>
                  Try Again
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default StripePayment;