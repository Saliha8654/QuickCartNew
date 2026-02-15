from flask import Blueprint, request, jsonify
from models import SessionLocal, Admin
from sqlalchemy.exc import IntegrityError
import secrets

admin_auth_bp = Blueprint('admin_auth', __name__)

# In-memory session store (use Redis in production)
active_sessions = {}

@admin_auth_bp.route('/admin/signup', methods=['POST'])
def admin_signup():
    """Register a new admin account"""
    try:
        data = request.get_json()
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        
        if not email or not username or not password:
            return jsonify({'error': 'Email, username, and password are required'}), 400
        
        db = SessionLocal()
        
        # Create new admin
        new_admin = Admin(email=email, username=username)
        new_admin.set_password(password)
        
        db.add(new_admin)
        db.commit()
        db.refresh(new_admin)
        
        # Create session token
        token = secrets.token_hex(32)
        active_sessions[token] = {
            'admin_id': new_admin.id,
            'email': new_admin.email,
            'username': new_admin.username
        }
        
        db.close()
        
        return jsonify({
            'message': 'Admin account created successfully',
            'token': token,
            'admin': {
                'id': new_admin.id,
                'email': new_admin.email,
                'username': new_admin.username
            }
        }), 201
        
    except IntegrityError as e:
        db.rollback()
        db.close()
        return jsonify({'error': 'Email or username already exists'}), 409
    except Exception as e:
        if db:
            db.rollback()
            db.close()
        return jsonify({'error': str(e)}), 500

@admin_auth_bp.route('/admin/login', methods=['POST'])
def admin_login():
    """Login to admin account"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        db = SessionLocal()
        
        # Find admin by email
        admin = db.query(Admin).filter(Admin.email == email).first()
        
        if not admin or not admin.check_password(password):
            db.close()
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not admin.is_active:
            db.close()
            return jsonify({'error': 'Account is deactivated'}), 403
        
        # Create session token
        token = secrets.token_hex(32)
        active_sessions[token] = {
            'admin_id': admin.id,
            'email': admin.email,
            'username': admin.username
        }
        
        db.close()
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'admin': {
                'id': admin.id,
                'email': admin.email,
                'username': admin.username
            }
        }), 200
        
    except Exception as e:
        if db:
            db.close()
        return jsonify({'error': str(e)}), 500

@admin_auth_bp.route('/admin/logout', methods=['POST'])
def admin_logout():
    """Logout from admin account"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if token in active_sessions:
            del active_sessions[token]
        
        return jsonify({'message': 'Logout successful'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_auth_bp.route('/admin/verify', methods=['GET'])
def verify_admin():
    """Verify admin token"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if token not in active_sessions:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        session_data = active_sessions[token]
        
        return jsonify({
            'valid': True,
            'admin': session_data
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
