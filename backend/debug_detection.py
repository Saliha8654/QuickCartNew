"""
Debug script to test hybrid detection components
"""
import cv2
import sys
import os
sys.path.append(os.path.dirname(__file__))

from detection import predict_image, load_model
from barcode_detection import detect_barcodes
from hybrid_detection import get_hybrid_service

def test_components():
    print("🔍 Testing detection components...")
    
    # Test 1: Camera capture
    print("\n1. Testing camera capture...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("❌ Camera not available")
        return
    
    success, frame = cap.read()
    if not success:
        print("❌ Failed to capture frame")
        cap.release()
        return
    
    print("✅ Frame captured successfully")
    print(f"   Frame shape: {frame.shape}")
    
    # Test 2: Object detection
    print("\n2. Testing object detection...")
    try:
        detections = predict_image(frame)
        print(f"✅ Object detection completed: {len(detections)} detections")
        for i, det in enumerate(detections[:3]):  # Show first 3
            print(f"   Detection {i+1}: Class {det.get('class')}, Score {det.get('score'):.2f}")
    except Exception as e:
        print(f"❌ Object detection failed: {e}")
    
    # Test 3: Barcode detection
    print("\n3. Testing barcode detection...")
    try:
        barcodes = detect_barcodes(frame)
        print(f"✅ Barcode detection completed: {len(barcodes)} barcodes")
        for i, bc in enumerate(barcodes[:3]):  # Show first 3
            print(f"   Barcode {i+1}: {bc.get('value', 'N/A')} ({bc.get('type', 'UNKNOWN')})")
    except Exception as e:
        print(f"❌ Barcode detection failed: {e}")
    
    # Test 4: Hybrid service
    print("\n4. Testing hybrid detection service...")
    try:
        hybrid_service = get_hybrid_service()
        result = hybrid_service.hybrid_detect(frame)
        print(f"✅ Hybrid detection completed")
        print(f"   Success: {result.get('success')}")
        print(f"   Method: {result.get('method')}")
        if result.get('product'):
            print(f"   Product: {result['product'].get('name')}")
        print(f"   Message: {result.get('message')}")
    except Exception as e:
        print(f"❌ Hybrid detection failed: {e}")
        import traceback
        traceback.print_exc()
    
    cap.release()
    print("\n✅ Component testing completed!")

if __name__ == "__main__":
    test_components()