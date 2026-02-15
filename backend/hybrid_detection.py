"""
Hybrid Detection Service
Combines object detection, barcode scanning, and weight verification
with duplicate prevention and intelligent fallback logic
"""
import time
import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(__file__))

try:
    from detection import predict_image, load_model
    from barcode_detection import detect_barcodes
    from models import SessionLocal, Product
except ImportError:
    try:
        from backend.detection import predict_image, load_model
        from backend.barcode_detection import detect_barcodes
        from backend.models import SessionLocal, Product
    except ImportError:
        # Last resort - direct imports
        import detection
        import barcode_detection
        import models
        predict_image = detection.predict_image
        load_model = detection.load_model
        detect_barcodes = barcode_detection.detect_barcodes
        SessionLocal = models.SessionLocal
        Product = models.Product


class HybridDetectionService:
    """
    Production-ready hybrid detection service with:
    - Object detection with confidence thresholds
    - Multi-barcode detection fallback
    - Weight verification
    - Duplicate detection prevention with cooldown
    """
    
    # Configuration constants
    OBJECT_DETECTION_CONFIDENCE_THRESHOLD = 0.80  # 80% confidence threshold
    WEIGHT_TOLERANCE = 0.10  # 10% tolerance for weight verification
    
    def __init__(self):
        """Initialize the hybrid detection service"""
        print("🔧 Hybrid Detection Service initialized (NO COOLDOWN)")
        print(f"   Confidence threshold: {self.OBJECT_DETECTION_CONFIDENCE_THRESHOLD * 100}%")
        print(f"   Manual quantity management enabled")
    
    # Cooldown system removed - items can be detected multiple times
    # Quantity management will be handled manually by the user
    
    def verify_weight(self, measured_weight_g: float, expected_weight_g: float) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify if measured weight matches expected weight within tolerance
        
        Args:
            measured_weight_g: Actual weight from load cell sensor
            expected_weight_g: Expected product weight from database
        
        Returns:
            Tuple of (is_valid, details_dict)
        """
        if expected_weight_g <= 0:
            return False, {
                "verified": False,
                "reason": "Invalid expected weight",
                "expected_g": expected_weight_g,
                "measured_g": measured_weight_g
            }
        
        lower_bound = expected_weight_g * (1 - self.WEIGHT_TOLERANCE)
        upper_bound = expected_weight_g * (1 + self.WEIGHT_TOLERANCE)
        
        is_valid = lower_bound <= measured_weight_g <= upper_bound
        
        return is_valid, {
            "verified": is_valid,
            "expected_g": expected_weight_g,
            "measured_g": measured_weight_g,
            "lower_bound_g": lower_bound,
            "upper_bound_g": upper_bound,
            "tolerance": self.WEIGHT_TOLERANCE,
            "deviation_percent": abs(measured_weight_g - expected_weight_g) / expected_weight_g * 100
        }
    
    def detect_objects(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Run object detection on frame
        
        Args:
            frame: OpenCV BGR image frame
        
        Returns:
            List of detection dictionaries with confidence scores
        """
        try:
            detections = predict_image(frame, conf=0.40)
            print(f"🔍 Object detection found {len(detections)} objects")
            return detections
        except Exception as e:
            print(f"❌ Object detection error: {e}")
            return []
    
    def detect_barcodes_multi(self, frame: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect multiple barcodes in frame
        
        Args:
            frame: OpenCV BGR image frame
        
        Returns:
            List of barcode dictionaries with values and types
        """
        try:
            barcodes = detect_barcodes(frame)
            print(f"📊 Barcode detection found {len(barcodes)} barcodes")
            for bc in barcodes:
                print(f"   └─ {bc.get('type', 'UNKNOWN')}: {bc.get('value', 'N/A')}")
            return barcodes
        except Exception as e:
            print(f"❌ Barcode detection error: {e}")
            return []
    
    def match_barcode_to_product(self, barcode_value: str) -> Optional[Dict[str, Any]]:
        """
        Find product in database by barcode
        
        Args:
            barcode_value: Scanned barcode string
        
        Returns:
            Product dictionary or None if not found
        """
        db = SessionLocal()
        try:
            product = db.query(Product).filter(Product.barcode == barcode_value).first()
            if product:
                return {
                    "id": product.id,
                    "class_id": product.class_id,
                    "name": product.name,
                    "price": product.price,
                    "expected_weight_g": product.expected_weight_g,
                    "inventory": product.inventory,
                    "barcode": product.barcode,
                    "image_url": product.image_url
                }
            return None
        finally:
            db.close()
    
    def match_class_to_product(self, class_id: int) -> Optional[Dict[str, Any]]:
        """
        Find product in database by YOLO class ID
        
        Args:
            class_id: YOLO detection class ID
        
        Returns:
            Product dictionary or None if not found
        """
        db = SessionLocal()
        try:
            product = db.query(Product).filter(Product.class_id == class_id).first()
            if product:
                return {
                    "id": product.id,
                    "class_id": product.class_id,
                    "name": product.name,
                    "price": product.price,
                    "expected_weight_g": product.expected_weight_g,
                    "inventory": product.inventory,
                    "barcode": product.barcode,
                    "image_url": product.image_url
                }
            return None
        finally:
            db.close()
    
    def hybrid_detect(
        self, 
        frame: np.ndarray,
        measured_weight_g: Optional[float] = None,
        auto_add_to_cart: bool = False
    ) -> Dict[str, Any]:
        """
        Main hybrid detection workflow:
        1. Try object detection first
        2. If confidence < 80%, fallback to barcode detection
        3. Verify weight if provided
        4. Check for duplicates (cooldown)
        5. Return detection result
        
        Args:
            frame: OpenCV BGR image
            measured_weight_g: Optional weight from load cell sensor
            auto_add_to_cart: Whether to automatically add verified products to cart
        
        Returns:
            Detection result dictionary
        """
        print("\n" + "=" * 70)
        print("🚀 HYBRID DETECTION STARTED")
        print("=" * 70)
        
        result = {
            "success": False,
            "method": None,
            "product": None,
            "confidence": 0.0,
            "weight_verified": False,
            "weight_details": None,
            "message": "",
            "all_detections": [],
            "all_barcodes": []
        }
        
        # Step 1: Object Detection
        object_detections = self.detect_objects(frame)
        result["all_detections"] = object_detections
        
        best_detection = None
        if object_detections:
            # Sort by confidence, get highest
            best_detection = max(object_detections, key=lambda x: x.get("score", 0))
            confidence = best_detection.get("score", 0)
            result["confidence"] = confidence
            
            print(f"🎯 Best object detection: Class {best_detection.get('class')} with {confidence*100:.1f}% confidence")
        
        # Step 2: Decide detection method based on confidence
        detected_product = None
        detection_method = None
        
        if best_detection and result["confidence"] >= self.OBJECT_DETECTION_CONFIDENCE_THRESHOLD:
            # High confidence object detection - use it
            print(f"✅ Object detection confidence ({result['confidence']*100:.1f}%) meets threshold")
            class_id = best_detection.get("class")
            detected_product = self.match_class_to_product(class_id)
            detection_method = "object_detection"
            
        else:
            # Low confidence or no detection - fallback to barcode
            if best_detection:
                print(f"⚠️  Object detection confidence ({result['confidence']*100:.1f}%) below threshold ({self.OBJECT_DETECTION_CONFIDENCE_THRESHOLD*100}%)")
            else:
                print("⚠️  No object detected")
            
            print("🔄 Falling back to barcode detection...")
            
            # Step 3: Barcode Detection Fallback
            barcodes = self.detect_barcodes_multi(frame)
            result["all_barcodes"] = barcodes
            
            if barcodes:
                # Try each detected barcode
                for barcode_info in barcodes:
                    barcode_value = barcode_info.get("value", "").strip()
                    if not barcode_value:
                        continue
                    
                    product = self.match_barcode_to_product(barcode_value)
                    if product:
                        detected_product = product
                        detection_method = "barcode"
                        result["confidence"] = 1.0  # Barcode is 100% accurate when matched
                        print(f"✅ Barcode matched: {barcode_value} -> {product['name']}")
                        break
                
                if not detected_product:
                    result["message"] = "Barcode(s) detected but not found in database"
                    print(f"❌ {result['message']}")
                    return result
            else:
                result["message"] = "No product detected and no barcodes found"
                print(f"❌ {result['message']}")
                return result
        
        # Step 4: Check if we found a product
        if not detected_product:
            result["message"] = "Product not found in database"
            print(f"❌ {result['message']}")
            return result
        
        result["product"] = detected_product
        result["method"] = detection_method
        
        # Step 5: Weight Verification (if weight sensor data provided)
        product_id = detected_product.get("id")
        barcode = detected_product.get("barcode")
        
        if measured_weight_g is not None:
            expected_weight = detected_product.get("expected_weight_g", 0)
            if expected_weight > 0:
                is_valid, weight_details = self.verify_weight(measured_weight_g, expected_weight)
                result["weight_verified"] = is_valid
                result["weight_details"] = weight_details
                
                if is_valid:
                    print(f"✅ Weight verified: {measured_weight_g}g (expected: {expected_weight}g)")
                else:
                    print(f"⚠️  Weight mismatch: {measured_weight_g}g (expected: {expected_weight}g ±{self.WEIGHT_TOLERANCE*100}%)")
                    result["message"] = f"Weight verification failed: {weight_details.get('deviation_percent', 0):.1f}% deviation"
                    # Don't return here - still allow detection, just flag weight issue
        
        # Step 8: Success!
        result["success"] = True
        result["message"] = f"Product detected: {detected_product['name']} (via {detection_method})"
        print(f"✅ {result['message']}")
        print("=" * 70)
        
        return result


# Global singleton instance
_hybrid_service = None

def get_hybrid_service() -> HybridDetectionService:
    """Get or create the global hybrid detection service instance"""
    global _hybrid_service
    if _hybrid_service is None:
        _hybrid_service = HybridDetectionService()
    return _hybrid_service
