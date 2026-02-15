from flask import Blueprint, request, jsonify
from models import SessionLocal, Product, TransactionLog, CartItem
from sqlalchemy import func, desc
from datetime import datetime, timedelta

admin_dashboard_bp = Blueprint('admin_dashboard', __name__)

def verify_token(request):
    """Helper function to verify admin token"""
    from routes.admin_auth import active_sessions
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token not in active_sessions:
        return None
    return active_sessions[token]

@admin_dashboard_bp.route('/admin/metrics', methods=['GET'])
def get_metrics():
    """Get dashboard metrics"""
    try:
        admin = verify_token(request)
        if not admin:
            return jsonify({'error': 'Unauthorized'}), 401
        
        db = SessionLocal()
        
        # Calculate metrics
        # Total sales (sum of all completed transactions)
        total_sales = db.query(func.sum(TransactionLog.total_amount))\
            .filter(TransactionLog.payment_status == 'completed')\
            .scalar() or 0
        
        # Daily transactions (transactions from today)
        today = datetime.now().date()
        daily_transactions = db.query(func.count(TransactionLog.id))\
            .filter(func.date(TransactionLog.timestamp) == today)\
            .scalar() or 0
        
        # Low stock alerts (products with inventory < 10)
        low_stock_count = db.query(func.count(Product.id))\
            .filter(Product.inventory < 10)\
            .scalar() or 0
        
        # Active users (approximation based on recent transactions)
        week_ago = datetime.now() - timedelta(days=7)
        active_users = db.query(func.count(func.distinct(TransactionLog.id)))\
            .filter(TransactionLog.timestamp >= week_ago)\
            .scalar() or 0
        
        # Get sales data for charts (last 7 days)
        sales_by_day = []
        for i in range(7):
            day = datetime.now().date() - timedelta(days=i)
            day_sales = db.query(func.sum(TransactionLog.total_amount))\
                .filter(func.date(TransactionLog.timestamp) == day)\
                .filter(TransactionLog.payment_status == 'completed')\
                .scalar() or 0
            sales_by_day.append({
                'date': day.strftime('%Y-%m-%d'),
                'sales': float(day_sales)
            })
        
        # Get top products
        top_products = db.query(
            Product.name,
            func.count(CartItem.id).label('sales_count')
        ).join(CartItem, Product.id == CartItem.product_id)\
         .group_by(Product.id)\
         .order_by(desc('sales_count'))\
         .limit(5)\
         .all()
        
        top_products_data = [
            {'name': name, 'count': count}
            for name, count in top_products
        ]
        
        db.close()
        
        return jsonify({
            'metrics': {
                'total_sales': float(total_sales),
                'daily_transactions': daily_transactions,
                'low_stock_alerts': low_stock_count,
                'active_users': active_users
            },
            'charts': {
                'sales_by_day': sales_by_day,
                'top_products': top_products_data
            }
        }), 200
        
    except Exception as e:
        if db:
            db.close()
        return jsonify({'error': str(e)}), 500

@admin_dashboard_bp.route('/admin/products', methods=['GET'])
def get_all_products():
    """Get all products for inventory management"""
    try:
        admin = verify_token(request)
        if not admin:
            return jsonify({'error': 'Unauthorized'}), 401
        
        db = SessionLocal()
        products = db.query(Product).all()
        
        products_data = [
            {
                'id': p.id,
                'class_id': p.class_id,
                'name': p.name,
                'price': float(p.price),
                'inventory': p.inventory,
                'expected_weight_g': float(p.expected_weight_g) if p.expected_weight_g else None,
                'barcode': p.barcode,
                'image_url': p.image_url
            }
            for p in products
        ]
        
        db.close()
        
        return jsonify({'products': products_data}), 200
        
    except Exception as e:
        if db:
            db.close()
        return jsonify({'error': str(e)}), 500

