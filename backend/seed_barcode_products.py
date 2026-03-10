"""
Seed Barcode Products Script
Updates the database with barcode information for specific products
"""
import os
import sys
sys.path.append(os.path.dirname(__file__))

from models import SessionLocal, Product

# Barcode mapping for products
BARCODE_PRODUCTS = [
    {
        "name": "Bisconni Chocolate Chip Cookies",
        "barcode": "8961102882845",
        "price": 50.0,
        "expected_weight_g": 100.0,
        "inventory": 50
    },
    {
        "name": "Colgate Maximum Cavity Protection",
        "barcode": "8886950051062",
        "price": 120.0,
        "expected_weight_g": 75.0,
        "inventory": 50
    },
    {
        "name": "Kurkure Chutney Chaska",
        "barcode": "8964002347353",
        "price": 30.0,
        "expected_weight_g": 62.0,
        "inventory": 50
    },
    {
        "name": "LU Candi Biscuit",
        "barcode": "8961003020315",
        "price": 25.0,
        "expected_weight_g": 60.0,
        "inventory": 50
    },
    {
        "name": "LU Oreo Biscuit",
        "barcode": "8961003026010",
        "price": 35.0,
        "expected_weight_g": 55.2,
        "inventory": 50
    },
    {
        "name": "Lays Masala",
        "barcode": "8964002345595",
        "price": 20.0,
        "expected_weight_g": 18.0,
        "inventory": 50
    },
    {
        "name": "Lifebuoy Total Protect Soap",
        "barcode": "8961014264630",
        "price": 40.0,
        "expected_weight_g": 123.0,
        "inventory": 50
    },
    {
        "name": "Lipton Yellow Label Tea",
        "barcode": "8720608622924",
        "price": 250.0,
        "expected_weight_g": 94.0,
        "inventory": 50
    },
    {
        "name": "Peek Freans Sooper Biscuit",
        "barcode": "8964003592950",
        "price": 45.0,
        "expected_weight_g": 95.0,
        "inventory": 50
    },
    {
        "name": "Safeguard Bar Soap Pure White",
        "barcode": "8001841420677",
        "price": 60.0,
        "expected_weight_g": 122.0,
        "inventory": 50
    },
    {
        "name": "Tapal Danedar",
        "barcode": "8961103600578",
        "price": 280.0,
        "expected_weight_g": 238.0,
        "inventory": 50
    }
]

def seed_barcode_products():
    """Update or create products with barcode information"""
    db = SessionLocal()
    
    print("🔄 Seeding barcode products...")
    print("=" * 60)
    
    updated_count = 0
    created_count = 0
    
    # Get starting class_id before the loop
    max_product = db.query(Product).order_by(Product.class_id.desc()).first()
    next_class_id = (max_product.class_id + 1) if max_product else 0
    
    for idx, product_data in enumerate(BARCODE_PRODUCTS):
        barcode = product_data["barcode"]
        
        # Check if product with this barcode already exists
        existing_product = db.query(Product).filter(Product.barcode == barcode).first()
        
        if existing_product:
            # Update existing product
            existing_product.name = product_data["name"]
            existing_product.price = product_data["price"]
            existing_product.expected_weight_g = product_data["expected_weight_g"]
            existing_product.inventory = product_data["inventory"]
            print(f"✓ Updated: {product_data['name']} (ID: {existing_product.id})")
            updated_count += 1
        else:
            # Create new product with incrementing class_id
            new_product = Product(
                class_id=next_class_id,
                name=product_data["name"],
                barcode=barcode,
                price=product_data["price"],
                expected_weight_g=product_data["expected_weight_g"],
                inventory=product_data["inventory"]
            )
            db.add(new_product)
            print(f"✅ Created: {product_data['name']} (Class ID: {next_class_id})")
            created_count += 1
            next_class_id += 1  # Increment for next product
    
    db.commit()
    
    print("=" * 60)
    print(f"✅ Seeding complete!")
    print(f"   Created: {created_count} products")
    print(f"   Updated: {updated_count} products")
    print(f"   Total barcode products: {len(BARCODE_PRODUCTS)}")
    
    # Display all products with barcodes
    print("\n" + "=" * 60)
    print("📋 Products with barcodes in database:")
    print("=" * 60)
    
    all_barcode_products = db.query(Product).filter(Product.barcode.isnot(None)).all()
    for prod in all_barcode_products:
        print(f"  ID: {prod.id:3d} | Class: {prod.class_id:3d} | Barcode: {prod.barcode}")
        print(f"       {prod.name}")
        print(f"       Price: ${prod.price:.2f} | Weight: {prod.expected_weight_g}g | Stock: {prod.inventory}")
        print()
    
    db.close()

if __name__ == "__main__":
    seed_barcode_products()
