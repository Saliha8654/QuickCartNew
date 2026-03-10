// src/pages/customer/HF4.jsx - Product Confirmation Screen
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./HF4.css";
import logo from "../../assets/logo.png";
import { FiMenu, FiPlus, FiMinus } from "react-icons/fi";
import { IoMdArrowBack } from "react-icons/io";
import { MdDelete } from "react-icons/md";
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

  const handleBack = () => {
    navigate("/detect-items");
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
      {/* Skin Color Header Bar */}
      <div className="hf4-header-bar">
        <button className="hf4-back-btn" onClick={handleBack}>
          <IoMdArrowBack />
        </button>
        <h2 className="hf4-heading">Product Confirmation</h2>
      </div>

      {/* Main Content */}
      <div className="hf4-content">
        {/* Left Column - Product Table */}
        <div className="hf4-left-section">
          <h3 className="section-title">Your Items</h3>
          <div className="products-table">
            <div className="table-header">
              <div className="header-cell">Product</div>
              <div className="header-cell">Unit Price</div>
              <div className="header-cell">Quantity</div>
              <div className="header-cell">Price</div>
              <div className="header-cell">Action</div>
            </div>

            <div className="table-body">
              {items.length === 0 ? (
                <p style={{ textAlign: 'center', padding: '20px', color: '#888' }}>
                  No items in cart
                </p>
              ) : (
                items.map((item) => (
                  <div key={item.id} className="table-row">
                    <div className="product-cell">
                      <div className="product-image">🛒</div>
                      <span className="product-name">{item.name}</span>
                    </div>
                    <div className="cell">Rs {item.price.toFixed(2)}</div>
                    <div className="cell quantity-cell">
                      <button
                        className="qty-btn"
                        onClick={() => updateQuantity(item.id, -1)}
                      >
                        <FiMinus />
                      </button>
                      <span className="qty-value">{item.quantity}</span>
                      <button
                        className="qty-btn"
                        onClick={() => updateQuantity(item.id, 1)}
                      >
                        <FiPlus />
                      </button>
                    </div>
                    <div className="cell price-cell">
                      Rs {(item.price * item.quantity).toFixed(2)}
                    </div>
                    <div className="cell action-cell">
                      <button
                        className="remove-btn"
                        onClick={() => removeItem(item.id)}
                      >
                        <MdDelete /> Remove
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Column - Order Summary */}
        <div className="hf4-right-section">
          <div className="cart-image">🛒</div>
          <h3 className="summary-title">Order Summary</h3>

          <div className="summary-details">
            <div className="summary-row">
              <span>Subtotal:</span>
              <span>Rs {getSubtotal()}</span>
            </div>
            <div className="summary-row">
              <span>Tax (10%):</span>
              <span>Rs {getTax()}</span>
            </div>
            <div className="summary-row total-row">
              <span>Total:</span>
              <span>Rs {getTotal()}</span>
            </div>
          </div>

          <button
            className="action-btn weight-btn"
            onClick={handleWeightVerification}
            disabled={items.length === 0}
          >
            Weight Verification
          </button>
          <button className="action-btn find-btn" onClick={handleFindItems}>
            Find Items
          </button>
        </div>
      </div>
    </div>
  );
}

export default HF4;
