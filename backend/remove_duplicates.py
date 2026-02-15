"""Remove duplicate products from database"""
from models import SessionLocal, Product

db = SessionLocal()

print("=" * 70)
print("REMOVING DUPLICATE PRODUCTS")
print("=" * 70)

# Get products with class_id > 24 (these are duplicates not in model)
duplicates = db.query(Product).filter(Product.class_id > 24).all()

print(f"\nFound {len(duplicates)} duplicate products to remove:")
for p in duplicates:
    print(f"  Class {p.class_id}: {p.name}")

if duplicates:
    confirm = input(f"\nDelete these {len(duplicates)} products? (yes/no): ")
    if confirm.lower() == 'yes':
        for p in duplicates:
            db.delete(p)
        db.commit()
        print(f"\n✅ Deleted {len(duplicates)} duplicate products!")
        
        # Verify
        remaining = db.query(Product).all()
        print(f"✅ Database now has {len(remaining)} products (should be 25)")
    else:
        print("\n❌ Cancelled - no products deleted")
else:
    print("\n✅ No duplicates found!")

db.close()
