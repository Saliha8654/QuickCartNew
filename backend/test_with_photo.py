"""Test detection with a photo"""
import cv2
from detection import predict_image

# Test with your own photo - replace 'your_photo.jpg' with actual photo path
photo_path = input("Enter path to your product photo (or press Enter for test_frame.jpg): ").strip()
if not photo_path:
    photo_path = "test_frame.jpg"

# Load image
frame = cv2.imread(photo_path)
if frame is None:
    print(f"❌ Could not load image: {photo_path}")
    exit(1)

print(f"✅ Loaded image: {frame.shape}")

# Test detection with ultra-low confidence (10%)
detections = predict_image(frame, conf=0.10)
print(f"\n🔍 Detections found: {len(detections)}")

for i, det in enumerate(detections):
    print(f"\nDetection {i+1}:")
    print(f"  Class: {det['class']}")
    print(f"  Confidence: {det['score']*100:.1f}%")
    print(f"  Bounding Box: {det['bbox']}")

if len(detections) == 0:
    print("\n❌ No detections found!")
    print("Possible reasons:")
    print("  - Photo too dark/blurred")
    print("  - Product not in training data")
    print("  - Wrong angle/perspective")
    print("  - Product too small in frame")
else:
    print(f"\n✅ SUCCESS! Found {len(detections)} objects!")
