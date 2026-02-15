"""
Quick script to check if products are loaded in database
"""
from models import SessionLocal, Product

db = SessionLocal()

print("\n" + "="*70)
print("📦 QUICKCART PRODUCT DATABASE")
print("="*70 + "\n")

products = db.query(Product).all()

if not products:
    print("❌ No products found in database!")
    print("Run: python init_db.py")
else:
    print(f"✅ Found {len(products)} products\n")
    print(f"{'ID':<5} {'Class':<7} {'Name':<50} {'Price':<10} {'Weight':<10} {'Stock':<8}")
    print("-" * 100)
    
    for p in products:
        print(f"{p.id:<5} {p.class_id:<7} {p.name:<50} Rs.{p.price:<8.2f} {p.expected_weight_g:<9.1f}g {p.inventory:<8}")

print("\n" + "="*70)
print(f"💰 Total Inventory Value: Rs. {sum(p.price * p.inventory for p in products):,.2f}")
print("="*70 + "\n")

db.close()
