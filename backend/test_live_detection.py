"""Test live detection with lower confidence"""
import cv2
import numpy as np
from detection import predict_image

print("=" * 70)
print("TESTING LIVE CAMERA DETECTION WITH YOUR PRODUCTS")
print("=" * 70)

# Open camera
print("\nOpening camera...")
cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("[ERROR] Cannot open camera!")
    exit(1)

print("[OK] Camera opened!")
print("\nPlease position one of these products in front of camera:")
print("  - Bisconni Chocolate Chip Cookies")
print("  - Coca Cola Can")
print("  - Oreo Biscuit")
print("  - Lays")
print("  - Any product from your list")
print("\nCapturing in 3 seconds...")

import time
time.sleep(3)

# Capture frame
ret, frame = cam.read()
cam.release()

if not ret:
    print("[ERROR] Could not capture frame")
    exit(1)

print(f"[OK] Frame captured: {frame.shape}")

# Save frame for inspection
cv2.imwrite("debug_frame.jpg", frame)
print("[OK] Frame saved as debug_frame.jpg - check this to see what camera sees!")

# Test with different confidence thresholds
print("\n" + "=" * 70)
print("TESTING WITH DIFFERENT CONFIDENCE THRESHOLDS")
print("=" * 70)

for conf in [0.15, 0.25, 0.35, 0.45, 0.60]:
    print(f"\n[TEST] Confidence threshold: {conf*100:.0f}%")
    detections = predict_image(frame, conf=conf)
    print(f"  Found {len(detections)} detections")
    
    for i, det in enumerate(detections[:3]):
        print(f"    Detection {i+1}:")
        print(f"      Class ID: {det['class']}")
        print(f"      Confidence: {det['score']*100:.1f}%")
        print(f"      BBox: {det['bbox']}")

print("\n" + "=" * 70)
print("RECOMMENDATIONS")
print("=" * 70)

if len(detections) == 0:
    print("\nNo detections found! Try these:")
    print("  1. Move item CLOSER to camera (30-50cm)")
    print("  2. Ensure GOOD LIGHTING (no shadows)")
    print("  3. Show the FRONT/LABEL of product to camera")
    print("  4. Keep item STEADY for 2-3 seconds")
    print("  5. Check debug_frame.jpg to see what camera captured")
    print("  6. Make sure item is from the trained model list")
else:
    print(f"\n[SUCCESS] {len(detections)} detections found!")
    print("  Detection is working! Frontend should also work now.")
    print("  If frontend still not working, check browser console for errors.")
