import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from flask import Flask
from flask_cors import CORS
from backend import config
from init_db import init_db
from routes.products import products_bp
from routes.cart import cart_bp
from routes.detect import detect_bp
from routes.weight import weight_bp
from routes.weight_sensor import weight_sensor_bp
from routes.admin_auth import admin_auth_bp
from routes.admin_dashboard import admin_dashboard_bp
from routes.payment import payment_bp
from detection import load_model

def create_app():
    app = Flask(__name__)
    CORS(app)
    init_db(seed=True)
    app.register_blueprint(products_bp, url_prefix="/api")
    app.register_blueprint(cart_bp, url_prefix="/api")
    app.register_blueprint(detect_bp, url_prefix="/api")
    app.register_blueprint(weight_bp, url_prefix="/api")
    app.register_blueprint(weight_sensor_bp, url_prefix="/api")
    app.register_blueprint(admin_auth_bp, url_prefix="/api")
    app.register_blueprint(admin_dashboard_bp, url_prefix="/api")
    app.register_blueprint(payment_bp, url_prefix="/api")
    return app

if __name__ == "__main__":
    print("🚀 Starting QuickCart backend server...")
    
    # ✅ Preload detection model
    print("🔍 Loading AI detection model at startup...")
    load_model()

    # ✅ Initialize weight sensor at startup
    try:
        from routes.weight_sensor import init_serial_connection
        print("⚖️ Initializing weight sensor...")
        init_serial_connection()
    except Exception as e:
        print(f"⚠️ Could not initialize weight sensor at startup: {e}")

    app = create_app()
    app.run(debug=config.DEBUG, host='0.0.0.0', port=config.APP_PORT)