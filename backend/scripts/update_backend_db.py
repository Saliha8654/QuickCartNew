import sqlite3
import os

db_path = 'c:\\Users\\Saliha Mahnoor\\Desktop\\QuickCart\\backend\\quickcart.db'

def update_db():
    try:
        if not os.path.exists(db_path):
            print(f"❌ Database not found at {db_path}")
            return
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        updates = [
            ("Safeguard%", 122.0),
            ("Lifebuoy%", 123.0),
            ("Lipton%", 94.0)
        ]
        
        for name_pattern, weight in updates:
            cursor.execute("UPDATE products SET expected_weight_g = ? WHERE name LIKE ?", (weight, name_pattern))
            if cursor.rowcount > 0:
                print(f"✅ Updated matching '{name_pattern[:-1]}' to {weight}g")
            else:
                print(f"❌ Product matching '{name_pattern[:-1]}' not found")
        
        # Also, let's clear the cart to avoid stale detections
        cursor.execute("DELETE FROM cart")
        print("✅ Cart cleared to avoid stale detections")
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_db()
