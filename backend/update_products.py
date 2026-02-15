"""
Update existing products with realistic prices and weights
"""
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

# Parse database URL
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://qc_user:qc_pass@127.0.0.1:3306/quickcart?charset=utf8mb4")
parts = DATABASE_URL.replace("mysql+pymysql://", "").split("@")
user_pass = parts[0].split(":")
user = user_pass[0]
password = user_pass[1]
host_db = parts[1].split("/")
host_port = host_db[0].split(":")
host = host_port[0]
port = int(host_port[1]) if len(host_port) > 1 else 3306
database = host_db[1].split("?")[0]

print(f"Connecting to database: {database} at {host}:{port}")

# Product prices and weights (matching the 25 products in data.yaml)
product_data = [
    (0, 15.0, 46.8),    # Bisconni Chocolate Chip Cookies
    (1, 50.0, 250.0),   # Coca Cola Can
    (2, 120.0, 75.0),   # Colgate
    (3, 80.0, 500.0),   # Fanta
    (4, 60.0, 500.0),   # Fresher Guava
    (5, 40.0, 200.0),   # Fruita Vitals
    (6, 250.0, 238.0),  # Islamabad Tea
    (7, 20.0, 18.0),    # Kolson Slanty
    (8, 70.0, 62.0),    # Kurkure
    (9, 30.0, 60.0),    # LU Candi
    (10, 25.0, 19.0),   # LU Oreo
    (11, 35.0, 55.2),   # LU Prince
    (12, 40.0, 34.0),   # Lays Masala
    (13, 45.0, 34.0),   # Lays Wavy
    (14, 90.0, 96.0),   # Lifebuoy
    (15, 180.0, 95.0),  # Lipton Tea
    (16, 220.0, 190.0), # Meezan Tea
    (17, 15.0, 13.2),   # Peek Freans
    (18, 160.0, 175.0), # Safeguard
    (19, 45.0, 250.0),  # Shezan Apple
    (20, 200.0, 160.0), # Sunsilk
    (21, 25.0, 30.0),   # Super Crisp
    (22, 170.0, 95.0),  # Supreme Tea
    (23, 190.0, 95.0),  # Tapal Danedar
    (24, 280.0, 100.0)  # Vaseline
]

try:
    connection = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset='utf8mb4'
    )
    
    cursor = connection.cursor()
    
    print("✅ Connected to database\n")
    print("🔄 Updating product prices and weights...\n")
    
    for class_id, price, weight in product_data:
        cursor.execute("""
            UPDATE products 
            SET price = %s, expected_weight_g = %s 
            WHERE class_id = %s
        """, (price, weight, class_id))
        
        # Get product name
        cursor.execute("SELECT name FROM products WHERE class_id = %s", (class_id,))
        result = cursor.fetchone()
        name = result[0] if result else "Unknown"
        
        print(f"✓ Updated: {name:<50} Rs.{price:>6.2f}  {weight:>6.1f}g")
    
    connection.commit()
    
    print("\n" + "="*70)
    print("✅ All products updated successfully!")
    print("="*70)
    
    cursor.close()
    connection.close()

except Exception as e:
    print(f"\n❌ Update failed: {e}")
    import traceback
    traceback.print_exc()
