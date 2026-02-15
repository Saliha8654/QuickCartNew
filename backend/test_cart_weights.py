"""Test if cart API returns expected weights"""
import requests

API_URL = "http://localhost:5000/api"

print("Testing cart API for expected weights...")
print("=" * 60)

try:
    response = requests.get(f"{API_URL}/cart", timeout=5)
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
        
        print(f"Cart has {len(items)} item(s)")
        print()
        
        for item in items:
            name = item.get('name', 'Unknown')
            qty = item.get('quantity', 0)
            expected_weight = item.get('expected_weight_g', 'NOT FOUND')
            
            print(f"Product: {name}")
            print(f"  Quantity: {qty}")
            print(f"  Expected Weight (per unit): {expected_weight}g")
            
            if expected_weight != 'NOT FOUND' and expected_weight is not None:
                total_weight = expected_weight * qty
                print(f"  Total Expected Weight: {total_weight}g")
                print(f"  Status: ✅ Weight field present")
            else:
                print(f"  Status: ❌ Weight field MISSING")
            print()
    else:
        print(f"Error: API returned status {response.status_code}")
        
except Exception as e:
    print(f"Error: {e}")

print("=" * 60)
