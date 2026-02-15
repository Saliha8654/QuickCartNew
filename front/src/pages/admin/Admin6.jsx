import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import AdminMenu from "./AdminMenu";
import "./Admin6.css";

function Admin6() {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("date_desc");
  const [showFilter, setShowFilter] = useState(false);

  useEffect(() => {
    fetchTransactions();
  }, [sortBy]);

  const fetchTransactions = async () => {
    try {
      const token = localStorage.getItem("adminToken");
      if (!token) {
        navigate("/admin/login");
        return;
      }

      const response = await axios.get(
        `http://localhost:5000/api/admin/transactions?search=${searchTerm}&sort_by=${sortBy}`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      setTransactions(response.data.transactions);
      setLoading(false);
    } catch (err) {
      console.error("Failed to fetch transactions:", err);
      if (err.response?.status === 401) {
        navigate("/admin/login");
      }
      setLoading(false);
    }
  };

  const handleSearch = () => {
    fetchTransactions();
  };

  return (
    <div className="admin6-container">
      {/* Top Blue Bar */}
      <div className="admin6-top-bar">
        <div className="admin6-logo">
          <h2 className="logo-small">QUICK</h2>
          <h2 className="logo-small-cart">CART</h2>
        </div>
        <div className="admin6-menu-icon" onClick={() => setMenuOpen(true)}>
          <div className="menu-line"></div>
          <div className="menu-line"></div>
          <div className="menu-line"></div>
        </div>
      </div>

      {/* Yellow Bar */}
      <div className="admin6-yellow-bar">
        <span className="admin6-back-arrow" onClick={() => navigate(-1)}>←</span>
        <h3 className="admin6-yellow-heading">Transaction History</h3>
      </div>

      {/* Welcome Heading */}
      <h2 className="admin6-welcome">Welcome to Admin Dashboard</h2>

      {/* Search and Filter */}
      <div className="admin6-search-container">
        <div className="admin6-search-bar">
          <input
            type="text"
            placeholder="Search by Transaction ID..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch}>Search</button>
        </div>
        <button className="admin6-filter-btn" onClick={() => setShowFilter(!showFilter)}>
          ☰ Filter
        </button>
      </div>

      {/* Filter Dropdown */}
      {showFilter && (
        <div className="admin6-filter-dropdown">
          <button onClick={() => { setSortBy("date_desc"); setShowFilter(false); }}>
            Date (Newest First)
          </button>
          <button onClick={() => { setSortBy("date_asc"); setShowFilter(false); }}>
            Date (Oldest First)
          </button>
          <button onClick={() => { setSortBy("amount_desc"); setShowFilter(false); }}>
            Amount (High to Low)
          </button>
          <button onClick={() => { setSortBy("amount_asc"); setShowFilter(false); }}>
            Amount (Low to High)
          </button>
        </div>
      )}

      {/* Transaction Table */}
      {loading ? (
        <p className="admin6-loading">Loading transactions...</p>
      ) : (
        <div className="admin6-table-container">
          <table className="admin6-table">
            <thead>
              <tr>
                <th>Transaction ID</th>
                <th>Amount</th>
                <th>Payment</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {transactions.length === 0 ? (
                <tr>
                  <td colSpan="4" style={{ textAlign: 'center', padding: '40px' }}>
                    No transactions found
                  </td>
                </tr>
              ) : (
                transactions.map((transaction) => (
                  <tr key={transaction.id}>
                    <td>T{transaction.id}</td>
                    <td>Rs {transaction.total_amount.toFixed(2)}</td>
                    <td>{transaction.payment_method || "N/A"}</td>
                    <td>
                      <span className={`admin6-status admin6-status-${transaction.payment_status}`}>
                        {transaction.payment_status || "pending"}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      {/* Bottom Blue Bar */}
      <div className="admin6-bottom-bar"></div>

      {/* Admin Menu */}
      <AdminMenu isOpen={menuOpen} onClose={() => setMenuOpen(false)} />
    </div>
  );
}

export default Admin6;
