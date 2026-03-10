from flask import Blueprint, request, jsonify
import serial
import time
import threading
from models import SessionLocal, Product, CartItem

# Create blueprint
weight_sensor_bp = Blueprint("weight_sensor", __name__)

# Global variables for serial connection and weight tracking
serial_connection = None
current_weight = 0.0
weight_lock = threading.Lock()
is_monitoring = False
monitor_thread = None

def init_serial_connection(port=None, baudrate=9600):
    """Initialize serial connection to weight sensor"""
    global serial_connection, is_monitoring, monitor_thread
    try:
        # If already connected, close it first
        if serial_connection and serial_connection.is_open:
            serial_connection.close()

        if port:
            serial_connection = serial.Serial(port, baudrate, timeout=1)
            time.sleep(2) # Give Arduino time to reset
            serial_connection.write(b'r\n') # Start continuous reading mode
            print(f"✅ Connected to weight sensor on {port}")
        else:
            # Try common ports, prioritize COM5 which worked before
            common_ports = ['COM5', 'COM3', 'COM4', 'COM8', 'COM9', '/dev/ttyUSB0', '/dev/ttyACM0']
            for p in common_ports:
                try:
                    # Use a shorter timeout for probing
                    serial_connection = serial.Serial(p, baudrate, timeout=0.1)
                    time.sleep(2) # Give Arduino time to reset
                    serial_connection.write(b'r\n') # Start continuous reading mode
                    # Set back to a reasonable timeout for reading
                    serial_connection.timeout = 1
                    print(f"✅ Connected to weight sensor on {p}")
                    break
                except:
                    serial_connection = None
                    continue
        
        if serial_connection and serial_connection.is_open:
            # Start background monitoring thread if not already running
            if not is_monitoring:
                is_monitoring = True
                monitor_thread = threading.Thread(target=background_weight_monitor, daemon=True)
                monitor_thread.start()
                print("🚀 Background weight monitor started")
            return True
        else:
            print("❌ Could not connect to weight sensor on any common port")
            return False
            
    except Exception as e:
        print(f"❌ Error connecting to weight sensor: {e}")
        return False

def background_weight_monitor():
    """Background thread to continuously read from sensor"""
    global serial_connection, current_weight, is_monitoring
    print("📋 Background monitor loop entered")
    
    while is_monitoring:
        if serial_connection and serial_connection.is_open:
            try:
                line = serial_connection.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    # Log to file for debugging
                    try:
                        with open("sensor_debug.log", "a") as f:
                            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - RAW: '{line}'\n")
                    except:
                        pass

                    # Detect calibration status
                    if "not calibrated" in line.lower() or "run 'c500'" in line.lower():
                        with weight_lock:
                            current_weight = -999.0
                        print("⚠️ Scale NOT calibrated. Please send 'c500' command.")
                        continue
                    
                    if "calibration loaded" in line.lower():
                        print("📦 Sensor confirmed: Persistent calibration LOADED.")
                        if current_weight == -999.0:
                            with weight_lock:
                                current_weight = 0.0
                        continue

                    # Parse logic
                    weight = parse_weight_line(line)
                    if weight is not None:
                        with weight_lock:
                            current_weight = weight
                        print(f"✅ Background weight updated: {weight}g")
                        try:
                            with open("sensor_debug.log", "a") as f:
                                f.write(f"✅ Parsed: {weight}g\n")
                        except:
                            pass
                    else:
                        if len(line) > 0 and not any(term in line for term in ["=====", "HX711"]):
                             print(f"ℹ️ Received non-weight line: '{line}'")
            except Exception as e:
                print(f"⚠️ Monitor error: {e}")
                time.sleep(1) 
        else:
            time.sleep(2)
            init_serial_connection()
        
        time.sleep(0.01)

def parse_weight_line(line):
    """Centralized parsing logic for weight sensor lines"""
    # 1. Try JSON parsing first
    try:
        import json
        data = json.loads(line)
        if isinstance(data, dict):
            if 'weight_g' in data: return float(data['weight_g'])
            if 'weight' in data: return float(data['weight'])
    except:
        pass

    # 2. Try parsing "Weight: 23.45g" format
    if "Weight:" in line:
        import re
        match = re.search(r"Weight:\s*([-+]?\d*\.?\d+)", line)
        if match: return float(match.group(1))
    
    # 3. If we see a number followed by 'g' or 'grams'
    import re
    match = re.search(r"([-+]?\d*\.?\d+)\s*(g|grams)", line.lower())
    if match: return float(match.group(1))

    # 4. Pure numeric
    clean_line = line.replace("g", "").replace("grams", "").strip()
    if clean_line.replace(".", "").replace("-", "").isdigit() and len(line) < 15:
        try:
            return float(clean_line)
        except:
            pass
            
    return None

