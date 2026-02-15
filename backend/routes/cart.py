from flask import Blueprint, request, jsonify
from models import SessionLocal, CartItem, Product, TransactionLog
cart_bp = Blueprint("cart", __name__)
@cart_bp.get("/cart")
def get_cart():
    db = SessionLocal()
    items = db.query(CartItem).all()
    total = 0.0
    out = []
    for c in items:
        lt = c.unit_price * c.quantity
        total += lt
        out.append({
            "id": c.id,
            "product_id": c.product_id,
            "name": c.product.name,
            "price": c.unit_price,
            "quantity": c.quantity,
            "line_total": lt,
            "weight_verified": c.weight_verified,
            "image_url": c.product.image_url,
            "expected_weight_g": c.product.expected_weight_g  # Add expected weight from product
        })
    db.close()
    return jsonify({"items": out, "total": total})
@cart_bp.post("/cart")
def add_to_cart():
    body = request.get_json(force=True)
    pid = int(body["product_id"])
    qty = int(body.get("quantity", 1))
    db = SessionLocal()
    prod = db.query(Product).filter(Product.id == pid).first()
    if not prod:
        db.close()
        return jsonify({"error": "Product not found"}), 404
    
    # Check inventory
    if prod.inventory < qty:
        db.close()
        return jsonify({"error": "Insufficient inventory"}), 400
    
    # Check if item already in cart
    existing_item = db.query(CartItem).filter(CartItem.product_id == pid).first()
    if existing_item:
        existing_item.quantity += qty
        db.commit()
    else:
        item = CartItem(product_id=pid, quantity=qty, unit_price=prod.price)
        db.add(item)
        db.commit()
    
    db.close()
    return jsonify({"message": "added"}), 201
@cart_bp.patch("/cart/<int:item_id>")
def update_item(item_id):
    body = request.get_json(force=True)
    qty = int(body.get("quantity", 1))
    db = SessionLocal()
    it = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not it:
        db.close()
        return jsonify({"error": "not found"}), 404
    
    # Check inventory when increasing quantity
    prod = db.query(Product).filter(Product.id == it.product_id).first()
    if prod and qty > it.quantity:
        diff = qty - it.quantity
        if prod.inventory < diff:
            db.close()
            return jsonify({"error": "Insufficient inventory"}), 400
    
    it.quantity = max(1, qty)
    db.commit()
    db.close()
    return jsonify({"message": "updated"})
@cart_bp.delete("/cart/<int:item_id>")
def remove_item(item_id):
    db = SessionLocal()
    it = db.query(CartItem).filter(CartItem.id==item_id).first()
    if not it: db.close(); return jsonify({"error":"not found"}),404
    db.delete(it); db.commit(); db.close()
    return jsonify({"message":"removed"})
@cart_bp.delete("/cart")
def clear_cart():
    db = SessionLocal()
    db.query(CartItem).delete()
    db.commit()
    db.close()
    return jsonify({"message": "cleared"})

@cart_bp.post("/cart/checkout")
def checkout():
    """Finalize cart and update inventory"""
    db = SessionLocal()
    try:
        items = db.query(CartItem).all()
        if not items:
            db.close()
            return jsonify({"error": "Cart is empty"}), 400
        
        total = 0.0
        details = []
        
        # Update inventory and prepare transaction details
        for cart_item in items:
            prod = db.query(Product).filter(Product.id == cart_item.product_id).first()
            if not prod:
                db.close()
                return jsonify({"error": f"Product {cart_item.product_id} not found"}), 404
            
            if prod.inventory < cart_item.quantity:
                db.close()
                return jsonify({"error": f"Insufficient inventory for {prod.name}"}), 400
            
            # Deduct from inventory
            prod.inventory -= cart_item.quantity
            
            line_total = cart_item.unit_price * cart_item.quantity
            total += line_total
            details.append({
                "name": prod.name,
                "quantity": cart_item.quantity,
                "unit_price": cart_item.unit_price,
                "total": line_total
            })
        
        # Create transaction log
        import json
        transaction = TransactionLog(
            details=json.dumps(details),
            total_amount=total,
            payment_status="pending"
        )
        db.add(transaction)
        
        # Clear cart
        db.query(CartItem).delete()
        
        db.commit()
        transaction_id = transaction.id
        db.close()
        
        return jsonify({
            "message": "Checkout successful",
            "transaction_id": transaction_id,
            "total": total
        }), 200
    
    except Exception as e:
        db.rollback()
        db.close()
        return jsonify({"error": str(e)}), 500
