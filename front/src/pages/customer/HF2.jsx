// src/pages/customer/HF2.jsx - Detect Items Screen
import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import "./HF2.css";
import logo from "../../assets/logo.png";
import { FiMenu, FiPlus, FiMinus } from "react-icons/fi";
import { IoMdArrowBack } from "react-icons/io";
import axios from "axios";

const API_URL = "http://localhost:5000/api";

function HF2() {
  const navigate = useNavigate();
  const [detectedItems, setDetectedItems] = useState([]);
  const [isDetecting, setIsDetecting] = useState(false);
  const [isCameraOn, setIsCameraOn] = useState(true);
  const [lastDetectionTime, setLastDetectionTime] = useState(0);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const streamRef = useRef(null);
  const detectionIntervalRef = useRef(null);

  // Start camera stream when component mounts
  useEffect(() => {
    if (isCameraOn) {
      startCamera();
    }
    return () => {
      stopCamera();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isCameraOn]);

  const startCamera = async () => {
    if (streamRef.current) {
      // Camera is already on
      return;
    }
    
    try {
      // Try different constraints for better browser compatibility
      const constraints = {
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user' // Prefer front camera
        }
      };
      
      // Use browser's getUserMedia to access webcam
      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
      }
      
      // Start periodic detection every 5 seconds instead of 1 second
      startPeriodicDetection();
    } catch (err) {
      console.error("Error accessing camera:", err);
      
      // Try with simpler constraints
      try {
        const fallbackConstraints = { video: { width: 640, height: 480 } };
        const stream = await navigator.mediaDevices.getUserMedia(fallbackConstraints);
        
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          streamRef.current = stream;
        }
        
        startPeriodicDetection();
      } catch (fallbackErr) {
        console.error("Fallback camera access failed:", fallbackErr);
        alert("Unable to access camera. Please grant camera permissions and ensure you're using a supported browser.");
      }
    }
  };

  const stopCamera = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    if (detectionIntervalRef.current) {
      clearInterval(detectionIntervalRef.current);
      detectionIntervalRef.current = null;
    }
  };

  const toggleCamera = () => {
    const newCameraState = !isCameraOn;
    setIsCameraOn(newCameraState);
    
    if (newCameraState) {
      // Turn camera on
      startCamera();
    } else {
      // Turn camera off
      stopCamera();
    }
  };

  const startPeriodicDetection = () => {
    // Run detection every 5 seconds instead of 1 second to reduce frequency
    detectionIntervalRef.current = setInterval(() => {
      captureAndDetect();
    }, 5000);
  };

  const captureAndDetect = async () => {
    if (!videoRef.current || isDetecting) return;
    
    // Throttle detection to prevent too frequent calls
    const now = Date.now();
    if (now - lastDetectionTime < 5000) { // Increase minimum time between detections to 5 seconds
      return;
    }
    
    setIsDetecting(true);
    setLastDetectionTime(now);
    
    // Show scanning indicator
    const canvas = canvasRef.current;
    const video = videoRef.current;
    if (canvas && video) {
      const ctx = canvas.getContext('2d');
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      // Draw scanning border
      ctx.strokeStyle = '#00ff00';
      ctx.lineWidth = 5;
      ctx.setLineDash([10, 5]);
      ctx.strokeRect(5, 5, canvas.width - 10, canvas.height - 10);
      ctx.setLineDash([]);
      
      // Draw scanning text
      ctx.fillStyle = 'rgba(0, 255, 0, 0.8)';
      ctx.fillRect(20, 20, 150, 40);
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 18px Arial';
      ctx.fillText('Scanning...', 30, 45);
    }
    
    try {
      // Capture current frame from video
      const canvas = canvasRef.current;
      const video = videoRef.current;
      
      if (!canvas || !video) {
        setIsDetecting(false);
        return;
      }
      
      canvas.width = 640;
      canvas.height = 480;
      const ctx = canvas.getContext('2d');
      ctx.drawImage(video, 0, 0);
      
      // Convert canvas to blob
      canvas.toBlob(async (blob) => {
        if (!blob) {
          setIsDetecting(false);
          return;
        }
        
        // Send to backend for detection
        const formData = new FormData();
        formData.append('image', blob, 'frame.jpg');
        
        try {
          const response = await axios.post(`${API_URL}/detect`, formData, {
            headers: { 'Content-Type': 'multipart/form-data' },
            timeout: 30000 // 5 second timeout
          });
          
          if (response.data.detections && response.data.detections.length > 0) {
            console.log(`✅ DETECTIONS FOUND: ${response.data.detections.length}`, response.data.detections);
            
            // Draw bounding boxes on canvas
            drawBoundingBoxes(response.data.detections, video.videoWidth, video.videoHeight);
            
            // Add ALL detected items - each detection adds quantity 1
            let addedCount = 0;
            response.data.detections.forEach(det => {
              if (det.product) {
                addDetectedItem(det.product);
                addedCount++;
              }
            });
            
            // Show visual feedback for all detections
            if (addedCount > 0) {
              showDetectionFeedback(addedCount);
              console.log(`Detected ${addedCount} item(s) - added with quantity 1 each`);
            }
          } else {
            console.log('NO DETECTIONS - Backend returned 0 objects');
            console.log('Response:', response.data);
                    
            // Draw "NO DETECTION" message on canvas
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    
            // Draw red border to indicate scanning but no detection
            ctx.strokeStyle = '#ff6b6b';
            ctx.lineWidth = 5;
            ctx.strokeRect(5, 5, canvas.width - 10, canvas.height - 10);
                    
            // Draw message
            ctx.fillStyle = 'rgba(255, 107, 107, 0.8)';
            ctx.fillRect(20, canvas.height - 60, canvas.width - 40, 40);
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText('Scanning... No products detected', canvas.width / 2, canvas.height - 35);
          }
        } catch (error) {
          console.error("Detection API error:", error);
          // Clear canvas on error
          const ctx = canvas.getContext('2d');
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        }
        
        setIsDetecting(false);
      }, 'image/jpeg', 0.5); // JPEG quality set to 0.8 for better performance
      
    } catch (error) {
      console.error("Detection error:", error);
      setIsDetecting(false);
    }
  };

  const showDetectionFeedback = (count) => {
    // Create a temporary visual indicator
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Draw a semi-transparent overlay
    ctx.fillStyle = 'rgba(0, 255, 0, 0.3)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw detection count text
    ctx.font = 'bold 24px Arial';
    ctx.fillStyle = '#ffffff';
    ctx.textAlign = 'center';
    ctx.fillText(`Detected ${count} item${count > 1 ? 's' : ''}!`, canvas.width / 2, canvas.height / 2);
    
    // Remove the overlay after a short delay
    setTimeout(() => {
      const video = videoRef.current;
      if (video) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      }
    }, 500);
  };

  const drawBoundingBoxes = (detections, videoWidth, videoHeight) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Redraw the video frame
    const video = videoRef.current;
    if (video) {
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    }
    
    // Draw bounding boxes for all detections
    detections.forEach((detection, index) => {
      if (detection.bbox && detection.bbox.length === 4) {
        const [x1, y1, x2, y2] = detection.bbox;
        
        // Scale coordinates to canvas size
        const scaleX = canvas.width / videoWidth;
        const scaleY = canvas.height / videoHeight;
        
        const scaledX1 = x1 * scaleX;
        const scaledY1 = y1 * scaleY;
        const scaledX2 = x2 * scaleX;
        const scaledY2 = y2 * scaleY;
        
        // Draw rectangle with different colors for each detection
        const colors = ['#00ff00', '#ff0000', '#0000ff', '#ffff00', '#ff00ff', '#00ffff'];
        const color = colors[index % colors.length];
        
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        // Draw the full bounding box (ensure it covers the complete detection area)
        ctx.strokeRect(scaledX1, scaledY1, scaledX2 - scaledX1, scaledY2 - scaledY1);
        
        // Draw corner markers for better visibility
        const cornerSize = 15;
        ctx.beginPath();
        
        // Top-left corner
        ctx.moveTo(scaledX1, scaledY1);
        ctx.lineTo(scaledX1 + cornerSize, scaledY1);
        ctx.moveTo(scaledX1, scaledY1);
        ctx.lineTo(scaledX1, scaledY1 + cornerSize);
        
        // Top-right corner
        ctx.moveTo(scaledX2, scaledY1);
        ctx.lineTo(scaledX2 - cornerSize, scaledY1);
        ctx.moveTo(scaledX2, scaledY1);
        ctx.lineTo(scaledX2, scaledY1 + cornerSize);
        
        // Bottom-left corner
        ctx.moveTo(scaledX1, scaledY2);
        ctx.lineTo(scaledX1 + cornerSize, scaledY2);
        ctx.moveTo(scaledX1, scaledY2);
        ctx.lineTo(scaledX1, scaledY2 - cornerSize);
        
        // Bottom-right corner
        ctx.moveTo(scaledX2, scaledY2);
        ctx.lineTo(scaledX2 - cornerSize, scaledY2);
        ctx.moveTo(scaledX2, scaledY2);
        ctx.lineTo(scaledX2, scaledY2 - cornerSize);
        
        ctx.strokeStyle = color;
        ctx.lineWidth = 3;
        ctx.stroke();
        
        // Draw label background
        if (detection.product) {
          const label = `${detection.product.name} (${Math.round(detection.score * 100)}%)`;
          ctx.font = 'bold 14px Arial';
          const textWidth = ctx.measureText(label).width;
          
          // Background rectangle for label
          ctx.fillStyle = color;
          ctx.fillRect(scaledX1, scaledY1 - 20, textWidth + 10, 20);
          
          // Label text
          ctx.fillStyle = '#ffffff';
          ctx.fillText(label, scaledX1 + 5, scaledY1 - 5);
        }
      }
    });
  };

  const addDetectedItem = (product) => {
    setDetectedItems((prevItems) => {
      const existingItem = prevItems.find(item => item.id === product.id);
      
      if (existingItem) {
        // Item already in list - do nothing, user will manually adjust quantity
        console.log(`Product "${product.name}" already in list - skipping`);
        return prevItems; // Don't add again
      } else {
        // New item detected - add with quantity 1
        console.log(`New product detected: "${product.name}" - added with quantity 1`);
        return [...prevItems, {
          id: product.id,
          name: product.name,
          price: product.price,
          quantity: 1,
          image_url: product.image_url
        }];
      }
    });
  };

  const updateQuantity = (id, change) => {
    setDetectedItems((items) =>
      items.map((item) =>
        item.id === id
          ? { ...item, quantity: Math.max(0, item.quantity + change) }
          : item
      ).filter(item => item.quantity > 0)
    );
  };

  const getTotalPrice = () => {
    return detectedItems.reduce(
      (total, item) => total + item.price * item.quantity,
      0
    ).toFixed(2);
  };

  const handleProceedToCheckout = async () => {
    // Add all items to cart before proceeding
    try {
      for (const item of detectedItems) {
        await axios.post(`${API_URL}/cart`, {
          product_id: item.id,
          quantity: item.quantity
        });
      }
      navigate("/product-confirmation", { state: { items: detectedItems } });
    } catch (error) {
      console.error("Error adding to cart:", error);
      alert("Failed to add items to cart. Please try again.");
    }
  };

  const handleSearchManually = () => {
    navigate("/find-products");
  };

  const handleBack = () => {
    navigate("/place-item");
  };

  return (
    <div className="hf2">
      {/* Header Bar */}
      <div className="hf2-header-bar">
        <button className="hf2-back-btn" onClick={handleBack}>
          <IoMdArrowBack />
        </button>
        <h2 className="hf2-heading">Detect Items</h2>
      </div>

      {/* Main Content */}
      <div className="hf2-content">
        {/* Left Side - Camera Detection */}
        <div className="hf2-left-section">
          <div className="hf2-camera-box">
            <div className="camera-box-header">
              <div className="camera-badge">
                <span className="badge-dot"></span>
                <p className="camera-label">Live Camera Scan</p>
              </div>
              <div className="camera-controls">
                <button
                  type="button"
                  className={`camera-toggle-btn ${isCameraOn ? 'on' : 'off'}`}
                  onClick={toggleCamera}
                >
                  {isCameraOn ? 'Camera ON' : 'Camera OFF'}
                </button>
              </div>
            </div>
            <div className="camera-placeholder">
              <video 
                ref={videoRef} 
                autoPlay 
                playsInline
                style={{
                  width: '100%',
                  height: '100%',
                  objectFit: 'cover',
                  borderRadius: '12px'
                }}
              />
              <canvas 
                ref={canvasRef} 
                style={{ 
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  width: '100%',
                  height: '100%',
                  borderRadius: '12px'
                }} 
              />
            </div>
            <div className="camera-status">
              <p>{isDetecting ? '🔍 Detecting...' : '✓ Ready'}</p>
            </div>
          </div>

          <div className="hf2-manual-search">
            <p className="manual-search-text">
              Didn't find what you're looking for?
            </p>
            <button className="search-btn" onClick={handleSearchManually}>
              Search Manually
            </button>
          </div>
        </div>

        {/* Right Side - Detected Items List */}
        <div className="hf2-right-section">
          <div className="detected-items-header">
            <h3 className="detected-items-title">🛒 Detected Items</h3>
            <span className="items-count">{detectedItems.length} item{detectedItems.length !== 1 ? 's' : ''}</span>
          </div>
          <div className="detected-items-list">
            {detectedItems.length === 0 ? (
              <div className="empty-state">
                <p className="empty-state-icon">📦</p>
                <p className="empty-state-text">No items detected yet</p>
                <p className="empty-state-hint">Place items in camera view</p>
              </div>
            ) : (
              detectedItems.map((item) => (
                <div key={item.id} className="detected-item">
                  <div className="item-info">
                    <div className="item-image-placeholder">🛒</div>
                    <div className="item-details">
                      <p className="item-name">{item.name}</p>
                      <p className="item-price">Rs {item.price.toFixed(2)}</p>
                    </div>
                  </div>
                  <div className="item-actions">
                    <div className="item-quantity">
                      <button
                        className="quantity-btn"
                        onClick={() => updateQuantity(item.id, -1)}
                      >
                        <FiMinus />
                      </button>
                      <span className="quantity-value">{item.quantity}</span>
                      <button
                        className="quantity-btn"
                        onClick={() => updateQuantity(item.id, 1)}
                      >
                        <FiPlus />
                      </button>
                    </div>
                    <p className="item-total">
                      Rs {(item.price * item.quantity).toFixed(2)}
                    </p>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Total Price */}
          <div className="total-section">
            <div className="total-row">
              <h3 className="total-label">Total:</h3>
              <h3 className="total-price">Rs {getTotalPrice()}</h3>
            </div>
          </div>

          {/* Proceed to Checkout Button */}
          <button 
            className="proceed-btn" 
            onClick={handleProceedToCheckout}
            disabled={detectedItems.length === 0}
          >
            Proceed to Checkout
          </button>
        </div>
      </div>
    </div>
  );
}

export default HF2;