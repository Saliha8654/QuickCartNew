// src/pages/customer/HF3.jsx - Find Products Screen
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./HF3.css";
import logo from "../../assets/logo.png";
import { FiMenu, FiSearch } from "react-icons/fi";
import { IoMdArrowBack } from "react-icons/io";
import { MdQrCodeScanner } from "react-icons/md";
import axios from "axios";

const API_URL = "http://localhost:5000/api";

function HF3() {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");
  const [cartItems, setCartItems] = useState([]);
  const [allProducts, setAllProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  // Fetch products from database
  useEffect(() => {
    fetchProducts();
  }, []);

  // Search products when search query changes (with debounce)
  useEffect(() => {
    // Debounce: wait 500ms after user stops typing before searching
    const timeoutId = setTimeout(() => {
      if (searchQuery) {
        searchProducts();
      } else {
        setSearchedProducts([]);
      }
    }, 500);

    // Cleanup: cancel the timeout if searchQuery changes before 500ms
    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/products`);
      setAllProducts(response.data);
    } catch (error) {
      console.error("Error fetching products:", error);
      // Show user-friendly error message
      alert("Failed to load products. Please make sure the backend server is running.");
    } finally {
      setLoading(false);
    }
  };

  const [searchedProducts, setSearchedProducts] = useState([]);

  const searchProducts = async () => {
    if (!searchQuery.trim()) {
      setSearchedProducts([]);
      return;
    }

    setLoading(true);
    try {
      // Search by name OR barcode
      const response = await axios.get(`${API_URL}/products?q=${searchQuery}`);
      setSearchedProducts(response.data);
    } catch (error) {
      console.error("Error searching products:", error);
      setSearchedProducts([]);
    } finally {
      setLoading(false);
    }
  };

  const addToBag = (product) => {
    const existingItem = cartItems.find((item) => item.id === product.id);
    if (existingItem) {
      setCartItems(
        cartItems.map((item) =>
          item.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        )
      );
    } else {
      setCartItems([...cartItems, { ...product, quantity: 1 }]);
    }
  };

  const addToCart = async (product) => {
    try {
      // Add to backend cart
      await axios.post(`${API_URL}/cart`, {
        product_id: product.id,
        quantity: 1
      });
      
      // Add to local cart
      addToBag(product);
      
      // Show success feedback
      console.log(`Added ${product.name} to cart`);
    } catch (error) {
      console.error("Error adding to cart:", error);
      alert("Failed to add item to cart. Please try again.");
    }
  };

  const getTotalPrice = () => {
    return cartItems
      .reduce((total, item) => total + item.price * item.quantity, 0)
      .toFixed(2);
  };

  const handleBack = () => {
    navigate("/detect-items");
  };

  const handleScanItems = () => {
    navigate("/detect-items");
  };

  const handleProceedToCheckout = () => {
    navigate("/product-confirmation", { state: { items: cartItems } });
  };

  return (
    <div className="hf3">
      {/* Skin Color Header Bar */}
      <div className="hf3-header-bar">
        <button className="hf3-back-btn" onClick={handleBack}>
          <IoMdArrowBack />
        </button>
        <h2 className="hf3-heading">Find Products</h2>
      </div>

      {/* Search Bar Section */}
      <div className="hf3-search-section">
        <div className="search-input-wrapper">
          <FiSearch className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Search for products..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <button className="scan-items-btn" onClick={handleScanItems}>
          <MdQrCodeScanner /> Scan Items
        </button>
      </div>

      {/* Main Content */}
      <div className="hf3-content">
        {/* Left Side - Search Results */}
        <div className="hf3-left-section">
          {!searchQuery && (
            <div className="search-placeholder">
              <div className="search-image">🔍</div>
              <p>Search for items you missed</p>
              {loading && <p>Loading products...</p>}
            </div>
          )}

          {searchQuery && searchedProducts.length === 0 && !loading && (
            <div className="no-results">
              <p>No products found</p>
            </div>
          )}

          {searchedProducts.length > 0 && (
            <div className="products-list">
              {searchedProducts.map((product) => (
                <div key={product.id} className="product-card">
                  <div className="product-image-placeholder">🛒</div>
                  <div className="product-info">
                    <h4 className="product-name">{product.name || 'Unnamed Product'}</h4>
                    <p className="product-category">Category: {product.class_id !== undefined ? `Class ${product.class_id}` : 'Uncategorized'}</p>
                    <p className="product-price">Rs {product.price !== undefined ? product.price.toFixed(2) : '0.00'}</p>
                  </div>
                  <button
                    className="add-to-bag-btn"
                    onClick={() => addToCart(product)}
                  >
                    Add to Bag
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right Side - Cart */}
        <div className="hf3-right-section">
          <h3 className="cart-title">Your Bag</h3>
          
          {cartItems.length === 0 ? (
            <div className="empty-cart">
              <p>No items in bag</p>
            </div>
          ) : (
            <>
              <div className="cart-items-list">
                {cartItems.map((item) => (
                  <div key={item.id} className="cart-item">
                    <div className="cart-item-info">
                      <div className="cart-item-image">🛒</div>
                      <div>
                        <p className="cart-item-name">{item.name}</p>
                        <p className="cart-item-quantity">Qty: {item.quantity}</p>
                        <p className="cart-item-price">Rs {item.price !== undefined ? (item.price * item.quantity).toFixed(2) : '0.00'}</p>
                      </div>
                    </div>
                    <p className="cart-item-price">
                      Rs {(item.price * item.quantity).toFixed(2)}
                    </p>
                  </div>
                ))}
              </div>

              <div className="cart-total">
                <h3>Total:</h3>
                <h3>Rs {getTotalPrice()}</h3>
              </div>

              <button className="proceed-btn" onClick={handleProceedToCheckout}>
                Proceed to Checkout
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default HF3;
