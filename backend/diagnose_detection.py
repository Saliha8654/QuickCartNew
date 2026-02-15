"""
Diagnostic Tool: Object Detection & Barcode Detection System Checker
Helps identify why detection might not be working
"""
import cv2
import sys
import os
import time
import numpy as np
sys.path.append(os.path.dirname(__file__))

from detection import predict_image, load_model
from barcode_detection import detect_barcodes
from hybrid_detection import get_hybrid_service
from models import SessionLocal, Product

def print_header(title):
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def check_camera_access():
    """Check if camera is accessible"""
    print_header("CAMERA ACCESS CHECK")
    
    print("\n🔍 Testing camera access...")
    
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ CAMERA ERROR: Cannot open camera")
            print("   Possible causes:")
            print("   - Camera in use by another application")
            print("   - Camera permissions not granted")
            print("   - No camera connected")
            cap.release()
            return False
        
        print("✅ Camera opened successfully")
        
        # Try to capture a frame
        success, frame = cap.read()
        cap.release()
        
        if not success:
            print("❌ CAMERA ERROR: Cannot capture frame")
            print("   Possible causes:")
            print("   - Camera hardware issue")
            print("   - Driver problems")
            return False
        
        print(f"✅ Frame captured successfully")
        print(f"   Frame dimensions: {frame.shape[1]}x{frame.shape[0]} pixels")
        print(f"   Color channels: {frame.shape[2] if len(frame.shape) > 2 else 1}")
        
        return True
        
    except Exception as e:
        print(f"❌ CAMERA ERROR: {e}")
        return False

