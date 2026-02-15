"""Update product barcodes in database"""
from models import SessionLocal, Product

def update_barcodes():
    db = SessionLocal()
    
    # Product name to barcode mapping
    product_barcodes = {
        "Kurkure": "8964002347353",
        "Lipton Yellow Label": "8720608622924",
        "Safeguard": "8001841420677",
        "Colgate": "8886950051062",
        "Tapal Danedar": "8961103600578",
        "Oreo": "8961003062010",
        "Lifebuoy": "8961014264630",
        "Chocolate Chip": "8961102882845",
    }
    
    print("Updating product barcodes in database...")
    print("=" * 60)
    
    # Get all products
    products = db.query(Product).all()
    
    updated_count = 0
    for product in products:
        # Try to match product name (case-insensitive, partial match)
        for product_name, barcode in product_barcodes.items():
            if product_name.lower() in product.name.lower() or product.name.lower() in product_name.lower():
                old_barcode = product.barcode
                product.barcode = barcode
                print(f"✅ Updated: {product.name}")
                print(f"   Barcode: {old_barcode} → {barcode}")
                updated_count += 1
                break
    
    # Commit changes
    db.commit()
    
    print("=" * 60)
    print(f"Updated {updated_count} products")
    print("\nAll products with barcodes:")
    print("=" * 60)
    
    products = db.query(Product).all()
    for p in products:
        barcode_str = p.barcode if p.barcode else "Not set"
        print(f"  {p.name}: {barcode_str}")
    
    db.close()

if __name__ == "__main__":
    update_barcodes()
