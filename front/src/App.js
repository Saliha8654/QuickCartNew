import React from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import HF0 from "./pages/customer/HF0";
import HF1 from "./pages/customer/HF1";
import HF2 from "./pages/customer/HF2";
import HF3 from "./pages/customer/HF3";
import HF4 from "./pages/customer/HF4";
import HF5 from "./pages/customer/HF5";
import HF6 from "./pages/customer/HF6";
import HF7 from "./pages/customer/HF7";
import StripePayment from "./pages/customer/StripePayment";
import Admin1 from "./pages/admin/Admin1";
import Admin2 from "./pages/admin/Admin2";
import Admin3 from "./pages/admin/Admin3";
import Admin4 from "./pages/admin/Admin4";
import Admin5 from "./pages/admin/Admin5";
import Admin6 from "./pages/admin/Admin6";
import AdminAssistance from "./pages/admin/AdminAssistance";
import TopNav from "./components/TopNav";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Customer Routes */}
        {/* HF0 - Home Screen (no TopNav) */}
        <Route path="/" element={<><TopNav /><HF0 /></>} />
        
        {/* HF1 - Place Item Screen (no TopNav) */}
        <Route path="/place-item" element={<><TopNav /><HF1 /></>} />
        
        {/* HF2 - Detect Items Screen (has its own top bar) */}
        <Route path="/detect-items" element={<><TopNav /><HF2 /></>} />
        
        {/* HF3 - Find Products Screen (has its own top bar) */}
        <Route path="/find-products" element={<><TopNav /><HF3 /></>} />
        
        {/* HF4 - Product Confirmation Screen (first bar only, back arrow on top nav) */}
        <Route path="/product-confirmation" element={<><TopNav showBack backPath="/detect-items" title="quickcart" /><HF4 /></>} />
        
        {/* HF5 - Weight Verification Screen (first bar only, back arrow on top nav) */}
        <Route path="/weight-verification" element={<><TopNav showBack backPath="/product-confirmation" title="quickcart" /><HF5 /></>} />
        
        {/* HF6 - Payment Selection Screen (first bar only, back arrow on top nav) */}
        <Route path="/payment-selection" element={<><TopNav showBack backPath="/weight-verification" title="quickcart" /><HF6 /></>} />
        
        {/* Stripe Payment Screen (first bar only, back arrow on top nav) */}
        <Route path="/stripe-payment" element={<><TopNav showBack backPath="/payment-selection" title="quickcart" /><StripePayment /></>} />
        
        {/* HF7 - Receipt Screen (has its own top bar) */}
        <Route path="/receipt" element={<><TopNav /><HF7 /></>} />

        {/* Admin Routes */}
        {/* Admin1 - Admin Home Screen */}
        <Route path="/admin" element={<Admin1 />} />
        
        {/* Admin2 - Admin Login Screen */}
        <Route path="/admin/login" element={<Admin2 />} />
        
        {/* Admin3 - Admin Signup Screen */}
        <Route path="/admin/signup" element={<Admin3 />} />
        
        {/* Admin4 - Admin Dashboard (Metrics) */}
        <Route path="/admin/dashboard" element={<Admin4 />} />
        <Route path="/admin/4" element={<Navigate to="/admin/dashboard" replace />} />
        
        {/* Admin5 - Product Inventory */}
        <Route path="/admin/inventory" element={<Admin5 />} />
        <Route path="/admin/5" element={<Navigate to="/admin/inventory" replace />} />
        
        {/* Admin6 - Transaction History */}
        <Route path="/admin/transactions" element={<Admin6 />} />
        <Route path="/admin/6" element={<Navigate to="/admin/transactions" replace />} />
        
        {/* AdminAssistance - Help & Support */}
        <Route path="/admin/assistance" element={<AdminAssistance />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
