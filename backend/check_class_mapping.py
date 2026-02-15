"""Check if model class IDs match database class IDs"""
from ultralytics import YOLO
from models import SessionLocal, Product

print("=" * 70)
print("CLASS ID MAPPING CHECK")
print("=" * 70)

# Load model
model = YOLO('models/best.pt')
print(f"\nMODEL HAS {len(model.names)} CLASSES:")
for idx, name in model.names.items():
    print(f"  Class {idx}: {name}")

# Load database products
db = SessionLocal()
products = db.query(Product).all()
print(f"\n\nDATABASE HAS {len(products)} PRODUCTS:")
for p in sorted(products, key=lambda x: x.class_id if x.class_id is not None else 999):
    print(f"  Class {p.class_id}: {p.name}")

print("\n" + "=" * 70)
print("MISMATCH CHECK")
print("=" * 70)

# Check for mismatches
model_classes = {idx: name for idx, name in model.names.items()}
db_classes = {p.class_id: p.name for p in products if p.class_id is not None}

print(f"\nModel classes: {len(model_classes)}")
print(f"Database classes: {len(db_classes)}")

mismatches = []
for class_id, model_name in model_classes.items():
    if class_id in db_classes:
        db_name = db_classes[class_id]
        if model_name.strip() != db_name.strip():
            mismatches.append((class_id, model_name, db_name))
            print(f"\n[MISMATCH] Class {class_id}:")
            print(f"  Model: {model_name}")
            print(f"  DB:    {db_name}")
    else:
        print(f"\n[MISSING IN DB] Class {class_id}: {model_name}")

missing_in_model = set(db_classes.keys()) - set(model_classes.keys())
if missing_in_model:
    print(f"\n[CLASSES IN DB BUT NOT IN MODEL]: {missing_in_model}")

if not mismatches and not missing_in_model:
    print("\n✅ ALL CLASS IDS MATCH PERFECTLY!")
else:
    print(f"\n❌ FOUND {len(mismatches)} MISMATCHES")

db.close()
