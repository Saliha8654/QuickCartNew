"""
Live Camera Detection Test with Multiple Objects and Barcodes
Tests the complete detection flow with real camera input
"""
import cv2
import numpy as np
import requests
import time
import sys

API_URL = "http://localhost:5000/api"

print("=" * 70)
print("LIVE CAMERA DETECTION TEST")
print("=" * 70)

# Test 1: Check if backend is running
print("\n[TEST 1] Checking if backend server is running...")
try:
    response = requests.get(f"{API_URL}/products", timeout=5)
    if response.status_code == 200:
        products = response.json()
        print(f"✅ PASSED: Backend is running, found {len(products)} products")
    else:
        print(f"❌ FAILED: Backend returned status {response.status_code}")
        print("   Please start the backend server: python app.py")
        sys.exit(1)
except requests.exceptions.ConnectionError:
    print("❌ FAILED: Cannot connect to backend server")
    print("   Please start the backend server: python app.py")
    sys.exit(1)
except Exception as e:
    print(f"❌ FAILED: {e}")
    sys.exit(1)

# Test 2: Check camera access
print("\n[TEST 2] Checking camera access...")
camera = cv2.VideoCapture(0)
if not camera.isOpened():
    print("❌ FAILED: Cannot access camera")
    print("   Make sure your camera is connected and not in use")
    sys.exit(1)
else:
    print("✅ PASSED: Camera is accessible")

# Test 3: Capture and test object detection
print("\n[TEST 3] Testing object detection with camera...")
print("   Capturing frame in 3 seconds... Please position items in view!")
time.sleep(3)

ret, frame = camera.read()
if not ret:
    print("❌ FAILED: Could not capture frame")
    camera.release()
    sys.exit(1)

print(f"✅ PASSED: Frame captured ({frame.shape})")

# Save frame for debugging
cv2.imwrite("test_frame.jpg", frame)
print("   Frame saved as 'test_frame.jpg'")

# Test 4: Test /api/detect endpoint
print("\n[TEST 4] Testing /api/detect endpoint...")
try:
    # Encode frame as JPEG
    ret, buffer = cv2.imencode('.jpg', frame)
    if not ret:
        print("❌ FAILED: Could not encode frame")
        camera.release()
        sys.exit(1)
    
    # Send to detection endpoint
    files = {'image': ('frame.jpg', buffer.tobytes(), 'image/jpeg')}
    response = requests.post(f"{API_URL}/detect", files=files, timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        detections = result.get('detections', [])
        print(f"✅ PASSED: Detection endpoint returned {len(detections)} detections")
        
        for i, det in enumerate(detections[:5]):
            print(f"\n   Detection {i+1}:")
            print(f"      Class: {det.get('class')}")
            print(f"      Score: {det.get('score', 0):.2%}")
            print(f"      BBox: {det.get('bbox')}")
            if 'barcode_value' in det:
                print(f"      Barcode: {det.get('barcode_value')} ({det.get('barcode_type')})")
                print(f"      Barcode IOU: {det.get('barcode_iou', 0):.2f}")
            if 'product' in det:
                prod = det['product']
                print(f"      Product: {prod.get('name')}")
                print(f"      Price: ${prod.get('price')}")
                print(f"      Expected Weight: {prod.get('expected_weight_g')}g")
    else:
        print(f"❌ FAILED: Detection endpoint returned status {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Test hybrid detection endpoint
print("\n[TEST 5] Testing /api/camera/detect/hybrid endpoint...")
try:
    # Start camera endpoint
    response = requests.get(f"{API_URL}/camera/start", timeout=5)
    print(f"   Camera start response: {response.json()}")
    
    # Wait a bit for camera to initialize
    time.sleep(1)
    
    # Test hybrid detection
    data = {
        'weight_g': None,
        'auto_add_to_cart': False
    }
    response = requests.post(f"{API_URL}/camera/detect/hybrid", json=data, timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ PASSED: Hybrid detection completed")
        print(f"   Success: {result.get('success')}")
        print(f"   Method: {result.get('method')}")
        print(f"   Message: {result.get('message')}")
        print(f"   Confidence: {result.get('confidence', 0):.2%}")
        
        if result.get('product'):
            prod = result['product']
            print(f"\n   Detected Product:")
            print(f"      Name: {prod.get('name')}")
            print(f"      Price: ${prod.get('price')}")
            print(f"      Barcode: {prod.get('barcode')}")
        
        print(f"\n   All Detections: {len(result.get('all_detections', []))}")
        print(f"   All Barcodes: {len(result.get('all_barcodes', []))}")
        
        for i, det in enumerate(result.get('all_detections', [])[:3]):
            print(f"      Detection {i+1}: Class={det.get('class')}, Score={det.get('score', 0):.2%}")
        
        for i, bc in enumerate(result.get('all_barcodes', [])[:3]):
            print(f"      Barcode {i+1}: Type={bc.get('type')}, Value={bc.get('value')}")
    else:
        print(f"❌ FAILED: Hybrid detection returned status {response.status_code}")
        print(f"   Response: {response.text}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()

# Clean up
camera.release()
print("\n" + "=" * 70)
print("LIVE CAMERA DETECTION TEST COMPLETE")
print("=" * 70)
print("\nTips:")
print("  - If no objects detected, ensure items are clearly visible in frame")
print("  - For barcode detection, ensure barcodes are clearly visible and well-lit")
print("  - Check test_frame.jpg to see what the camera captured")
print("  - For multiple object detection, spread items out in the frame")
