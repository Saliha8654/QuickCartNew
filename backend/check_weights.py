#!/usr/bin/env python3
"""
Script to check that product weights are properly set in the database
"""

import sys
import os

# Add the project root to the path so we can import backend modules
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from backend.models import SessionLocal, Product

def check_product_weights():
    """Check that all products have expected_weight_g values populated"""
    db = SessionLocal()
    
    try:
        # Get all products
        products = db.query(Product).all()
        
        print(f"Found {len(products)} products in the database:")
        print("-" * 80)
        print(f"{'ID':<3} {'Name':<40} {'Price':<8} {'Expected Weight (g)':<20}")
        print("-" * 80)
        
        missing_weights = []
        for product in products:
            weight_value = product.expected_weight_g
            weight_info = f"{weight_value}g" if weight_value is not None else "NOT SET"
            if weight_value is None:
                missing_weights.append(product)
            
            # Truncate long names for display
            name_str = str(product.name)
            name = name_str[:37] + "..." if len(name_str) > 37 else name_str
            print(f"{product.id:<3} {name:<40} ${product.price:<7.2f} {weight_info:<20}")
        
        print("-" * 80)
        print(f"\nSummary:")
        print(f"- Total products: {len(products)}")
        print(f"- Products with weights: {len(products) - len(missing_weights)}")
        print(f"- Products missing weights: {len(missing_weights)}")
        
        if missing_weights:
            print(f"\nProducts missing expected weights:")
            for product in missing_weights:
                print(f"  - ID {product.id}: {product.name}")
        else:
            print(f"\n✅ All products have expected weights set!")
            
        return len(missing_weights) == 0
        
    except Exception as e:
        print(f"❌ Error checking product weights: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("Checking product weights in database...")
    success = check_product_weights()
    sys.exit(0 if success else 1)