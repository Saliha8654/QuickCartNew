import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import AdminMenu from "./AdminMenu";
import "./AdminAssistance.css";

function AdminAssistance() {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <div className="admin-assistance-container">
      {/* Top Blue Bar */}
      <div className="admin-assistance-top-bar">
        <div className="admin-assistance-logo">
          <h2 className="logo-small">QUICK</h2>
          <h2 className="logo-small-cart">CART</h2>
        </div>
        <div className="admin-assistance-menu-icon" onClick={() => setMenuOpen(true)}>
          <div className="menu-line"></div>
          <div className="menu-line"></div>
          <div className="menu-line"></div>
        </div>
      </div>

      {/* Yellow Bar */}
      <div className="admin-assistance-yellow-bar">
        <span className="admin-assistance-back-arrow" onClick={() => navigate(-1)}>←</span>
        <h3 className="admin-assistance-yellow-heading">Assistance</h3>
      </div>

      {/* Content */}
      <div className="admin-assistance-content">
        <h2>Admin Help & Support</h2>
        <div className="admin-assistance-card">
          <h3>📊 Record Metrics</h3>
          <p>View real-time sales data, daily transactions, low stock alerts, and active users.</p>
        </div>
        <div className="admin-assistance-card">
          <h3>📦 Product Inventory</h3>
          <p>Manage products, update prices, stock levels, and add new items to the inventory.</p>
        </div>
        <div className="admin-assistance-card">
          <h3>💳 Transaction History</h3>
          <p>Track all transactions, filter by date or amount, and monitor payment statuses.</p>
        </div>
        <div className="admin-assistance-card">
          <h3>📞 Contact Support</h3>
          <p>For technical assistance, contact: support@quickcart.com</p>
        </div>
      </div>

      {/* Bottom Blue Bar */}
      <div className="admin-assistance-bottom-bar"></div>

      {/* Admin Menu */}
      <AdminMenu isOpen={menuOpen} onClose={() => setMenuOpen(false)} />
    </div>
  );
}

export default AdminAssistance;