def check_object_detection():
    """Check object detection capability"""
    print_header("OBJECT DETECTION CHECK")
    
    print("\n🔍 Testing object detection...")
    
    try:
        # Try to load model
        model = load_model()
        if model is None:
            print("❌ OBJECT DETECTION ERROR: Cannot load YOLO model")
            print("   Possible causes:")
            print("   - Model file missing or corrupted")
            print("   - Path configuration issue")
            return False
        
        print("✅ YOLO model loaded successfully")
        
        # Create a simple test image
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.rectangle(frame, (100, 100), (200, 200), (0, 255, 0), -1)
        
        # Test detection
        detections = predict_image(frame)
        print(f"✅ Object detection test completed")
        print(f"   Detections found: {len(detections)}")
        
        return True
        
    except Exception as e:
        print(f"❌ OBJECT DETECTION ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_barcode_detection():
    """Check barcode detection capability"""
    print_header("BARCODE DETECTION CHECK")
    
    print("\n🔍 Testing barcode detection...")
    
    try:
        # Create a dummy frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Test barcode detection
        barcodes = detect_barcodes(frame)
        print(f"✅ Barcode detection test completed")
        print(f"   Barcodes found: {len(barcodes)}")
        
        # Check what backend is being used
        try:
            import pyzxing
            print("✅ Using ZXing (pyzxing) backend - preferred")
        except ImportError:
            print("⚠️  Using OpenCV BarcodeDetector fallback")
            print("   Note: For better barcode detection, install pyzxing:")
            print("   pip install pyzxing")
        
        return True
        
    except Exception as e:
        print(f"❌ BARCODE DETECTION ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database():
    """Check database connectivity and products"""
    print_header("DATABASE CHECK")
    
    print("\n🔍 Testing database connectivity...")
    
    try:
        db = SessionLocal()
        products = db.query(Product).count()
        barcode_products = db.query(Product).filter(Product.barcode.isnot(None)).count()
        db.close()
        
        print(f"✅ Database connection successful")
        print(f"   Total products: {products}")
        print(f"   Products with barcodes: {barcode_products}")
        
        if barcode_products == 0:
            print("⚠️  WARNING: No products with barcodes found")
            print("   This may affect barcode detection functionality")
        
        return True
        
    except Exception as e:
        print(f"❌ DATABASE ERROR: {e}")
        return False

def check_hybrid_service():
    """Check hybrid detection service"""
    print_header("HYBRID SERVICE CHECK")
    
    print("\n🔍 Testing hybrid detection service...")
    
    try:
        service = get_hybrid_service()
        print("✅ Hybrid detection service initialized")
        print(f"   Confidence threshold: {service.OBJECT_DETECTION_CONFIDENCE_THRESHOLD * 100}%")
        print(f"   Weight tolerance: ±{service.WEIGHT_TOLERANCE * 100}%")
        print(f"   Cooldown period: {service.COOLDOWN_SECONDS} seconds")
        
        # Test with dummy frame
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = service.hybrid_detect(frame)
        
        print(f"✅ Hybrid detection test completed")
        print(f"   Success: {result['success']}")
        print(f"   Message: {result['message']}")
        
        return True
        
    except Exception as e:
        print(f"❌ HYBRID SERVICE ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_api_endpoints():
    """Check if API endpoints are responsive"""
    print_header("API ENDPOINT CHECK")
    
    print("\n🔍 Testing API endpoints...")
    
    try:
        import requests
        
        # Test camera start endpoint
        try:
            response = requests.get('http://localhost:5000/api/camera/start', timeout=5)
            print(f"✅ Camera start endpoint: {response.status_code}")
        except:
            print("❌ Camera start endpoint: NOT RESPONDING")
        
        # Test hybrid detection endpoint
        try:
            response = requests.post('http://localhost:5000/api/camera/detect/hybrid', 
                                   json={'auto_add_to_cart': False}, 
                                   timeout=10)
            print(f"✅ Hybrid detection endpoint: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Response: {result.get('message', 'No message')}")
        except:
            print("❌ Hybrid detection endpoint: NOT RESPONDING")
        
        # Test cart endpoint
        try:
            response = requests.get('http://localhost:5000/api/cart', timeout=5)
            print(f"✅ Cart endpoint: {response.status_code}")
        except:
            print("❌ Cart endpoint: NOT RESPONDING")
        
        return True
        
    except Exception as e:
        print(f"❌ API CHECK ERROR: {e}")
        return False

def troubleshooting_guide():
    """Provide troubleshooting suggestions"""
    print_header("TROUBLESHOOTING GUIDE")
    
    print("\n💡 COMMON ISSUES AND SOLUTIONS:")
    
    print("\n1. 📷 CAMERA NOT DETECTING PRODUCTS:")
    print("   - Ensure good lighting")
    print("   - Place product clearly in camera view")
    print("   - Hold product steady for 2-3 seconds")
    print("   - Check camera lens is clean")
    
    print("\n2. 🔍 OBJECT DETECTION NOT WORKING:")
    print("   - Ensure YOLO model file exists")
    print("   - Check models/best.pt file")
    print("   - Verify model is compatible")
    
    print("\n3. 📊 BARCODE NOT DETECTED:")
    print("   - Ensure barcode is clearly visible")
    print("   - Try installing pyzxing for better detection:")
    print("     pip install pyzxing")
    print("   - Check barcode is not damaged")
    
    print("\n4. 🌐 API ENDPOINTS NOT RESPONDING:")
    print("   - Ensure Flask server is running")
    print("   - Check if port 5000 is available")
    print("   - Verify no firewall blocking")
    
    print("\n5. 🗄️ DATABASE ISSUES:")
    print("   - Check MySQL server is running")
    print("   - Verify database credentials")
    print("   - Ensure products table has barcode data")

def run_comprehensive_check():
    """Run all checks"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "QUICKCART DETECTION SYSTEM DIAGNOSTIC" + " " * 22 + "║")
    print("╚" + "=" * 78 + "╝")
    
    checks = [
        ("Camera Access", check_camera_access),
        ("Object Detection", check_object_detection),
        ("Barcode Detection", check_barcode_detection),
        ("Database", check_database),
        ("Hybrid Service", check_hybrid_service),
        ("API Endpoints", check_api_endpoints)
    ]
    
    results = []
    
    for name, check_func in checks:
        print(f"\n🔍 Checking {name}...")
        try:
            result = check_func()
            results.append((name, result))
            if result:
                print(f"   ✅ {name}: PASSED")
            else:
                print(f"   ❌ {name}: FAILED")
        except Exception as e:
            print(f"   ❌ {name}: ERROR - {e}")
            results.append((name, False))
    
    # Summary
    print_header("DIAGNOSTIC SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 ALL SYSTEMS FUNCTIONAL!")
        print("   Your detection system is working correctly.")
        print("   If you're not getting detections, try:")
        print("   1. Placing a product with barcode in front of camera")
        print("   2. Ensuring good lighting")
        print("   3. Holding product steady for 2-3 seconds")
    else:
        failed_checks = [name for name, result in results if not result]
        print(f"\n⚠️  {len(failed_checks)} CHECK(S) FAILED:")
        for check_name in failed_checks:
            print(f"   - {check_name}")
        
        print("\n🔧 RECOMMENDED ACTIONS:")
        for check_name in failed_checks:
            print(f"   - Fix {check_name} issue (see troubleshooting guide below)")
    
    # Show troubleshooting guide
    troubleshooting_guide()
    
    print("\n" + "=" * 80)
    print("  DIAGNOSTIC COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    run_comprehensive_check()
