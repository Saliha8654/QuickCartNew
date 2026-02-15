import os, yaml
import sys
sys.path.append(os.path.dirname(__file__))
from models import Base, engine, SessionLocal, Product

def init_db(seed=True, dataset_yaml_path=None):
    Base.metadata.create_all(bind=engine)
    if seed:
        db = SessionLocal()
        if db.query(Product).count() == 0:
            # Try to load from data.yaml in project root
            if dataset_yaml_path is None:
                yaml_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data.yaml")
                if os.path.exists(yaml_path):
                    dataset_yaml_path = yaml_path
            
            if dataset_yaml_path and os.path.exists(dataset_yaml_path):
                with open(dataset_yaml_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                names = data.get("names") or []
                print(f"✅ Loading {len(names)} products from data.yaml...")
                
                # Define realistic prices and weights for your products
                product_prices = [
                    15.0, 50.0, 120.0, 80.0, 60.0, 40.0, 250.0, 20.0, 70.0, 30.0,
                    25.0, 35.0, 40.0, 45.0, 90.0, 180.0, 220.0, 15.0, 160.0, 45.0,
                    200.0, 25.0, 170.0, 190.0, 280.0
                ]
                product_weights = [
                    46.8, 250.0, 75.0, 500.0, 500.0, 200.0, 238.0, 18.0, 62.0, 60.0,
                    19.0, 55.2, 34.0, 34.0, 96.0, 95.0, 190.0, 13.2, 175.0, 250.0,
                    160.0, 30.0, 95.0, 95.0, 100.0
                ]
                
                for idx, name in enumerate(names):
                    price = product_prices[idx] if idx < len(product_prices) else 50.0
                    weight = product_weights[idx] if idx < len(product_weights) else 100.0
                    p = Product(
                        class_id=idx,
                        name=name,
                        price=price,
                        expected_weight_g=weight,
                        inventory=100
                    )
                    db.add(p)
                db.commit()
                print(f"✅ Successfully added {len(names)} products to database!")
            else:
                print("⚠️ No data.yaml found, adding sample products...")
                samples = [
                    Product(class_id=0, name="Sample Item A 100g", price=100, expected_weight_g=100, inventory=50),
                    Product(class_id=1, name="Sample Item B 200g", price=200, expected_weight_g=200, inventory=50),
                ]
                db.add_all(samples)
                db.commit()
        db.close()

if __name__ == "__main__":
    init_db(seed=True)
