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
import { IoMdArrowBack } from "react-icons/io";
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
      <div className="order-summary-stripe">
        <h3>Order Summary</h3>
        <div className="order-id-stripe">Order ID: {orderId}</div>
        <div className="order-amount-stripe">Amount: PKR {total.toFixed(2)}</div>
        
        <div className="items-summary-stripe">
          <h4>Items:</h4>
          {items.slice(0, 3).map((item, index) => (
            <div key={index} className="item-row-stripe">
              <span>{item.name}</span>
              <span>x{item.quantity}</span>
              <span>PKR {(item.price * item.quantity).toFixed(2)}</span>
            </div>
          ))}
          {items.length > 3 && (
            <div className="more-items-stripe">+ {items.length - 3} more items</div>
          )}
        </div>
      </div>

      <div className="card-element-container">
        <h3>Card Information</h3>
        <CardElement options={cardElementOptions} />
      </div>

      {error && <div className="error-message">{error}</div>}

      <button 
        type="submit" 
        disabled={!stripe || loading}
        className="pay-button"
      >
        {loading ? "Processing..." : `Pay PKR ${total.toFixed(2)}`}
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

  const handleBack = () => {
    navigate("/payment-selection");
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
        <div className="success-header">
          <button className="back-btn" onClick={handleBack}>
            <IoMdArrowBack />
          </button>
          <h2>Payment Successful</h2>
        </div>
        
        <div className="success-content">
          <div className="success-icon">✅</div>
          <h3>Thank You!</h3>
          <p>Your payment has been processed successfully.</p>
          <div className="order-details-success">
            <p><strong>Order ID:</strong> ORD-{Date.now()}-{Math.floor(Math.random() * 1000)}</p>
            <p><strong>Amount Paid:</strong> PKR {total.toFixed(2)}</p>
          </div>
          <button className="proceed-btn" onClick={handleProceed}>
            View Receipt
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="stripe-payment">
      {/* Header */}
      <div className="stripe-header-bar">
        <button className="stripe-back-btn" onClick={handleBack}>
          <IoMdArrowBack />
        </button>
        <h2 className="stripe-heading">
          <FaCreditCard style={{ marginRight: "10px" }} />
          Credit Card Payment
        </h2>
      </div>

      {/* Main Content */}
      <div className="stripe-content">
        <Elements stripe={stripePromise}>
          <CheckoutForm 
            items={items} 
            total={total} 
            onPaymentSuccess={handlePaymentSuccess}
          />
        </Elements>

        {paymentStatus === "failed" && (
          <div className="payment-failed-stripe">
            <div className="failed-icon">❌</div>
            <h3>Payment Failed</h3>
            <p>Something went wrong with your payment.</p>
            <button className="retry-btn-stripe" onClick={handleRetry}>
              Try Again
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default StripePayment;