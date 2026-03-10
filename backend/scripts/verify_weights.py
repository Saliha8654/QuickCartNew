import sqlite3

def verify_db():
    try:
        conn = sqlite3.connect('quickcart.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, expected_weight_g FROM products WHERE name LIKE 'Safeguard%' OR name LIKE 'Lifebuoy%' OR name LIKE 'Lipton%'")
        rows = cursor.fetchall()
        for row in rows:
            print(f"Product: {row[0]}, Weight: {row[1]}g")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify_db()
