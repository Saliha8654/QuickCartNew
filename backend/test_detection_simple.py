"""Simple detection test"""
import requests
import cv2
import numpy as np

print("=" * 70)
print("TESTING CAMERA DETECTION")
print("=" * 70)

# Test backend
try:
    r = requests.get('http://localhost:5000/api/products', timeout=2)
    print(f"\n[OK] Backend running - {len(r.json())} products found")
except:
    print("\n[ERROR] Backend not running!")
    exit(1)

# Capture frame
print("\n[TEST] Capturing frame from camera...")
cam = cv2.VideoCapture(0)
if not cam.isOpened():
    print("[ERROR] Cannot access camera")
    exit(1)

ret, frame = cam.read()
cam.release()

if not ret:
    print("[ERROR] Could not capture frame")
    exit(1)

print(f"[OK] Frame captured: {frame.shape}")

# Test detection
print("\n[TEST] Sending frame to /api/detect...")
ret2, buf = cv2.imencode('.jpg', frame)
files = {'image': ('test.jpg', buf.tobytes(), 'image/jpeg')}
r = requests.post('http://localhost:5000/api/detect', files=files, timeout=10)

print(f"[OK] Response status: {r.status_code}")
result = r.json()

if 'error' in result:
    print(f"[ERROR] Detection failed: {result['error']}")
else:
    detections = result.get('detections', [])
    print(f"[OK] Found {len(detections)} detections")
    
    for i, det in enumerate(detections[:5]):
        print(f"\n  Detection {i+1}:")
        print(f"    Class: {det.get('class')}")
        print(f"    Score: {det.get('score', 0)*100:.1f}%")
        if 'product' in det:
            print(f"    Product: {det['product'].get('name')}")
            print(f"    Price: ${det['product'].get('price')}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
