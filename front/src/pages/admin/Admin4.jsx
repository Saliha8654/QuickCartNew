import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import AdminMenu from "./AdminMenu";
import "./Admin4.css";

function Admin4() {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const [metrics, setMetrics] = useState({
    total_sales: 0,
    daily_transactions: 0,
    low_stock_alerts: 0,
    active_users: 0
  });
  const [charts, setCharts] = useState({
    sales_by_day: [],
    top_products: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      const token = localStorage.getItem("adminToken");
      if (!token) {
        navigate("/admin/login");
        return;
      }

      const response = await axios.get("http://localhost:5000/api/admin/metrics", {
        headers: { Authorization: `Bearer ${token}` }
      });

      setMetrics(response.data.metrics);
      setCharts(response.data.charts);
      setLoading(false);
    } catch (err) {
      console.error("Failed to fetch metrics:", err);
      if (err.response?.status === 401) {
        localStorage.removeItem("adminToken");
        localStorage.removeItem("adminData");
        navigate("/admin/login");
      }
      setLoading(false);
    }
  };

  return (
    <div className="admin4-container">
      {/* Top Blue Bar */}
      <div className="admin4-top-bar">
        <div className="admin4-logo">
          <h2 className="logo-small">QUICK</h2>
          <h2 className="logo-small-cart">CART</h2>
        </div>
        <div className="admin4-menu-icon" onClick={() => setMenuOpen(true)}>
          <div className="menu-line"></div>
          <div className="menu-line"></div>
          <div className="menu-line"></div>
        </div>
      </div>

      {/* Yellow Bar with Back Arrow */}
      <div className="admin4-yellow-bar">
        <span className="admin4-back-arrow" onClick={() => navigate(-1)}>←</span>
        <h3 className="admin4-yellow-heading">Record Metrics</h3>
      </div>

      {/* Welcome Heading */}
      <h2 className="admin4-welcome">Welcome to Admin Dash Board</h2>

      {/* Metrics Table */}
      {loading ? (
        <p className="admin4-loading">Loading metrics...</p>
      ) : (
        <>
          <div className="admin4-metrics-table">
            <div className="admin4-table-header">
              <div className="admin4-table-cell">Metric</div>
              <div className="admin4-table-cell">Value</div>
            </div>
            <div className="admin4-table-row">
              <div className="admin4-table-cell">Total Sales</div>
              <div className="admin4-table-cell">Rs {metrics.total_sales.toLocaleString()}</div>
            </div>
            <div className="admin4-table-row">
              <div className="admin4-table-cell">Daily Transactions</div>
              <div className="admin4-table-cell">{metrics.daily_transactions}</div>
            </div>
            <div className="admin4-table-row">
              <div className="admin4-table-cell">Low Stock Alerts</div>
              <div className="admin4-table-cell">{metrics.low_stock_alerts} Products</div>
            </div>
            <div className="admin4-table-row">
              <div className="admin4-table-cell">Active Users</div>
              <div className="admin4-table-cell">{metrics.active_users}</div>
            </div>
          </div>

          {/* Charts Section */}
          <div className="admin4-charts">
            <div className="admin4-chart">
              <h4>Sales Distribution</h4>
              <div className="admin4-pie-chart">
                <div className="pie-slice" style={{ 
                  background: `conic-gradient(#003d5c ${(metrics.total_sales / (metrics.total_sales + 500000)) * 360}deg, #ffefc8 0deg)` 
                }}>
                  <div className="pie-center">
                    <span>{Math.round((metrics.total_sales / (metrics.total_sales + 500000)) * 100)}%</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="admin4-chart">
              <h4>Weekly Performance</h4>
              <div className="admin4-bar-chart">
                {charts.sales_by_day.slice(0, 7).reverse().map((day, idx) => {
                  const maxSales = Math.max(...charts.sales_by_day.map(d => d.sales), 1);
                  const height = (day.sales / maxSales) * 100;
                  return (
                    <div key={idx} className="bar-container">
                      <div className="bar" style={{ height: `${height}%`, backgroundColor: idx % 2 === 0 ? '#ffefc8' : '#003d5c' }}></div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </>
      )}

      {/* Bottom Blue Bar */}
      <div className="admin4-bottom-bar"></div>

      {/* Admin Menu */}
      <AdminMenu isOpen={menuOpen} onClose={() => setMenuOpen(false)} />
    </div>
  );
}

export default Admin4;
