// src/pages/customer/HF4.jsx - Product Confirmation Screen
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./HF4.css";
import { FiPlus, FiMinus } from "react-icons/fi";
import { MdDelete, MdCheckCircle } from "react-icons/md";
import { FaShoppingCart } from "react-icons/fa";
import axios from "axios";

const API_URL = "http://localhost:5000/api";

function HF4() {
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch cart items from backend
    fetchCartItems();
  }, []);

  const fetchCartItems = async () => {
    try {
      const response = await axios.get(`${API_URL}/cart`);
      setItems(response.data.items.map(item => ({
        id: item.id,
        product_id: item.product_id,
        name: item.name,
        price: item.price,
        quantity: item.quantity,
        image_url: item.image_url
      })));
      setLoading(false);
    } catch (error) {
      console.error("Error fetching cart:", error);
      setLoading(false);
    }
  };

  const updateQuantity = async (cartItemId, change) => {
    const item = items.find(i => i.id === cartItemId);
    if (!item) return;

    const newQuantity = item.quantity + change;

    if (newQuantity < 1) {
      removeItem(cartItemId);
      return;
    }

    try {
      await axios.patch(`${API_URL}/cart/${cartItemId}`, {
        quantity: newQuantity
      });

      // Update local state
      setItems(prevItems =>
        prevItems.map(i =>
          i.id === cartItemId
            ? { ...i, quantity: newQuantity }
            : i
        )
      );
    } catch (error) {
      console.error("Error updating quantity:", error);
      if (error.response?.data?.error) {
        alert(error.response.data.error);
      }
    }
  };

  const removeItem = async (cartItemId) => {
    try {
      await axios.delete(`${API_URL}/cart/${cartItemId}`);
      setItems(prevItems => prevItems.filter(item => item.id !== cartItemId));
    } catch (error) {
      console.error("Error removing item:", error);
    }
  };

  const getSubtotal = () => {
    return items
      .reduce((total, item) => total + item.price * item.quantity, 0)
      .toFixed(2);
  };

  const getTax = () => {
    return (parseFloat(getSubtotal()) * 0.1).toFixed(2);
  };

  const getTotal = () => {
    return (parseFloat(getSubtotal()) + parseFloat(getTax())).toFixed(2);
  };

  const handleWeightVerification = () => {
    navigate("/weight-verification", { state: { items } });
  };

  const handleFindItems = () => {
    navigate("/find-products");
  };

  if (loading) {
    return (
      <div className="hf4">
        <p style={{ textAlign: 'center', marginTop: '50px' }}>Loading cart...</p>
      </div>
    );
  }

  return (
    <div className="hf4">
      {/* Page Header */}
      <div className="hf4-header">
        <h2 className="hf4-page-title">Review Your Order</h2>
        <p className="hf4-page-subtitle">Verify items and proceed with checkout</p>
      </div>

      {/* Main Content */}
      <div className="hf4-content">
        {/* Left Column - Product Cards */}
        <div className="hf4-left-section">
          <div className="items-header">
            <h3 className="section-title">Your Items</h3>
            <span className="items-count">{items.length}</span>
          </div>

          {items.length === 0 ? (
            <div className="empty-state">
              <FaShoppingCart className="empty-icon" />
              <p className="empty-text">No items in cart yet</p>
              <p className="empty-subtext">Add items from detection to get started</p>
            </div>
          ) : (
            <div className="products-list">
              {items.map((item) => (
                <div key={item.id} className="product-card" data-item-id={item.id}>
                  <div className="product-info">
                    <div className="product-image">🛍️</div>
                    <div className="product-details">
                      <h4 className="product-name">{item.name}</h4>
                      <p className="product-price">Rs {item.price.toFixed(2)}</p>
                    </div>
                  </div>

                  <div className="product-controls">
                    <div className="quantity-control">
                      <button
                        className="qty-btn minus-btn"
                        onClick={() => updateQuantity(item.id, -1)}
                        title="Decrease quantity"
                      >
                        <FiMinus />
                      </button>
                      <span className="qty-value">{item.quantity}</span>
                      <button
                        className="qty-btn plus-btn"
                        onClick={() => updateQuantity(item.id, 1)}
                        title="Increase quantity"
                      >
                        <FiPlus />
                      </button>
                    </div>
                    <div className="product-total">Rs {(item.price * item.quantity).toFixed(2)}</div>
                    <button
                      className="remove-btn"
                      onClick={() => removeItem(item.id)}
                      title="Remove from cart"
                    >
                      <MdDelete />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Column - Order Summary */}
        <div className="hf4-right-section">
          <div className="summary-card">
            <div className="summary-icon">
              <FaShoppingCart />
            </div>
            <h3 className="summary-title">Order Summary</h3>

            <div className="summary-divider"></div>

            <div className="summary-details">
              <div className="summary-row">
                <span className="summary-label">Subtotal</span>
                <span className="summary-value">Rs {getSubtotal()}</span>
              </div>
              <div className="summary-row">
                <span className="summary-label">Tax (10%)</span>
                <span className="summary-value">Rs {getTax()}</span>
              </div>
              <div className="summary-row total-row">
                <span className="summary-label">Total</span>
                <span className="summary-total">Rs {getTotal()}</span>
              </div>
            </div>

            <div className="summary-divider"></div>

            <button
              className="action-btn weight-btn"
              onClick={handleWeightVerification}
              disabled={items.length === 0}
              title="Verify order weight"
            >
              <MdCheckCircle className="btn-icon" />
              Weight Verification
            </button>
            <button className="action-btn find-btn" onClick={handleFindItems} title="Continue shopping">
              <FaShoppingCart className="btn-icon" />
              Continue Shopping
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default HF4;
