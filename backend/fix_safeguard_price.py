
from models import SessionLocal, Product

def update_safeguard_price():
    db = SessionLocal()
    # Find Safeguard soap (usually class_id 18 or 19 depending on which script was used)
    # Let's search by name
    safeguards = db.query(Product).filter(Product.name.like('%Safeguard%')).all()
    
    if not safeguards:
        print("❌ Safeguard soap not found in database.")
        db.close()
        return

    print(f"Found {len(safeguards)} Safeguard products.")
    for p in safeguards:
        print(f"Updating {p.name} from Rs {p.price} to Rs 160.0")
        p.price = 160.0
        # Also ensure weight is 23g as requested before
        p.expected_weight_g = 23.0
    
    db.commit()
    print("✅ Database updated successfully!")
    db.close()

if __name__ == "__main__":
    update_safeguard_price()
