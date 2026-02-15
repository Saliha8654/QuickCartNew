import cv2
import numpy as np
import os
import tempfile
from typing import List, Dict, Any

# ---------------------------------------------------------------------------
# Barcode backends
# ---------------------------------------------------------------------------
# 1) ZXing via pyzxing  (preferred when available)
# 2) OpenCV's built‑in BarcodeDetector (fallback when pyzxing is missing)

_ZXING_AVAILABLE = False
_ZXING_READER = None
_OPENCV_BARCODE_DETECTOR = None

# Try ZXing wrapper first
try:
    import pyzxing  # type: ignore

    _ZXING_READER = pyzxing.BarCodeReader()
    _ZXING_AVAILABLE = True
    print("✅ ZXing (pyzxing) barcode reader initialized")
except Exception as e:
    print("⚠️ ZXing/pyzxing not available, will try OpenCV BarcodeDetector instead:", e)

# If ZXing is not available, fall back to OpenCV's BarcodeDetector (requires
# opencv-contrib-python >= 4.5).
if not _ZXING_AVAILABLE:
    try:
        if hasattr(cv2, "barcode_BarcodeDetector"):
            _OPENCV_BARCODE_DETECTOR = cv2.barcode_BarcodeDetector()
            print("✅ OpenCV BarcodeDetector initialized (fallback barcode reader)")
        else:
            print("⚠️ OpenCV build does not include barcode_BarcodeDetector; barcode detection disabled")
    except Exception as e:  # pragma: no cover - very environment specific
        _OPENCV_BARCODE_DETECTOR = None
        print("⚠️ Failed to init OpenCV BarcodeDetector; barcode detection disabled:", e)


def _save_frame_to_temp(frame) -> str:
    """Save an OpenCV BGR frame to a temporary PNG file and return its path."""
    fd, path = tempfile.mkstemp(suffix=".png")
    os.close(fd)
    # Ensure frame is uint8
    if frame is None:
        return path
    if frame.dtype != "uint8":
        frame_to_save = frame.astype("uint8")
    else:
        frame_to_save = frame
    cv2.imwrite(path, frame_to_save)
    return path


