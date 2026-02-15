"""Test barcode search functionality"""
import requests

API_URL = "http://localhost:5000/api"

def test_barcode_search():
    print("=" * 60)
    print("TESTING BARCODE SEARCH FUNCTIONALITY")
    print("=" * 60)
    
    # Test barcodes
    test_cases = [
        ("8964002347353", "Kurkure"),
        ("8720608622924", "Lipton Yellow Label"),
        ("8001841420677", "Safeguard"),
        ("8886950051062", "Colgate"),
        ("8961103600578", "Tapal Danedar"),
        ("8961003062010", "Oreo"),
        ("8961014264630", "Lifebuoy"),
        ("8961102882845", "Chocolate Chip"),
    ]
    
    print("\n1. Testing search by barcode:")
    print("-" * 60)
    
    for barcode, expected_product in test_cases:
        try:
            response = requests.get(f"{API_URL}/products?q={barcode}", timeout=5)
            if response.status_code == 200:
                products = response.json()
                if products:
                    product = products[0]
                    print(f"✅ Barcode {barcode}")
                    print(f"   Found: {product['name']}")
                    print(f"   Expected: {expected_product}")
                    if expected_product.lower() in product['name'].lower():
                        print(f"   Match: ✓")
                    else:
                        print(f"   Match: ✗ (Unexpected product)")
                else:
                    print(f"❌ Barcode {barcode}: No products found")
            else:
                print(f"❌ Barcode {barcode}: API error {response.status_code}")
        except Exception as e:
            print(f"❌ Barcode {barcode}: Error - {e}")
        print()
    
    print("\n2. Testing search by product name:")
    print("-" * 60)
    
    test_names = ["Kurkure", "Colgate", "Oreo"]
    for name in test_names:
        try:
            response = requests.get(f"{API_URL}/products?q={name}", timeout=5)
            if response.status_code == 200:
                products = response.json()
                print(f"✅ Search '{name}': Found {len(products)} product(s)")
                for p in products:
                    barcode = p.get('barcode', 'No barcode')
                    print(f"   - {p['name']} (Barcode: {barcode})")
            else:
                print(f"❌ Search '{name}': API error {response.status_code}")
        except Exception as e:
            print(f"❌ Search '{name}': Error - {e}")
        print()
    
    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_barcode_search()
