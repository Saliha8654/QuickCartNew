"""
Update barcodes for known products using class_id -> EAN mapping.

Run after running migrate_db.py so that the `barcode` column exists.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from models import SessionLocal
import config

load_dotenv()

print(f"Connecting to database: {config.DATABASE_URL}")

# IMPORTANT: class_id mapping here follows comments in update_products.py
BARCODE_DATA = [
    # class_id, barcode, comment
    (0,  "8961102882845", "Bisconni Chocolate Chip Cookies"),
    (2,  "8886950051062", "Colgate Maximum Cavity Protection"),
    (8,  "8964002347353", "Kurkure Chutney Chaska"),
    (9,  "8961003020315", "LU Candi Biscuit"),
    (10, "8961003026010", "LU Oreo Biscuit"),
    (12, "8964002345595", "Lays Masala"),
    (14, "8961014264630", "Lifebuoy Total Protect Soap"),
    (15, "8720608622924", "Lipton Yellow Label Tea"),
    (17, "8964003592950", "Peek Freans Sooper Biscuit"),
    (18, "8001841420677", "Safeguard Bar Soap Pure White"),
    (23, "8961103600578", "Tapal Danedar"),
]

try:
    # Use SQLAlchemy engine for database operations
    engine = create_engine(config.DATABASE_URL)
    
    with engine.connect() as connection:
        print("✅ Connected to database\n")
        print("🔄 Updating product barcodes...\n")

        for class_id, barcode, label in BARCODE_DATA:
            connection.execute(
                text("""
                UPDATE products
                SET barcode = :barcode
                WHERE class_id = :class_id
                """),
                {"barcode": barcode, "class_id": class_id},
            )

            result = connection.execute(
                text("SELECT name FROM products WHERE class_id = :class_id"),
                {"class_id": class_id}
            )
            row = result.fetchone()
            name = row[0] if row else label

            print(f"✓ Set barcode {barcode} for class_id={class_id:2d} -> {name}")

        connection.commit()

        print("\n" + "=" * 70)
        print("✅ All barcodes updated successfully!")
        print("=" * 70)

except Exception as e:
    print(f"\n❌ Barcode update failed: {e}")
    import traceback
    traceback.print_exc()