def detect_barcodes(frame) -> List[Dict[str, Any]]:
    """Detect multiple barcodes in a BGR frame.

    Prefer ZXing (via pyzxing) when available, otherwise fall back to OpenCV's
    :class:`BarcodeDetector` if it exists in the current OpenCV build.

    Returns a list of dictionaries:
    [{
        "value": "8961102882845",
        "type": "EAN_13" | "QR_CODE" | ...,
        "bbox": [x1, y1, x2, y2] or None
    }, ...]
    """
    if frame is None:
        return []
    
    # Validate frame is a numpy array
    if not isinstance(frame, np.ndarray):
        print(f"[WARNING] barcode_detection: frame is {type(frame)}, expected numpy array")
        return []

    # ------------------------------------------------------------------
    # 1) ZXing backend (pyzxing)
    # ------------------------------------------------------------------
    if _ZXING_AVAILABLE and _ZXING_READER is not None:
        temp_path = _save_frame_to_temp(frame)
        barcodes: List[Dict[str, Any]] = []

        try:
            # pyzxing API: Different versions use different methods
            # Try decode first (single barcode), then decode_array (multiple barcodes)
            if hasattr(_ZXING_READER, 'decode_array'):
                results = _ZXING_READER.decode_array(temp_path) or []
            elif hasattr(_ZXING_READER, 'decode'):
                # Single barcode mode - wrap in list
                result = _ZXING_READER.decode(temp_path)
                # If result is a dict, wrap in list; if it's already a list, use it
                if isinstance(result, dict):
                    results = [result] if result else []
                elif isinstance(result, list):
                    results = result
                else:
                    results = []
            else:
                # Fallback to OpenCV
                results = []
        except Exception as zxing_error:
            print(f"[ERROR] pyzxing decode failed: {zxing_error}")
            import traceback
            traceback.print_exc()
            results = []

            for r in results:
                # Different pyzxing versions use slightly different keys; be defensive
                # Handle both dict and string results
                if isinstance(r, str):
                    # Direct string result
                    barcodes.append({
                        "value": r.strip(),
                        "type": "UNKNOWN",
                        "bbox": None,
                    })
                    continue
                
                if not isinstance(r, dict):
                    continue
                    
                value = (
                    r.get("raw_text")
                    or r.get("raw")
                    or r.get("text")
                    or r.get("parsed")
                )
                if not value:
                    continue

                btype = r.get("format") or r.get("type") or "UNKNOWN"

                # Try to get a bounding box if available
                bbox = None
                bounds = r.get("bounds") or r.get("rect") or r.get("position")
                if isinstance(bounds, dict):
                    # Common style: {"x":.., "y":.., "w":.., "h":..} or similar
                    x = bounds.get("x") or bounds.get("left")
                    y = bounds.get("y") or bounds.get("top")
                    w = bounds.get("w") or bounds.get("width")
                    h = bounds.get("h") or bounds.get("height")
                    if None not in (x, y, w, h):
                        bbox = [int(x), int(y), int(x + w), int(y + h)]
                elif isinstance(bounds, (list, tuple)) and len(bounds) == 4:
                    x, y, w, h = bounds
                    bbox = [int(x), int(y), int(x + w), int(y + h)]

                barcodes.append(
                    {
                        "value": str(value).strip(),
                        "type": str(btype),
                        "bbox": bbox,
                    }
                )
        finally:
            try:
                os.remove(temp_path)
            except OSError:
                pass

        return barcodes

    # ------------------------------------------------------------------
    # 2) OpenCV BarcodeDetector fallback
    # ------------------------------------------------------------------
    if _OPENCV_BARCODE_DETECTOR is None:
        # No backend available at all
        return []

    barcodes: List[Dict[str, Any]] = []
    try:
        # detectAndDecodeWithType returns: retval, decoded_info, decoded_type, points
        ok, decoded_info, decoded_type, points = _OPENCV_BARCODE_DETECTOR.detectAndDecodeWithType(frame)
    except Exception:
        # If OpenCV raises for any reason, treat as no detection instead of crashing
        return []

    if not ok or not decoded_info:
        return []

    # points is an array of shape (N, 4, 2) with corner coordinates
    for idx, value in enumerate(decoded_info):
        if not value:
            continue

        btype = None
        if decoded_type is not None and idx < len(decoded_type):
            btype = decoded_type[idx]
        btype = btype or "UNKNOWN"

        bbox = None
        if points is not None and len(points) > idx and len(points[idx]) >= 4:
            pts = points[idx]
            xs = [float(p[0]) for p in pts]
            ys = [float(p[1]) for p in pts]
            x1, y1, x2, y2 = min(xs), min(ys), max(xs), max(ys)
            bbox = [int(x1), int(y1), int(x2), int(y2)]

        barcodes.append(
            {
                "value": str(value).strip(),
                "type": str(btype),
                "bbox": bbox,
            }
        )

    return barcodes


def match_barcodes_to_detections(barcodes: List[Dict[str, Any]], detections: List[Dict[str, Any]], iou_threshold: float = 0.1):
    """Spatially match barcode boxes to YOLO detections using IoU / overlap.

    If a barcode has no bbox (ZXing didn't provide position), it is skipped for
    spatial matching. In that case detections will just not get barcode info.
    """

    def iou(box1, box2) -> float:
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        inter_w = max(0, x2 - x1)
        inter_h = max(0, y2 - y1)
        inter = inter_w * inter_h
        if inter <= 0:
            return 0.0
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = max(area1 + area2 - inter, 1e-6)
        return inter / union

    if not barcodes:
        return detections

    enriched: List[Dict[str, Any]] = []
    for det in detections:
        det_copy = dict(det)
        det_box = det_copy.get("bbox")
        if not det_box or len(det_box) != 4:
            enriched.append(det_copy)
            continue

        best_barcode = None
        best_score = 0.0

        for bc in barcodes:
            bc_box = bc.get("bbox")
            if not bc_box or len(bc_box) != 4:
                continue
            score = iou(det_box, bc_box)
            if score > best_score:
                best_score = score
                best_barcode = bc

        if best_barcode and best_score >= iou_threshold:
            det_copy["barcode_value"] = best_barcode["value"]
            det_copy["barcode_type"] = best_barcode.get("type")
            det_copy["barcode_iou"] = float(best_score)

        enriched.append(det_copy)

    return enriched
