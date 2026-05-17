import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import AdminMenu from "./AdminMenu";
import "./Admin5.css";

function Admin5() {
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [formData, setFormData] = useState({
    class_id: "",
    name: "",
    price: "",
    inventory: "",
    expected_weight_g: "",
    barcode: "",
    image_url: ""
  });

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const token = localStorage.getItem("adminToken");
      if (!token) {
        navigate("/admin/login");
        return;
      }

      const response = await axios.get("http://localhost:5000/api/admin/products", {
        headers: { Authorization: `Bearer ${token}` }
      });

      setProducts(response.data.products);
      setLoading(false);
    } catch (err) {
      console.error("Failed to fetch products:", err);
      if (err.response?.status === 401) {
        localStorage.removeItem("adminToken");
        localStorage.removeItem("adminData");
        navigate("/admin/login");
      }
      setLoading(false);
    }
  };

  const handleAdd = async () => {
    try {
      const token = localStorage.getItem("adminToken");
      await axios.post("http://localhost:5000/api/admin/products", formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setShowAddForm(false);
      resetForm();
      fetchProducts();
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem("adminToken");
        localStorage.removeItem("adminData");
        navigate("/admin/login");
        return;
      }
      alert("Failed to add product: " + (err.response?.data?.error || err.message));
    }
  };

  const handleEdit = async () => {
    try {
      const token = localStorage.getItem("adminToken");
      await axios.put(`http://localhost:5000/api/admin/products/${editingProduct.id}`, formData, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setEditingProduct(null);
      resetForm();
      fetchProducts();
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem("adminToken");
        localStorage.removeItem("adminData");
        navigate("/admin/login");
        return;
      }
      alert("Failed to update product: " + (err.response?.data?.error || err.message));
    }
  };

  const handleDelete = async (productId) => {
    if (!window.confirm("Are you sure you want to delete this product?")) return;

    try {
      const token = localStorage.getItem("adminToken");
      await axios.delete(`http://localhost:5000/api/admin/products/${productId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      fetchProducts();
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem("adminToken");
        localStorage.removeItem("adminData");
        navigate("/admin/login");
        return;
      }
      alert("Failed to delete product: " + (err.response?.data?.error || err.message));
    }
  };

  const openEditForm = (product) => {
    setEditingProduct(product);
    setFormData({
      class_id: product.class_id,
      name: product.name,
      price: product.price,
      inventory: product.inventory,
      expected_weight_g: product.expected_weight_g || "",
      barcode: product.barcode || "",
      image_url: product.image_url || ""
    });
  };

  const resetForm = () => {
    setFormData({
      class_id: "",
      name: "",
      price: "",
      inventory: "",
      expected_weight_g: "",
      barcode: "",
      image_url: ""
    });
  };

  return (
    <div className="admin5-container">
      {/* Top Blue Bar */}
      <div className="admin5-top-bar">
        <div className="admin5-logo">
          <h2 className="logo-small">QUICK</h2>
          <h2 className="logo-small-cart">CART</h2>
        </div>
        <div className="admin5-menu-icon" onClick={() => setMenuOpen(true)}>
          <div className="menu-line"></div>
          <div className="menu-line"></div>
          <div className="menu-line"></div>
        </div>
      </div>

      {/* Yellow Bar */}
      <div className="admin5-yellow-bar">
        <span className="admin5-back-arrow" onClick={() => navigate(-1)}>←</span>
        <h3 className="admin5-yellow-heading">Product Inventory</h3>
      </div>

      {/* Welcome Heading */}
      <h2 className="admin5-welcome">Welcome to Admin Dashboard</h2>

      {/* Product Table */}
      {loading ? (
        <p className="admin5-loading">Loading products...</p>
      ) : (
        <div className="admin5-table-container">
          <table className="admin5-table">
            <thead>
              <tr>
                <th>Product ID</th>
                <th>Product Name</th>
                <th>Price</th>
                <th>Stock</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {products.map((product) => (
                <tr key={product.id}>
                  <td>{product.class_id}</td>
                  <td>{product.name}</td>
                  <td>Rs {product.price}</td>
                  <td>{product.inventory}</td>
                  <td className="admin5-actions">
                    <button className="admin5-edit-btn" onClick={() => openEditForm(product)}>Edit</button>
                    <button className="admin5-delete-btn" onClick={() => handleDelete(product.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Add Product Button */}
      <div className="admin5-add-container">
        <button className="admin5-add-btn" onClick={() => setShowAddForm(true)}>
          Add Product
        </button>
      </div>

      {/* Add/Edit Product Form Modal */}
      {(showAddForm || editingProduct) && (
        <div className="admin5-modal-overlay" onClick={() => { setShowAddForm(false); setEditingProduct(null); resetForm(); }}>
          <div className="admin5-modal" onClick={(e) => e.stopPropagation()}>
            <h3>{editingProduct ? "Edit Product" : "Add New Product"}</h3>
            <div className="admin5-form">
              <input
                type="number"
                placeholder="Class ID"
                value={formData.class_id}
                onChange={(e) => setFormData({ ...formData, class_id: e.target.value })}
              />
              <input
                type="text"
                placeholder="Product Name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
              <input
                type="number"
                placeholder="Price"
                value={formData.price}
                onChange={(e) => setFormData({ ...formData, price: e.target.value })}
              />
              <input
                type="number"
                placeholder="Stock Quantity"
                value={formData.inventory}
                onChange={(e) => setFormData({ ...formData, inventory: e.target.value })}
              />
              <input
                type="number"
                placeholder="Expected Weight (g)"
                value={formData.expected_weight_g}
                onChange={(e) => setFormData({ ...formData, expected_weight_g: e.target.value })}
              />
              <input
                type="text"
                placeholder="Barcode"
                value={formData.barcode}
                onChange={(e) => setFormData({ ...formData, barcode: e.target.value })}
              />
              <input
                type="text"
                placeholder="Image URL"
                value={formData.image_url}
                onChange={(e) => setFormData({ ...formData, image_url: e.target.value })}
              />
              <div className="admin5-form-buttons">
                <button onClick={() => { setShowAddForm(false); setEditingProduct(null); resetForm(); }}>
                  Cancel
                </button>
                <button onClick={editingProduct ? handleEdit : handleAdd}>
                  {editingProduct ? "Update" : "Add"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Blue Bar */}
      <div className="admin5-bottom-bar"></div>

      {/* Admin Menu */}
      <AdminMenu isOpen={menuOpen} onClose={() => setMenuOpen(false)} />
    </div>
  );
}

export default Admin5;
