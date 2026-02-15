"""Update Safeguard weight"""
from models import SessionLocal, Product

db = SessionLocal()

# Update Safeguard
safeguard = db.query(Product).filter(Product.name.like("%Safeguard%")).first()
if safeguard:
    safeguard.expected_weight_g = 125.0
    db.commit()
    print(f"✅ Updated: {safeguard.name}")
    print(f"   Weight: 175.0g → 125.0g")
else:
    print("❌ Safeguard not found")

db.close()
