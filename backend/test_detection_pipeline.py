"""
Comprehensive Detection Pipeline Test
Tests object detection, barcode detection, and hybrid detection
"""
import cv2
import numpy as np
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

print("=" * 70)
print("DETECTION PIPELINE TEST")
print("=" * 70)

# Test 1: Load YOLO Model
print("\n[TEST 1] Loading YOLO Model...")
try:
    from detection import load_model, predict_image
    model = load_model()
    if model is None:
        print("❌ FAILED: Model is None")
        sys.exit(1)
    print("✅ PASSED: YOLO model loaded successfully")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 2: Test Camera Access
print("\n[TEST 2] Testing Camera Access...")
try:
    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        print("⚠️  WARNING: Camera not available (may be in use or not connected)")
        print("    Creating test image instead...")
        # Create a test image
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add some color to make it interesting
        test_frame[:, :, 0] = 100  # Blue channel
        test_frame[:, :, 1] = 150  # Green channel
        test_frame[:, :, 2] = 200  # Red channel
    else:
        print("✅ PASSED: Camera opened successfully")
        # Capture a frame
        ret, test_frame = camera.read()
        if not ret:
            print("⚠️  WARNING: Could not capture frame, using generated test image")
            test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        else:
            print(f"✅ PASSED: Frame captured ({test_frame.shape})")
        camera.release()
except Exception as e:
    print(f"❌ FAILED: {e}")
    test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

# Test 3: Test Object Detection
print("\n[TEST 3] Testing Object Detection...")
try:
    detections = predict_image(test_frame, conf=0.4)
    print(f"✅ PASSED: Object detection returned {len(detections)} detections")
    for i, det in enumerate(detections[:5]):  # Show first 5
        print(f"   Detection {i+1}: Class={det['class']}, Score={det['score']:.2f}, BBox={det['bbox']}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Test Barcode Detection
print("\n[TEST 4] Testing Barcode Detection...")
try:
    from barcode_detection import detect_barcodes
    barcodes = detect_barcodes(test_frame)
    print(f"✅ PASSED: Barcode detection returned {len(barcodes)} barcodes")
    for i, bc in enumerate(barcodes[:5]):  # Show first 5
        print(f"   Barcode {i+1}: Type={bc['type']}, Value={bc['value']}, BBox={bc.get('bbox')}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test Hybrid Detection Service
print("\n[TEST 5] Testing Hybrid Detection Service...")
try:
    from hybrid_detection import get_hybrid_service
    hybrid_service = get_hybrid_service()
    
    result = hybrid_service.hybrid_detect(
        frame=test_frame,
        measured_weight_g=None,
        auto_add_to_cart=False
    )
    
    print(f"✅ PASSED: Hybrid detection completed")
    print(f"   Success: {result['success']}")
    print(f"   Method: {result['method']}")
    print(f"   Product: {result['product']}")
    print(f"   Confidence: {result['confidence']}")
    print(f"   Message: {result['message']}")
    print(f"   All Detections: {len(result['all_detections'])}")
    print(f"   All Barcodes: {len(result['all_barcodes'])}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Test Database Connection
print("\n[TEST 6] Testing Database Connection...")
try:
    from models import SessionLocal, Product
    db = SessionLocal()
    products = db.query(Product).all()
    print(f"✅ PASSED: Database connected, found {len(products)} products")
    for i, prod in enumerate(products[:5]):  # Show first 5
        print(f"   Product {i+1}: ID={prod.id}, Name={prod.name}, ClassID={prod.class_id}, Barcode={prod.barcode}")
    db.close()
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 7: Test Flask Routes (without starting server)
print("\n[TEST 7] Testing Flask Route Registration...")
try:
    from routes.detect import detect_bp
    print(f"✅ PASSED: Detection blueprint loaded")
    print(f"   Routes in blueprint:")
    for rule in detect_bp.url_map.iter_rules() if hasattr(detect_bp, 'url_map') else []:
        print(f"      {rule}")
    # Note: Blueprint routes are only available after app registration
    print("   Note: Full routes available after app.register_blueprint()")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("DETECTION PIPELINE TEST COMPLETE")
print("=" * 70)
