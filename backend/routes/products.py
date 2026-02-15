from flask import Blueprint, request, jsonify
from models import SessionLocal, Product
from sqlalchemy import or_

products_bp = Blueprint("products", __name__)
@products_bp.get("/products")
def list_products():
    db = SessionLocal()
    q = request.args.get("q","")
    if q:
        # Search by name OR barcode
        rows = db.query(Product).filter(
            or_(
                Product.name.ilike(f"%{q}%"),
                Product.barcode.ilike(f"%{q}%")
            )
        ).all()
    else:
        rows = db.query(Product).all()
    out = []
    for p in rows:
        out.append({
            "id": p.id,
            "class_id": p.class_id,
            "name": p.name,
            "price": p.price,
            "expected_weight_g": p.expected_weight_g,
            "inventory": p.inventory,
            "image_url": p.image_url,
            "barcode": p.barcode
        })
    db.close()
    return jsonify(out)
@products_bp.post("/products")
def create_product():
    body = request.get_json(force=True)
    db = SessionLocal()
    p = Product(
        class_id=int(body["class_id"]),
        name=body["name"],
        price=float(body["price"]),
        expected_weight_g=body.get("expected_weight_g"),
        inventory=int(body.get("inventory", 100)),
        image_url=body.get("image_url")
    )
    db.add(p); db.commit(); pid = p.id; db.close()
    return jsonify({"id":pid}), 201
