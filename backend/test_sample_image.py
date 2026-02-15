"""
Test script for hybrid detection using a sample image
"""
import cv2
import sys
import os
import numpy as np
sys.path.append(os.path.dirname(__file__))

from detection import predict_image
from barcode_detection import detect_barcodes
from hybrid_detection import get_hybrid_service

def create_sample_image():
    """Create a simple test image"""
    # Create a black image with some shapes
    img = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Add some colored rectangles to simulate objects
    cv2.rectangle(img, (100, 100), (200, 200), (0, 255, 0), -1)  # Green rectangle
    cv2.rectangle(img, (300, 150), (450, 250), (255, 0, 0), -1)  # Blue rectangle
    cv2.circle(img, (500, 300), 50, (0, 0, 255), -1)  # Red circle
    
    # Add some text
    cv2.putText(img, "Test Image", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    return img

def test_with_sample_image():
    print("🔍 Testing detection components with sample image...")
    
    # Create a sample image
    frame = create_sample_image()
    print("✅ Sample image created")
    print(f"   Image shape: {frame.shape}")
    
    # Test 1: Object detection
    print("\n1. Testing object detection...")
    try:
        detections = predict_image(frame)
        print(f"✅ Object detection completed: {len(detections)} detections")
        for i, det in enumerate(detections[:3]):  # Show first 3
            print(f"   Detection {i+1}: Class {det.get('class')}, Score {det.get('score'):.2f}")
    except Exception as e:
        print(f"❌ Object detection failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Barcode detection
    print("\n2. Testing barcode detection...")
    try:
        barcodes = detect_barcodes(frame)
        print(f"✅ Barcode detection completed: {len(barcodes)} barcodes")
        for i, bc in enumerate(barcodes[:3]):  # Show first 3
            print(f"   Barcode {i+1}: {bc.get('value', 'N/A')} ({bc.get('type', 'UNKNOWN')})")
    except Exception as e:
        print(f"❌ Barcode detection failed: {e}")
    
    # Test 3: Hybrid service
    print("\n3. Testing hybrid detection service...")
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
    
    print("\n✅ Component testing completed!")

if __name__ == "__main__":
    test_with_sample_image()