@admin_dashboard_bp.route('/admin/products', methods=['POST'])
def add_product():
    """Add a new product"""
    try:
        admin = verify_token(request)
        if not admin:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        
        db = SessionLocal()
        
        new_product = Product(
            class_id=data.get('class_id'),
            name=data.get('name'),
            price=data.get('price'),
            inventory=data.get('inventory', 100),
            expected_weight_g=data.get('expected_weight_g'),
            barcode=data.get('barcode'),
            image_url=data.get('image_url')
        )
        
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        product_data = {
            'id': new_product.id,
            'class_id': new_product.class_id,
            'name': new_product.name,
            'price': float(new_product.price),
            'inventory': new_product.inventory,
            'expected_weight_g': float(new_product.expected_weight_g) if new_product.expected_weight_g else None,
            'barcode': new_product.barcode,
            'image_url': new_product.image_url
        }
        
        db.close()
        
        return jsonify({
            'message': 'Product added successfully',
            'product': product_data
        }), 201
        
    except Exception as e:
        if db:
            db.rollback()
            db.close()
        return jsonify({'error': str(e)}), 500

@admin_dashboard_bp.route('/admin/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update a product"""
    try:
        admin = verify_token(request)
        if not admin:
            return jsonify({'error': 'Unauthorized'}), 401
        
        data = request.get_json()
        
        db = SessionLocal()
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            db.close()
            return jsonify({'error': 'Product not found'}), 404
        
        # Update fields
        if 'name' in data:
            product.name = data['name']
        if 'price' in data:
            product.price = data['price']
        if 'inventory' in data:
            product.inventory = data['inventory']
        if 'expected_weight_g' in data:
            product.expected_weight_g = data['expected_weight_g']
        if 'barcode' in data:
            product.barcode = data['barcode']
        if 'image_url' in data:
            product.image_url = data['image_url']
        
        db.commit()
        db.refresh(product)
        
        product_data = {
            'id': product.id,
            'class_id': product.class_id,
            'name': product.name,
            'price': float(product.price),
            'inventory': product.inventory,
            'expected_weight_g': float(product.expected_weight_g) if product.expected_weight_g else None,
            'barcode': product.barcode,
            'image_url': product.image_url
        }
        
        db.close()
        
        return jsonify({
            'message': 'Product updated successfully',
            'product': product_data
        }), 200
        
    except Exception as e:
        if db:
            db.rollback()
            db.close()
        return jsonify({'error': str(e)}), 500

@admin_dashboard_bp.route('/admin/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    try:
        admin = verify_token(request)
        if not admin:
            return jsonify({'error': 'Unauthorized'}), 401
        
        db = SessionLocal()
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
            db.close()
            return jsonify({'error': 'Product not found'}), 404
        
        db.delete(product)
        db.commit()
        db.close()
        
        return jsonify({'message': 'Product deleted successfully'}), 200
        
    except Exception as e:
        if db:
            db.rollback()
            db.close()
        return jsonify({'error': str(e)}), 500

@admin_dashboard_bp.route('/admin/transactions', methods=['GET'])
def get_transactions():
    """Get all transactions with optional filtering"""
    try:
        admin = verify_token(request)
        if not admin:
            return jsonify({'error': 'Unauthorized'}), 401
        
        db = SessionLocal()
        
        # Get query parameters for filtering
        search = request.args.get('search', '')
        sort_by = request.args.get('sort_by', 'date_desc')  # date_desc, date_asc, amount_desc, amount_asc
        
        query = db.query(TransactionLog)
        
        # Apply search filter
        if search:
            query = query.filter(TransactionLog.id.like(f'%{search}%'))
        
        # Apply sorting
        if sort_by == 'date_desc':
            query = query.order_by(desc(TransactionLog.timestamp))
        elif sort_by == 'date_asc':
            query = query.order_by(TransactionLog.timestamp)
        elif sort_by == 'amount_desc':
            query = query.order_by(desc(TransactionLog.total_amount))
        elif sort_by == 'amount_asc':
            query = query.order_by(TransactionLog.total_amount)
        
        transactions = query.all()
        
        transactions_data = [
            {
                'id': t.id,
                'timestamp': t.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'total_amount': float(t.total_amount),
                'payment_method': t.payment_method,
                'payment_status': t.payment_status,
                'details': t.details
            }
            for t in transactions
        ]
        
        db.close()
        
        return jsonify({'transactions': transactions_data}), 200
        
    except Exception as e:
        if db:
            db.close()
        return jsonify({'error': str(e)}), 500
