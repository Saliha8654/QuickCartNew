import React from "react";
import { useNavigate } from "react-router-dom";
import "./AdminMenu.css";

function AdminMenu({ isOpen, onClose }) {
  const navigate = useNavigate();

  const go = (path) => {
    if (onClose) onClose();
    navigate(path);
  };

  const logout = () => {
    try {
      localStorage.removeItem("adminToken");
      localStorage.removeItem("adminData");
    } catch (e) {
      // ignore
    }
    if (onClose) onClose();
    navigate("/admin/login");
  };

  if (!isOpen) return null;

  return (
    <>
      <div className="admin-menu-overlay" onClick={onClose} />
      <div className="admin-menu">
        <button className="admin-menu-btn" onClick={() => go("/admin/dashboard")}
          type="button"
        >
          Record Metrics
        </button>

        <button className="admin-menu-btn" onClick={() => go("/admin/inventory")}
          type="button"
        >
          Products
        </button>

        <button className="admin-menu-btn" onClick={() => go("/admin/transactions")}
          type="button"
        >
          Transactions
        </button>

        <div className="admin-menu-logout">
          <button className="admin-menu-btn" onClick={logout} type="button">
            Logout
          </button>
        </div>
      </div>
    </>
  );
}

export default AdminMenu;

