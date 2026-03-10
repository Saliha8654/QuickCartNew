"""Check what the app sees as Safeguard's weight."""
import sys
import os
from models import SessionLocal, Product

db = SessionLocal()
prods = db.query(Product).filter(Product.name.like("%Safeguard%")).all()
print(f"Count: {len(prods)}")
for p in prods:
    print(f"ID: {p.id}, Name: {p.name}, Weight: {p.expected_weight_g}g")
db.close()
