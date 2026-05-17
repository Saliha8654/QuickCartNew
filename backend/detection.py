from ultralytics import YOLO
import os
import cv2
import numpy as np
from PIL import Image
import io
import sys

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

try:
    import config
except ImportError:
    try:
        from backend import config
    except ImportError:
        # Fallback: create a minimal config
        class config:
            MODEL_PATH = "models/best.pt"

_model = None

def load_model():
    """Load YOLO model once and cache it."""
    global _model
    if _model is None:
        model_path = os.path.join(os.path.dirname(__file__), config.MODEL_PATH)
        print(f"📦 Loading YOLO model from: {model_path}")
        try:
            _model = YOLO(model_path)
            print("✅ YOLO model loaded successfully!")
        except Exception as e:
            print("❌ Error loading YOLO model:", e)
            _model = None
    return _model


def predict_image(file_like, conf=0.5, iou=0.4):
    """Run YOLO prediction and return clean JSON-style results."""
    model = load_model()
    
    # Check if model loaded successfully
    if model is None:
        print("❌ YOLO model not loaded")
        return []
    
    try:
        # Convert file-like object to numpy array for YOLO
        if hasattr(file_like, 'read'):
            # Read the file content
            file_bytes = file_like.read()
            # Convert to PIL Image
            image = Image.open(io.BytesIO(file_bytes))
            # Convert to numpy array (RGB format)
            image_array = np.array(image)
            # Convert RGB to BGR for OpenCV/YOLO
            if len(image_array.shape) == 3 and image_array.shape[2] == 3:
                image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        elif isinstance(file_like, str):
            # If it's a file path, read it
            image_array = cv2.imread(file_like)
            if image_array is None:
                print(f"❌ Could not read image from path: {file_like}")
                return []
        elif isinstance(file_like, np.ndarray):
            # Already a numpy array
            image_array = file_like
        else:
            # Try to use it directly
            image_array = file_like
        
        # Run prediction with improved parameters for multiple object detection
        # Lower confidence threshold and adjust NMS threshold for better multi-object detection
        # Using 15% confidence threshold for MAXIMUM detection sensitivity
        results = model.predict(source=image_array, conf=0.15, iou=0.5,  imgsz=320, verbose=False)
        detections = []

        if results and len(results) > 0 and hasattr(results[0], 'boxes') and results[0].boxes is not None:
            boxes = results[0].boxes
            for box in boxes:
                if box is not None and hasattr(box, 'xyxy') and box.xyxy is not None:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    conf_score = float(box.conf[0])
                    cls_id = int(box.cls[0])
                    
                    # Only include detections with reasonable confidence (lowered to 15% for MAXIMUM sensitivity)
                    if conf_score >= 0.15:
                        detections.append({
                            "class": cls_id,
                            "score": conf_score,
                            "bbox": [int(x1), int(y1), int(x2), int(y2)]
                        })

        # Sort detections by confidence (highest first) and limit to top 10 to prevent overload
        detections.sort(key=lambda x: x['score'], reverse=True)
        return detections[:10]  # Limit to top 10 detections
    
    except Exception as e:
        print(f"❌ Detection error: {e}")
        import traceback
        traceback.print_exc()
        return []