def read_weight_from_sensor():
    """Returns the most recent weight captured by the background monitor"""
    global current_weight
    # Ensure connection is lazy-initialized
    if not serial_connection or not serial_connection.is_open:
        init_serial_connection()
        
    with weight_lock:
        return current_weight

@weight_sensor_bp.route("/weight_sensor/connect", methods=["POST"])
def connect_weight_sensor():
    """Connect to weight sensor"""
    data = request.get_json()
    port = data.get("port", None)
    baudrate = data.get("baudrate", 9600)
    
    if init_serial_connection(port, baudrate):
        return jsonify({"status": "connected", "message": "Weight sensor connected successfully"})
    else:
        return jsonify({"status": "error", "message": "Failed to connect to weight sensor"}), 500

@weight_sensor_bp.route("/weight_sensor/read", methods=["GET"])
def read_current_weight():
    """Get current weight reading"""
    weight = read_weight_from_sensor()
    return jsonify({"weight_g": weight, "unit": "g"})

@weight_sensor_bp.route("/weight_sensor/verify_cart", methods=["POST"])
def verify_cart_weight():
    """Verify total cart weight against expected weight"""
    try:
        # Calculate expected total weight from cart items
        db = SessionLocal()
        cart_items = db.query(CartItem).all()
        
        expected_total_weight = 0.0
        items_with_weights = []
        
        for item in cart_items:
            if item.product and item.product.expected_weight_g:
                expected_weight = item.product.expected_weight_g * item.quantity
                expected_total_weight += expected_weight
                items_with_weights.append({
                    "product_id": item.product_id,
                    "product_name": item.product.name,
                    "quantity": item.quantity,
                    "expected_weight_g": expected_weight
                })
        
        db.close()
        
        # Get latest weight from monitor
        actual_weight = read_weight_from_sensor()
        
        # Verification with tolerance (10% by default as per frontend logic)
        data = request.get_json() or {}
        tolerance = data.get("tolerance", 0.1)  # 10% tolerance
        
        lower_bound = expected_total_weight * (1 - tolerance)
        upper_bound = expected_total_weight * (1 + tolerance)
        
        is_verified = lower_bound <= actual_weight <= upper_bound
        
        print(f"📊 Verification: Expected={expected_total_weight}g, Actual={actual_weight}g, Matched={is_verified}")
        
        return jsonify({
            "verified": is_verified,
            "expected_total_g": expected_total_weight,
            "actual_weight_g": actual_weight,
            "tolerance_percent": tolerance * 100,
            "lower_bound_g": lower_bound,
            "upper_bound_g": upper_bound,
            "items": items_with_weights
        })
        
    except Exception as e:
        print(f"❌ Weight verification error: {e}")
        return jsonify({"error": str(e)}), 500

@weight_sensor_bp.route("/weight_sensor/calibrate", methods=["POST"])
def calibrate_weight_sensor():
    """Send calibration command to sensor"""
    global serial_connection
    # Ensure connection is lazy-initialized
    if not serial_connection or not serial_connection.is_open:
        print("🔄 Calibration requested but not connected. Attempting connection...")
        init_serial_connection()
    
    data = request.get_json(silent=True) or {}
    weight = data.get("weight", 500)
    
    if serial_connection and serial_connection.is_open:
        try:
            cmd = f"c{weight}\n"
            serial_connection.write(cmd.encode())
            print(f"📡 Sent calibration command: {cmd.strip()}")
            return jsonify({"status": "success", "message": f"Sent calibration command for {weight}g"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "Weight sensor not connected and could not be initialized"}), 500

@weight_sensor_bp.route("/weight_sensor/tare", methods=["POST"])
def tare_weight_sensor():
    """Send tare command to sensor"""
    global serial_connection
    # Ensure connection is lazy-initialized
    if not serial_connection or not serial_connection.is_open:
        init_serial_connection()

    if serial_connection and serial_connection.is_open:
        try:
            serial_connection.write(b"t\n")
            print("📡 Sent tare command")
            return jsonify({"status": "success", "message": "Sent tare command"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        return jsonify({"status": "error", "message": "Weight sensor not connected"}), 500

@weight_sensor_bp.route("/weight_sensor/disconnect", methods=["POST"])
def disconnect_weight_sensor():
    """Disconnect from weight sensor"""
    global serial_connection, is_monitoring
    try:
        is_monitoring = False
        if serial_connection and serial_connection.is_open:
            serial_connection.close()
            serial_connection = None
        return jsonify({"status": "disconnected", "message": "Weight sensor disconnected"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
