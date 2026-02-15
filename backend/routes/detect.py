from flask import Blueprint, request, jsonify, Response
import cv2
import numpy as np
import json

# ---------------------------------------------------------------------------
# Robust imports for detection model and database
# ---------------------------------------------------------------------------
try:
    # When running the app from inside the backend/ folder
    from detection import predict_image, load_model
except ImportError:
    # When importing as a package: `from backend import app`
    from backend.detection import predict_image, load_model

try:
    from models import SessionLocal, Product, CartItem
except ImportError:
    from backend.models import SessionLocal, Product, CartItem

# Import hybrid detection service
try:
    from hybrid_detection import get_hybrid_service
except ImportError:
    from backend.hybrid_detection import get_hybrid_service

# ---------------------------------------------------------------------------
# Barcode detection (ZXing or OpenCV fallback)
# ---------------------------------------------------------------------------
BARCODE_DETECTION_AVAILABLE = True

try:
    from barcode_detection import detect_barcodes, match_barcodes_to_detections
except ImportError as e:
    try:
        # Package-style import
        from backend.barcode_detection import detect_barcodes, match_barcodes_to_detections
    except ImportError:
        print(f"Warning: Barcode detection not available: {e}")

        # Define dummy functions when barcode detection is not available
        def detect_barcodes(frame):
            return []

        def match_barcodes_to_detections(barcodes, detections, iou_threshold=0.1):
            return detections

        BARCODE_DETECTION_AVAILABLE = False

detect_bp = Blueprint("detect", __name__)

# Camera instance (global to keep it alive)
camera = None

