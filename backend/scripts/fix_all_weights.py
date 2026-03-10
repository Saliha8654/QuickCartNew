import sqlite3
import os

db_path = 'c:\\Users\\Saliha Mahnoor\\Desktop\\QuickCart\\backend\\quickcart.db'

def update_all_soap_weights():
    try:
        if not os.path.exists(db_path):
            print(f"❌ Database not found at {db_path}")
            return
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Comprehensive updates for Safeguard, Lifebuoy, and Lipton
        # based on user measurements (Safeguard: 23g, Lifebuoy: 24g, Lipton: 19g)
        updates = [
            ("Safeguard%", 23.0),
            ("Lifebuoy%", 24.0),
            ("Lipton%", 19.0)
        ]
        
        for name_pattern, weight in updates:
            cursor.execute("UPDATE products SET expected_weight_g = ? WHERE name LIKE ?", (weight, name_pattern))
            if cursor.rowcount > 0:
                print(f"✅ Updated matching '{name_pattern[:-1]}' to {weight}g ({cursor.rowcount} items)")
            else:
                print(f"❌ Product matching '{name_pattern[:-1]}' not found")
        
        # Clear cart to remove wrong items
        cursor.execute("DELETE FROM cart")
        print("✅ Cart cleared to ensure next detection is fresh.")
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_all_soap_weights()
