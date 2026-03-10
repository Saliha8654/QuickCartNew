"""Update Safeguard weight"""
from models import SessionLocal, Product

db = SessionLocal()

# Update Safeguard
safeguard = db.query(Product).filter(Product.name.like("%Safeguard%")).first()
if safeguard:
    safeguard.expected_weight_g = 122.0
    db.commit()
    print(f"✅ Updated: {safeguard.name}")
    print(f"   Weight: 23.0g → 122.0g")
else:
    print("❌ Safeguard not found")

db.close()
