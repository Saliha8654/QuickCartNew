"""
Cooldown System Specific Test
Tests if cooldown is preventing legitimate detections
"""
import time
import sys
import os
sys.path.append(os.path.dirname(__file__))

from hybrid_detection import get_hybrid_service
import numpy as np

def test_cooldown_directly():
    """Test the cooldown system directly"""
    print("=" * 80)
    print("  COOLDOWN SYSTEM SPECIFIC TEST")
    print("=" * 80)
    
    print("\n🔍 Testing cooldown mechanism directly...")
    
    # Get hybrid service
    service = get_hybrid_service()
    
    # Test product ID and barcode
    product_id = 28  # Bisconni Chocolate Chip Cookies
    barcode = "8961102882845"
    
    print(f"\n🧪 Testing with:")
    print(f"   Product ID: {product_id}")
    print(f"   Barcode: {barcode}")
    print(f"   Cooldown period: {service.COOLDOWN_SECONDS} seconds")
    
    # Test 1: Initial state (should not be in cooldown)
    print(f"\n⏱️  Test 1: Initial state")
    in_cooldown = service._is_in_cooldown(product_id, barcode)
    print(f"   In cooldown: {in_cooldown} (Expected: False)")
    
    if in_cooldown:
        print("   ❌ ISSUE: Product should not be in cooldown initially!")
        # Clear cooldown for testing
        service._detection_history.clear()
        service._barcode_history.clear()
        print("   🛠️  Cleared cooldown history for testing")
        
        # Re-test
        in_cooldown = service._is_in_cooldown(product_id, barcode)
        print(f"   After clearing: In cooldown: {in_cooldown} (Expected: False)")
    
    # Test 2: Record a detection
    print(f"\n⏱️  Test 2: Recording detection")
    service._record_detection(product_id, barcode)
    print(f"   ✅ Detection recorded at {time.time():.1f}")
    
    # Test 3: Immediately check (should be in cooldown)
    print(f"\n⏱️  Test 3: Immediate recheck (should be in cooldown)")
    in_cooldown = service._is_in_cooldown(product_id, barcode)
    print(f"   In cooldown: {in_cooldown} (Expected: True)")
    
    if not in_cooldown:
        print("   ❌ ISSUE: Product should be in cooldown immediately after recording!")
    
    # Test 4: Wait for cooldown to expire
    print(f"\n⏱️  Test 4: Waiting for cooldown to expire ({service.COOLDOWN_SECONDS} seconds)")
    time.sleep(service.COOLDOWN_SECONDS + 0.1)  # Wait a bit more than cooldown
    
    in_cooldown = service._is_in_cooldown(product_id, barcode)
    print(f"   In cooldown: {in_cooldown} (Expected: False after {service.COOLDOWN_SECONDS}s)")
    
    if in_cooldown:
        print("   ❌ ISSUE: Product should NOT be in cooldown after expiration!")
    
    print(f"\n✅ Cooldown system test completed!")

def test_hybrid_detection_with_cooldown():
    """Test hybrid detection with cooldown simulation"""
    print("\n" + "=" * 80)
    print("  HYBRID DETECTION WITH COOLDOWN SIMULATION")
    print("=" * 80)
    
    print("\n🔍 Simulating detection scenario with cooldown...")
    
    service = get_hybrid_service()
    
    # Create a dummy frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    print(f"\n🧪 Detection Simulation:")
    print(f"   Cooldown period: {service.COOLDOWN_SECONDS} seconds")
    
    # Simulate multiple rapid detections
    for i in range(3):
        print(f"\n--- Detection #{i+1} ---")
        start_time = time.time()
        
        # Run hybrid detection
        result = service.hybrid_detect(frame, auto_add_to_cart=False)
        
        elapsed = time.time() - start_time
        print(f"   Result: {result['message']}")
        print(f"   Success: {result['success']}")
        print(f"   In cooldown: {result['in_cooldown']}")
        print(f"   Time taken: {elapsed:.2f}s")
        
        # Small delay between detections
        if i < 2:  # Don't sleep after last iteration
            time.sleep(1)

