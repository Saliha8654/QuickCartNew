"""Update weights in the active database (MySQL)."""
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from backend.models import SessionLocal, Product, CartItem
    from backend import config
    
    print(f"Connecting to: {config.DATABASE_URL}")
    
    db = SessionLocal()
    
    updates = [
        ("Safeguard%", 23.0),
        ("Lifebuoy%", 24.0),
        ("Lipton%", 19.0)
    ]
    
    for name_pattern, weight in updates:
        # Using SQLAlchemy filter with like
        products = db.query(Product).filter(Product.name.like(name_pattern)).all()
        if products:
            for p in products:
                old_weight = p.expected_weight_g
                p.expected_weight_g = weight
                print(f"✅ Updated {p.name}: {old_weight}g -> {weight}g")
        else:
            print(f"❌ No product found matching '{name_pattern}'")
            
    # Clear cart
    db.query(CartItem).delete()
    print("✅ Cart cleared.")
    
    db.commit()
    db.close()
    print("🚀 Database update complete!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
    pass # Script runs on import logic above or I'll just run it
