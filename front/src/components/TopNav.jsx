// src/components/TopNav.jsx
import React, { useState } from "react";
import "./TopNav.css";
import { FiMenu } from "react-icons/fi";
import { IoMdClose } from "react-icons/io";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const API_URL = "http://localhost:5000/api";

function TopNav({ showLogo = false, logo = null }) {
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();

  const toggleMenu = () => {
    setMenuOpen(!menuOpen);
  };

  const handleFindItems = () => {
    setMenuOpen(false);
    navigate("/find-products");
  };

  const handleRemoveItems = async () => {
    if (window.confirm("Are you sure you want to remove all items from the cart?")) {
      try {
        // Get all cart items
        const response = await axios.get(`${API_URL}/cart`);
        const items = response.data.items || [];
        
        // Delete each item
        for (const item of items) {
          await axios.delete(`${API_URL}/cart/${item.id}`);
        }
        
        alert("All items removed from cart");
        setMenuOpen(false);
        // Optionally reload the page or update state
        window.location.reload();
      } catch (error) {
        console.error("Error removing items:", error);
        alert("Failed to remove items. Please try again.");
      }
    }
  };

  return (
    <>
      <div className="topnav">
        {showLogo && logo && (
          <div className="topnav-logo">
            <img src={logo} alt="Logo" />
          </div>
        )}
        <button className="menu-btn" onClick={toggleMenu}>
          <FiMenu className="menu-icon" />
        </button>
      </div>

      {/* Menu Sidebar */}
      {menuOpen && (
        <>
          <div className="menu-overlay" onClick={toggleMenu}></div>
          <div className="menu-sidebar">
            <button className="close-menu" onClick={toggleMenu}>
              <IoMdClose />
            </button>
            <div className="menu-options">
              <button className="menu-option" onClick={() => { setMenuOpen(false); /* Leave other options as is */ }}>
                Assistance
              </button>
              <button className="menu-option" onClick={handleFindItems}>
                Find Items
              </button>
              <button className="menu-option" onClick={handleRemoveItems}>
                Remove Items
              </button>
              <button className="menu-option" onClick={() => { setMenuOpen(false); /* Leave other options as is */ }}>
                Add Your Own Bag
              </button>
            </div>
          </div>
        </>
      )}
    </>
  );
}

export default TopNav;
