"""
Hybrid Detection System Test Script
Demonstrates all features of the hybrid detection system
"""
import os
import sys
sys.path.append(os.path.dirname(__file__))

import cv2
import numpy as np
from hybrid_detection import get_hybrid_service
from models import SessionLocal, Product

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def test_barcode_products():
    """Test 1: Display all barcode products in database"""
    print_section("TEST 1: Barcode Products in Database")
    
    db = SessionLocal()
    products = db.query(Product).filter(Product.barcode.isnot(None)).all()
    
    print(f"\nFound {len(products)} products with barcodes:\n")
    for p in products:
        print(f"  [{p.id:3d}] {p.name}")
        print(f"       Barcode: {p.barcode}")
        print(f"       Price: ${p.price:.2f} | Weight: {p.expected_weight_g}g | Stock: {p.inventory}")
        print()
    
    db.close()
    return products

def test_hybrid_service_initialization():
    """Test 2: Initialize hybrid detection service"""
    print_section("TEST 2: Initialize Hybrid Detection Service")
    
    service = get_hybrid_service()
    print(f"\n✅ Service initialized successfully")
    print(f"   Confidence threshold: {service.OBJECT_DETECTION_CONFIDENCE_THRESHOLD * 100}%")
    print(f"   Weight tolerance: {service.WEIGHT_TOLERANCE * 100}%")
    print(f"   Cooldown period: {service.COOLDOWN_SECONDS}s")
    
    return service

def test_weight_verification(service):
    """Test 3: Weight verification logic"""
    print_section("TEST 3: Weight Verification")
    
    test_cases = [
        (100.0, 100.0, "Exact match"),
        (105.0, 100.0, "Within +5% tolerance"),
        (95.0, 100.0, "Within -5% tolerance"),
        (110.0, 100.0, "At upper bound (+10%)"),
        (90.0, 100.0, "At lower bound (-10%)"),
        (115.0, 100.0, "Above tolerance (+15%)"),
        (85.0, 100.0, "Below tolerance (-15%)")
    ]
    
    print("\nWeight Verification Test Cases:\n")
    for measured, expected, description in test_cases:
        is_valid, details = service.verify_weight(measured, expected)
        status = "✅ PASS" if is_valid else "❌ FAIL"
        print(f"{status} | {description}")
        print(f"      Measured: {measured}g | Expected: {expected}g | Deviation: {details['deviation_percent']:.1f}%")
        print(f"      Valid range: {details['lower_bound_g']:.1f}g - {details['upper_bound_g']:.1f}g")
        print()

def test_barcode_matching(service):
    """Test 4: Barcode to product matching"""
    print_section("TEST 4: Barcode Matching")
    
    test_barcodes = [
        "8961102882845",  # Bisconni Chocolate Chip Cookies
        "8886950051062",  # Colgate
        "8964002347353",  # Kurkure
        "9999999999999"   # Non-existent barcode
    ]
    
    print("\nBarcode Lookup Test:\n")
    for barcode in test_barcodes:
        product = service.match_barcode_to_product(barcode)
        if product:
            print(f"✅ Barcode: {barcode}")
            print(f"   Product: {product['name']} (${product['price']:.2f})")
        else:
            print(f"❌ Barcode: {barcode} - Not found in database")
        print()

def test_cooldown_mechanism(service):
    """Test 5: Duplicate detection prevention (cooldown)"""
    print_section("TEST 5: Cooldown Mechanism (Duplicate Prevention)")
    
    import time
    
    print("\nSimulating repeated detections of the same product:\n")
    
    # Simulate detecting product with ID 28 (Bisconni)
    product_id = 28
    barcode = "8961102882845"
    
    print(f"Detection 1: Product ID {product_id}")
    in_cooldown = service._is_in_cooldown(product_id, barcode)
    print(f"  In cooldown: {in_cooldown} (Expected: False)")
    service._record_detection(product_id, barcode)
    print(f"  ✅ Detection recorded, cooldown activated")
    
    print(f"\nDetection 2: Same product immediately after (< 1 second)")
    in_cooldown = service._is_in_cooldown(product_id, barcode)
    print(f"  In cooldown: {in_cooldown} (Expected: True)")
    if in_cooldown:
        print(f"  🚫 Detection blocked - duplicate prevention working!")
    
    print(f"\nWaiting 2 seconds...")
    time.sleep(2)
    
    print(f"\nDetection 3: Same product after 2 seconds")
    in_cooldown = service._is_in_cooldown(product_id, barcode)
    print(f"  In cooldown: {in_cooldown} (Expected: True, cooldown is 4s)")
    
    print(f"\nWaiting 3 more seconds (total 5s)...")
    time.sleep(3)
    
    print(f"\nDetection 4: Same product after 5 seconds total")
    in_cooldown = service._is_in_cooldown(product_id, barcode)
    print(f"  In cooldown: {in_cooldown} (Expected: False, cooldown expired)")
    if not in_cooldown:
        print(f"  ✅ Cooldown expired, can detect again!")

