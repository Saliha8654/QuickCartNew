"""Deep dive into MySQL to find the 125g Safeguard."""
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

try:
    from backend.models import SessionLocal, Product, CartItem
    from backend import config
    
    print(f"--- DB Diagnostic ---")
    print(f"URL: {config.DATABASE_URL}")
    
    db = SessionLocal()
    
    # 1. Find ANY product with expected_weight_g = 125
    print("\n1. Products with weight 125.0:")
    w125 = db.query(Product).filter(Product.expected_weight_g == 125.0).all()
    for p in w125:
        print(f"   ID: {p.id} | Name: {p.name} | Weight: {p.expected_weight_g}")
    if not w125: print("   None found.")
    
    # 2. Find ALL products with 'Safeguard' in name
    print("\n2. All 'Safeguard' products:")
    safeguards = db.query(Product).filter(Product.name.like("%Safeguard%")).all()
    for p in safeguards:
        print(f"   ID: {p.id} | Name: {p.name} | Weight: {p.expected_weight_g}")
    if not safeguards: print("   None found.")
    
    # 3. Check Cart Items
    print("\n3. Current Cart Items:")
    cart_items = db.query(CartItem).all()
    for c in cart_items:
        p = c.product
        print(f"   CartID: {c.id} | ProdID: {p.id} | Name: {p.name} | UnitPrice: {c.unit_price} | ExpectedInDB: {p.expected_weight_g}")
    if not cart_items: print("   Cart is empty.")
    
    # 4. FORCE UPDATE Safeguard to 23.0 IF it's wrong
    print("\n4. Applying Force Update...")
    for p in safeguards:
        if p.expected_weight_g != 23.0:
            print(f"   Fixing {p.name}: {p.expected_weight_g} -> 23.0")
            p.expected_weight_g = 23.0
    
    db.commit()
    db.close()
    print("\nDiagnostic and Fix Complete.")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
