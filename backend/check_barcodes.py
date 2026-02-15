from models import SessionLocal, Product

db = SessionLocal()
products = db.query(Product).filter(Product.barcode != None).all()
print(f'✅ Products with barcodes: {len(products)}')
for p in products[:10]:
    print(f'  {p.id}: {p.name} - Barcode: {p.barcode}, ClassID: {p.class_id}')
db.close()
