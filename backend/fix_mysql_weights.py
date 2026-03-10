"""Update weights for Safeguard, Lifebuoy, and Lipton in MySQL."""
from models import SessionLocal, Product, CartItem

db = SessionLocal()

updates = [
    ("%Safeguard%", 23.0),
    ("%Lifebuoy%", 24.0),
    ("%Lipton%", 19.0),
    ("%Yellow Label%", 19.0)
]

print("Starting MySQL weight updates...")

for pattern, weight in updates:
    prods = db.query(Product).filter(Product.name.like(pattern)).all()
    if prods:
        for p in prods:
            old = p.expected_weight_g
            p.expected_weight_g = weight
            print(f"✅ Updated {p.name}: {old}g -> {weight}g")
    else:
        print(f"❌ No product matching '{pattern}'")

# Clear cart to be sure
db.query(CartItem).delete()
print("✅ Cart cleared.")

db.commit()
db.close()
print("🚀 Done!")