@detect_bp.post("/detect")
def detect():
    try:
        if 'image' not in request.files:
            return jsonify({"error":"image required"}), 400
        
        f = request.files['image']
        if f.filename == '':
            return jsonify({"error":"no file selected"}), 400
        
        # Convert uploaded image to numpy array for reuse in barcode detection
        file_bytes = f.read()
        np_arr = np.frombuffer(file_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        print(f"[DEBUG] Received image: {frame.shape if frame is not None else 'None'}")
        
        # Save frame for debugging (every 10th request to avoid spam)
        import random
        if random.randint(1, 10) == 1:
            cv2.imwrite("last_detection_frame.jpg", frame)
            print("  Saved frame as last_detection_frame.jpg for debugging")

        # Run object detection with lowered confidence for MAXIMUM sensitivity
        dets = predict_image(frame, conf=0.15)
        
        print(f"[DEBUG] Detections found: {len(dets)}")
        if len(dets) > 0:
            for i, d in enumerate(dets[:3]):
                print(f"  Detection {i+1}: Class={d['class']}, Score={d['score']*100:.1f}%")
        else:
            print("  [WARNING] No detections! Possible reasons:")
            print("    - Products too far (move to 30-50cm)")
            print("    - Poor lighting (turn on lights)")
            print("    - Camera angle wrong (face product label to camera)")
            print("    - Product not from trained model")
            print("    - Check last_detection_frame.jpg to see what camera sees")

        # Run multi-barcode detection on the same frame
        barcode_results = detect_barcodes(frame)
        # Attach nearby barcodes to detections
        dets = match_barcodes_to_detections(barcode_results, dets)

        db = SessionLocal()
        out = []
        
        for d in dets:
            cls = d["class"]
            prod = db.query(Product).filter(Product.class_id==cls).first()
            item = {"class":cls, "score":d["score"], "bbox":d["bbox"]}
            # Attach barcode info from vision layer (if any)
            if "barcode_value" in d:
                item["barcode_value"] = d["barcode_value"]
                item["barcode_type"] = d.get("barcode_type")
                item["barcode_iou"] = d.get("barcode_iou")
            if prod:
                item["product"] = {
                    "id":prod.id,
                    "name":prod.name,
                    "price":prod.price,
                    "expected_weight_g":prod.expected_weight_g,
                    "inventory":prod.inventory,
                    "image_url":prod.image_url
                }
            out.append(item)
        
        db.close()
        return jsonify({"detections": out})
    
    except Exception as e:
        print(f"❌ Detection endpoint error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "detections": []}), 200

@detect_bp.get("/camera/start")
def start_camera():
    """Initialize camera"""
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
        if not camera.isOpened():
            return jsonify({"error": "Could not open camera"}), 500
    return jsonify({"message": "Camera started"})

@detect_bp.get("/camera/stop")
def stop_camera():
    """Stop camera"""
    global camera
    if camera is not None:
        camera.release()
        camera = None
    return jsonify({"message": "Camera stopped"})

@detect_bp.get("/camera/stream")
def camera_stream():
    """Stream camera feed as MJPEG"""
    def generate():
        global camera
        if camera is None:
            camera = cv2.VideoCapture(0)
        
        while True:
            success, frame = camera.read()
            if not success:
                break
            
            # Encode frame as JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@detect_bp.post("/camera/detect")
def detect_from_camera():
    """Capture current frame and run detection"""
    global camera
    
    if camera is None:
        camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        return jsonify({"error": "Camera not available"}), 500
    
    # Capture frame
    success, frame = camera.read()
    if not success:
        return jsonify({"error": "Failed to capture frame"}), 500
    
    # Run detection on frame with improved parameters for multiple objects
    model = load_model()
    if model is None:
        return jsonify({"error": "Model not loaded"}), 500
        
    # Use the same parameters as in predict_image for consistency
    # Using 15% confidence for MAXIMUM detection sensitivity
    results = model.predict(source=frame, conf=0.15, iou=0.5, verbose=False)
    
    detections = []
    db = SessionLocal()
    
    if results and len(results) > 0 and hasattr(results[0], 'boxes') and results[0].boxes is not None:
        boxes = results[0].boxes
        processed_detections = []
        
        for box in boxes:
            if box is not None and hasattr(box, 'xyxy') and box.xyxy is not None:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf_score = float(box.conf[0])
                cls_id = int(box.cls[0])
                
                # Only include detections with reasonable confidence (lowered to 15% for MAXIMUM sensitivity)
                if conf_score >= 0.15:
                    # Get product from database
                    prod = db.query(Product).filter(Product.class_id == cls_id).first()
                    
                    detection = {
                        "class": cls_id,
                        "score": conf_score,
                        "bbox": [int(x1), int(y1), int(x2), int(y2)]
                    }
                    
                    if prod:
                        detection["product"] = {
                            "id": prod.id,
                            "name": prod.name,
                            "price": prod.price,
                            "expected_weight_g": prod.expected_weight_g,
                            "inventory": prod.inventory,
                            "image_url": prod.image_url,
                            "barcode": getattr(prod, "barcode", None),
                        }
                    
                    processed_detections.append(detection)

        # Run multi-barcode detection on the same frame and spatially match
        barcode_results = detect_barcodes(frame)
        processed_detections = match_barcodes_to_detections(barcode_results, processed_detections)

        # Now enforce cross-checking: only mark detections as "verified" when
        # barcode (if present and known in DB) matches the product's barcode.
        for det in processed_detections:
            det["barcode_verified"] = False
            bc_val = det.get("barcode_value")
            prod_info = det.get("product")
            prod_barcode = prod_info.get("barcode") if prod_info else None

            # If both model + barcode agree, mark as verified
            if bc_val and prod_barcode and bc_val == prod_barcode:
                det["barcode_verified"] = True

        # Sort by confidence and limit to top 10
        processed_detections.sort(key=lambda x: x['score'], reverse=True)
        detections = processed_detections[:10]
    
    db.close()
    return jsonify({"detections": detections})

@detect_bp.post("/camera/detect/hybrid")
def hybrid_detect_from_camera():
    """
    Advanced hybrid detection endpoint:
    1. Captures frame from camera
    2. Runs object detection first
    3. If confidence < 80%, falls back to multi-barcode detection
    4. Verifies weight if provided
    5. Prevents duplicates with cooldown mechanism
    6. Optionally adds to cart
    """
    global camera
    
    if camera is None:
        camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        return jsonify({"error": "Camera not available"}), 500
    
    # Capture frame
    success, frame = camera.read()
    if not success:
        return jsonify({"error": "Failed to capture frame"}), 500
    
    # Get optional parameters
    try:
        body = request.get_json(force=True) if request.is_json else {}
    except:
        body = {}
    
    measured_weight_g = body.get("weight_g")  # Optional weight from load cell
    auto_add = body.get("auto_add_to_cart", False)  # Auto-add to cart if verified
    
    # Get hybrid detection service
    hybrid_service = get_hybrid_service()
    
    # Run hybrid detection
    result = hybrid_service.hybrid_detect(
        frame=frame,
        measured_weight_g=measured_weight_g,
        auto_add_to_cart=auto_add
    )
    
    # If successful and weight verified, optionally add to cart
    if result["success"] and auto_add:
        product = result.get("product")
        if product:
            # Check if weight verification is required
            weight_required = measured_weight_g is not None
            weight_ok = result.get("weight_verified", True) if weight_required else True
            
            if weight_ok:
                # Add to cart
                db = SessionLocal()
                try:
                    product_id = product["id"]
                    
                    # Check if already in cart
                    existing = db.query(CartItem).filter(CartItem.product_id == product_id).first()
                    if existing:
                        existing.quantity += 1
                        if weight_ok:
                            existing.weight_verified = 1
                    else:
                        cart_item = CartItem(
                            product_id=product_id,
                            quantity=1,
                            unit_price=product["price"],
                            weight_verified=1 if weight_ok else 0
                        )
                        db.add(cart_item)
                    
                    db.commit()
                    result["added_to_cart"] = True
                    result["message"] += " | Added to cart"
                except Exception as e:
                    db.rollback()
                    result["cart_error"] = str(e)
                finally:
                    db.close()
    
    return jsonify(result)

@detect_bp.post("/detect/hybrid")
def hybrid_detect_from_upload():
    """
    Hybrid detection from uploaded image (for testing)
    Same logic as camera endpoint but accepts file upload
    """
    try:
        if 'image' not in request.files:
            return jsonify({"error": "image required"}), 400
        
        f = request.files['image']
        if f.filename == '':
            return jsonify({"error": "no file selected"}), 400
        
        # Convert uploaded image to numpy array
        file_bytes = f.read()
        np_arr = np.frombuffer(file_bytes, np.uint8)
        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        
        # Get optional parameters from form data
        measured_weight_g = request.form.get("weight_g")
        if measured_weight_g:
            measured_weight_g = float(measured_weight_g)
        
        auto_add = request.form.get("auto_add_to_cart", "false").lower() == "true"
        
        # Get hybrid detection service
        hybrid_service = get_hybrid_service()
        
        # Run hybrid detection
        result = hybrid_service.hybrid_detect(
            frame=frame,
            measured_weight_g=measured_weight_g,
            auto_add_to_cart=auto_add
        )
        
        # If successful and auto_add requested, add to cart
        if result["success"] and auto_add:
            product = result.get("product")
            if product:
                weight_required = measured_weight_g is not None
                weight_ok = result.get("weight_verified", True) if weight_required else True
                
                if weight_ok:
                    db = SessionLocal()
                    try:
                        product_id = product["id"]
                        
                        existing = db.query(CartItem).filter(CartItem.product_id == product_id).first()
                        if existing:
                            existing.quantity += 1
                            if weight_ok:
                                existing.weight_verified = 1
                        else:
                            cart_item = CartItem(
                                product_id=product_id,
                                quantity=1,
                                unit_price=product["price"],
                                weight_verified=1 if weight_ok else 0
                            )
                            db.add(cart_item)
                        
                        db.commit()
                        result["added_to_cart"] = True
                        result["message"] += " | Added to cart"
                    except Exception as e:
                        db.rollback()
                        result["cart_error"] = str(e)
                    finally:
                        db.close()
        
        return jsonify(result)
    
    except Exception as e:
        print(f"❌ Hybrid detection error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e), "success": False}), 500