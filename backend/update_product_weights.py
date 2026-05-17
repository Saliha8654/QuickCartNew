"""Update product weights in database"""
from models import SessionLocal, Product

def update_weights():
    db = SessionLocal()
    
    # Product name to weight mapping (in grams)
    product_weights = {
        "Tapal Danedar": 85.0,
        "Lifebuoy": 4.0,
        "Colgate": 1.0,
        "Lipton Yellow Label": 4.4,
        "Chocolate Chip Cookies": 36.0,
        "Safeguard Soap": 3.0,
        "Oreo": 38.6,
        "Kurkure": 34.0,
    }


    
    print("Updating product weights in database...")
    print("=" * 60)
    
    # Get all products
    products = db.query(Product).all()
    
    updated_count = 0
    for product in products:
        # Try to match product name (case-insensitive, partial match)
        for product_name, weight in product_weights.items():
            if product_name.lower() in product.name.lower() or product.name.lower() in product_name.lower():
                old_weight = product.expected_weight_g
                product.expected_weight_g = weight
                print(f"✅ Updated: {product.name}")
                print(f"   Weight: {old_weight}g → {weight}g")
                updated_count += 1
                break
    
    # Commit changes
    db.commit()
    
    print("=" * 60)
    print(f"Updated {updated_count} products")
    print("\nAll products with weights:")
    print("=" * 60)
    
    products = db.query(Product).all()
    for p in products:
        weight_str = f"{p.expected_weight_g}g" if p.expected_weight_g else "Not set"
        print(f"  {p.name}: {weight_str}")
    
    db.close()

if __name__ == "__main__":
    update_weights()
