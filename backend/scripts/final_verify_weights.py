import sqlite3
import os

db_path = 'c:\\Users\\Saliha Mahnoor\\Desktop\\QuickCart\\backend\\quickcart.db'

def final_verify():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, expected_weight_g FROM products WHERE name LIKE 'Safeguard%' OR name LIKE 'Lifebuoy%' OR name LIKE 'Lipton%'")
        rows = cursor.fetchall()
        for row in rows:
            print(f"Product: {row[0]}, Weight: {row[1]}g")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    final_verify()