def test_manual_cooldown_reset():
    """Test manual cooldown reset"""
    print("\n" + "=" * 80)
    print("  MANUAL COOLDOWN RESET TEST")
    print("=" * 80)
    
    print("\n🔍 Testing manual cooldown reset...")
    
    service = get_hybrid_service()
    
    # Check current cooldown state
    print(f"\n📊 Current cooldown state:")
    print(f"   Detection history size: {len(service._detection_history)}")
    print(f"   Barcode history size: {len(service._barcode_history)}")
    
    if service._detection_history or service._barcode_history:
        print(f"   🧹 Clearing cooldown history...")
        service._detection_history.clear()
        service._barcode_history.clear()
        print(f"   ✅ Cooldown history cleared")
        print(f"   New detection history size: {len(service._detection_history)}")
        print(f"   New barcode history size: {len(service._barcode_history)}")
    else:
        print(f"   ✅ Cooldown history already clear")

def api_cooldown_test():
    """Test cooldown via API endpoints"""
    print("\n" + "=" * 80)
    print("  API COOLDOWN TEST")
    print("=" * 80)
    
    print("\n🔍 Testing cooldown via API endpoints...")
    
    try:
        import requests
        
        print(f"\n🧪 API Cooldown Test:")
        
        # Test 1: First detection
        print(f"\n--- API Call #1 ---")
        start_time = time.time()
        response1 = requests.post('http://localhost:5000/api/camera/detect/hybrid', 
                                json={'auto_add_to_cart': False}, 
                                timeout=10)
        elapsed1 = time.time() - start_time
        
        if response1.status_code == 200:
            result1 = response1.json()
            print(f"   Status: {response1.status_code} ✓")
            print(f"   Message: {result1.get('message', 'No message')}")
            print(f"   In cooldown: {result1.get('in_cooldown', 'N/A')}")
            print(f"   Success: {result1.get('success', 'N/A')}")
            print(f"   Time taken: {elapsed1:.2f}s")
        else:
            print(f"   Status: {response1.status_code} ❌")
        
        # Test 2: Immediate second call
        print(f"\n--- API Call #2 (Immediate) ---")
        start_time = time.time()
        response2 = requests.post('http://localhost:5000/api/camera/detect/hybrid', 
                                json={'auto_add_to_cart': False}, 
                                timeout=10)
        elapsed2 = time.time() - start_time
        
        if response2.status_code == 200:
            result2 = response2.json()
            print(f"   Status: {response2.status_code} ✓")
            print(f"   Message: {result2.get('message', 'No message')}")
            print(f"   In cooldown: {result2.get('in_cooldown', 'N/A')}")
            print(f"   Success: {result2.get('success', 'N/A')}")
            print(f"   Time taken: {elapsed2:.2f}s")
        else:
            print(f"   Status: {response2.status_code} ❌")
        
        # Analyze results
        print(f"\n📊 Analysis:")
        if response1.status_code == 200 and response2.status_code == 200:
            result1 = response1.json()
            result2 = response2.json()
            
            # Check if cooldown was triggered appropriately
            first_in_cooldown = result1.get('in_cooldown', False)
            second_in_cooldown = result2.get('in_cooldown', False)
            
            if not first_in_cooldown and second_in_cooldown:
                print(f"   ✅ Cooldown working correctly!")
                print(f"   First call: Not in cooldown")
                print(f"   Second call: Correctly blocked by cooldown")
            elif first_in_cooldown and second_in_cooldown:
                print(f"   ⚠️  Both calls in cooldown - cooldown may be stuck")
            elif not first_in_cooldown and not second_in_cooldown:
                print(f"   ⚠️  Neither call in cooldown - cooldown may not be working")
            else:
                print(f"   ❓ Unexpected cooldown pattern")
        
    except Exception as e:
        print(f"   ❌ API test failed: {e}")

def main():
    """Run all cooldown tests"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "COOLDOWN SYSTEM DIAGNOSTIC TEST" + " " * 25 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        # Test 1: Direct cooldown testing
        test_cooldown_directly()
        
        # Test 2: Hybrid detection simulation
        test_hybrid_detection_with_cooldown()
        
        # Test 3: Manual reset
        test_manual_cooldown_reset()
        
        # Test 4: API testing
        api_cooldown_test()
        
        print("\n" + "=" * 80)
        print("  COOLDOWN TEST SUMMARY")
        print("=" * 80)
        print("\n✅ All cooldown tests completed!")
        print("\nIf you're still having issues with detection:")
        print("1. The cooldown system might be holding a previous detection")
        print("2. Try clearing the cooldown manually (shown above)")
        print("3. Wait for the full cooldown period to expire")
        print("4. Or restart the Flask server to reset all state")
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
