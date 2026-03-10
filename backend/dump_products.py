from models import SessionLocal, Product
import sys
import os

import config
print(f"DEBUG: Using DATABASE_URL = {config.DATABASE_URL}")

try:
    db = SessionLocal()
    products = db.query(Product).all()
    print("-" * 50)
    print(f"Found {len(products)} products.")
    for p in products:
        print(f"ID: {p.id}, Class: {p.class_id}, Name: {p.name}, Weight: {p.expected_weight_g}g")
    print("-" * 50)
    db.close()
except Exception as e:
    print(f"ERROR: {e}")
