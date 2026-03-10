"""Update weights for specific products based on user measurements."""
import sys
import os

# Add the backend directory to sys.path to import from backend
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

from models import SessionLocal, Product

def update_weights():
    db = SessionLocal()
    try:
        updates = [
            {"name": "Safeguard", "weight": 122.0},
            {"name": "Lifebuoy", "weight": 123.0},
            {"name": "Lipton", "weight": 94.0}
        ]
        
        for update in updates:
            product = db.query(Product).filter(Product.name.like(f"%{update['name']}%")).first()
            if product:
                old_weight = product.expected_weight_g
                product.expected_weight_g = update['weight']
                db.commit()
                print(f"✅ Updated {product.name}: {old_weight}g -> {update['weight']}g")
            else:
                print(f"❌ Product matching '{update['name']}' not found")
                
    except Exception as e:
        print(f"❌ Error updating weights: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_weights()