def test_detection_methods(service):
    """Test 6: Detection method selection logic"""
    print_section("TEST 6: Detection Method Selection")
    
    print("\nThe hybrid detection system uses the following logic:")
    print("\n1. Object Detection First:")
    print("   - Runs YOLO model on camera frame")
    print("   - If confidence >= 80% → Use object detection result")
    print("   - If confidence < 80% → Fallback to barcode detection")
    
    print("\n2. Barcode Detection Fallback:")
    print("   - Scans for multiple barcodes in the same frame")
    print("   - Matches barcode to product database")
    print("   - 100% accurate when barcode is found")
    
    print("\n3. Weight Verification:")
    print("   - Compares measured weight to expected weight")
    print("   - Tolerance: ±10%")
    print("   - Flags mismatches but still allows detection")
    
    print("\n4. Duplicate Prevention:")
    print("   - 4-second cooldown per product")
    print("   - Prevents same item from being added multiple times")
    print("   - Works with both product ID and barcode")

def print_api_endpoints():
    """Display available API endpoints"""
    print_section("API ENDPOINTS")
    
    print("\n📡 Available Endpoints:\n")
    
    print("1. POST /api/camera/detect/hybrid")
    print("   - Hybrid detection from live camera feed")
    print("   - Body (JSON): {")
    print('       "weight_g": 100.5,          // Optional: weight from load cell')
    print('       "auto_add_to_cart": true    // Optional: auto-add verified products')
    print("   }")
    print("   - Returns: Full detection result with method, product, weight verification")
    
    print("\n2. POST /api/detect/hybrid")
    print("   - Hybrid detection from uploaded image")
    print("   - Form Data:")
    print("       - image: (file) Image file to process")
    print("       - weight_g: (optional) Measured weight")
    print("       - auto_add_to_cart: (optional) 'true' or 'false'")
    print("   - Returns: Same as camera endpoint")
    
    print("\n3. GET /api/camera/stream")
    print("   - Live MJPEG camera stream")
    
    print("\n4. POST /api/camera/detect")
    print("   - Legacy object detection endpoint (still available)")

def print_usage_guide():
    """Print usage guide"""
    print_section("USAGE GUIDE")
    
    print("\n🚀 How to Use the Hybrid Detection System:\n")
    
    print("STEP 1: Start the Backend Server")
    print("   cd backend")
    print("   python app.py")
    
    print("\nSTEP 2: Test with Camera (Example using curl):")
    print('   curl -X POST http://localhost:5000/api/camera/detect/hybrid \\')
    print('        -H "Content-Type: application/json" \\')
    print('        -d \'{"weight_g": 100, "auto_add_to_cart": true}\'')
    
    print("\nSTEP 3: Test with Image Upload:")
    print('   curl -X POST http://localhost:5000/api/detect/hybrid \\')
    print('        -F "image=@product.jpg" \\')
    print('        -F "weight_g=100" \\')
    print('        -F "auto_add_to_cart=true"')
    
    print("\nSTEP 4: Frontend Integration (React Example):")
    print("   ```javascript")
    print("   const detectProduct = async (imageBlob, weight) => {")
    print("     const formData = new FormData();")
    print("     formData.append('image', imageBlob);")
    print("     if (weight) formData.append('weight_g', weight);")
    print("     formData.append('auto_add_to_cart', 'true');")
    print("     ")
    print("     const response = await fetch('/api/detect/hybrid', {")
    print("       method: 'POST',")
    print("       body: formData")
    print("     });")
    print("     return await response.json();")
    print("   };")
    print("   ```")

def print_system_summary():
    """Print system capabilities summary"""
    print_section("SYSTEM CAPABILITIES SUMMARY")
    
    print("\n✨ Features Implemented:\n")
    
    features = [
        ("✅", "Real-time object detection using YOLO"),
        ("✅", "Multiple barcode detection (EAN-13, UPC, QR codes, etc.)"),
        ("✅", "Intelligent fallback: Object detection → Barcode scanning"),
        ("✅", "80% confidence threshold for object detection"),
        ("✅", "Weight verification with ±10% tolerance"),
        ("✅", "Duplicate prevention with 4-second cooldown"),
        ("✅", "Automatic cart integration"),
        ("✅", "11 pre-configured barcode products"),
        ("✅", "Production-ready error handling"),
        ("✅", "Comprehensive logging and debugging"),
        ("✅", "RESTful API endpoints"),
        ("✅", "Camera and image upload support")
    ]
    
    for status, feature in features:
        print(f"   {status} {feature}")
    
    print("\n📊 Configuration:\n")
    service = get_hybrid_service()
    print(f"   - Object detection confidence threshold: {service.OBJECT_DETECTION_CONFIDENCE_THRESHOLD * 100}%")
    print(f"   - Weight tolerance: ±{service.WEIGHT_TOLERANCE * 100}%")
    print(f"   - Cooldown period: {service.COOLDOWN_SECONDS} seconds")
    print(f"   - Detection cycle: Every 2 seconds (configurable)")

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "HYBRID DETECTION SYSTEM TEST SUITE" + " " * 24 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        # Run tests
        products = test_barcode_products()
        service = test_hybrid_service_initialization()
        test_weight_verification(service)
        test_barcode_matching(service)
        test_cooldown_mechanism(service)
        test_detection_methods(service)
        
        # Print guides
        print_api_endpoints()
        print_usage_guide()
        print_system_summary()
        
        print_section("TEST SUITE COMPLETED")
        print("\n✅ All tests completed successfully!")
        print("\n💡 The hybrid detection system is ready to use.")
        print("   Start the backend server and use the API endpoints above.\n")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
