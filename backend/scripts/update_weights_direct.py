import sqlite3
import os

db_path = 'c:\\Users\\Saliha Mahnoor\\Desktop\\QuickCart\\quickcart.db'

def update_db():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        updates = [
            ("Safeguard%", 23.0),
            ("Lifebuoy%", 24.0),
            ("Lipton%", 19.0)
        ]
        
        for name_pattern, weight in updates:
            cursor.execute("UPDATE products SET expected_weight_g = ? WHERE name LIKE ?", (weight, name_pattern))
            if cursor.rowcount > 0:
                print(f"✅ Updated {name_pattern[:-1]} to {weight}g")
            else:
                print(f"❌ Product {name_pattern[:-1]} not found")
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_db()
