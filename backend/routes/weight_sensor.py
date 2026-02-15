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

def init_serial_connection(port=None, baudrate=9600):
    """Initialize serial connection to weight sensor"""
    global serial_connection
    try:
        if port:
            serial_connection = serial.Serial(port, baudrate, timeout=1)
            print(f"✅ Connected to weight sensor on {port}")
            return True
        else:
            # Try common ports
            common_ports = ['COM3', 'COM4', 'COM5', '/dev/ttyUSB0', '/dev/ttyACM0']
            for port in common_ports:
                try:
                    serial_connection = serial.Serial(port, baudrate, timeout=1)
                    print(f"✅ Connected to weight sensor on {port}")
                    return True
                except:
                    continue
            print("❌ Could not connect to weight sensor on any common port")
            return False
    except Exception as e:
        print(f"❌ Error connecting to weight sensor: {e}")
        return False

def read_weight_from_sensor():
    """Read weight from serial sensor"""
    global serial_connection, current_weight
    if not serial_connection or not serial_connection.is_open:
        return None
    
    try:
        # Read data from sensor (implementation depends on your sensor)
        # This is a generic implementation - you may need to adjust based on your sensor
        line = serial_connection.readline().decode('utf-8').strip()
        if line:
            # Parse weight value (adjust based on your sensor's output format)
            # Example: "Weight: 150.5g" or just "150.5"
            if ':' in line:
                weight_str = line.split(':')[1].replace('g', '').strip()
            else:
                weight_str = line.replace('g', '').strip()
            
            weight = float(weight_str)
            with weight_lock:
                current_weight = weight
            return weight
    except Exception as e:
        print(f"❌ Error reading weight: {e}")
        return None

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
    if weight is not None:
        return jsonify({"weight_g": weight, "unit": "g"})
    else:
        return jsonify({"weight_g": current_weight, "unit": "g"})

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
        
        # Get actual weight from sensor
        actual_weight = read_weight_from_sensor()
        if actual_weight is None:
            actual_weight = current_weight
        
        # Verification with tolerance (5% by default)
        data = request.get_json()
        tolerance = data.get("tolerance", 0.05)  # 5% tolerance
        
        lower_bound = expected_total_weight * (1 - tolerance)
        upper_bound = expected_total_weight * (1 + tolerance)
        
        is_verified = lower_bound <= actual_weight <= upper_bound
        
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

@weight_sensor_bp.route("/weight_sensor/disconnect", methods=["POST"])
def disconnect_weight_sensor():
    """Disconnect from weight sensor"""
    global serial_connection
    try:
        if serial_connection and serial_connection.is_open:
            serial_connection.close()
            serial_connection = None
        return jsonify({"status": "disconnected", "message": "Weight sensor disconnected"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500