import sqlite3
import os

db_path = 'c:\\Users\\Saliha Mahnoor\\Desktop\\QuickCart\\quickcart.db'

def check_safeguard():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, expected_weight_g FROM products WHERE name LIKE '%Safeguard%'")
        rows = cursor.fetchall()
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Weight: {row[2]}g")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_safeguard()
