"""Quick Serial Port Test"""
import serial
import time

print("Testing COM4 directly...")
print("Make sure Arduino Serial Monitor is CLOSED!")
print("-" * 50)

try:
    ser = serial.Serial('COM4', 9600, timeout=5)
    print("✅ Connected to COM4")
    print("⏳ Waiting 5 seconds for Arduino to reset...")
    time.sleep(5)
    
    print("📡 Reading any data for 10 seconds...")
    print("(If you see nothing, Arduino sketch might not be uploaded)")
    print("-" * 50)
    
    start = time.time()
    data_count = 0
    
    while time.time() - start < 10:
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                print(f"📥 {line}")
                data_count += 1
        time.sleep(0.1)
    
    print("-" * 50)
    if data_count > 0:
        print(f"🎉 SUCCESS! Received {data_count} lines of data!")
        print("Your Arduino is working correctly!")
    else:
        print("⚠️ No data received")
        print("Possible issues:")
        print("  1. Arduino sketch not uploaded")
        print("  2. Wrong baud rate (should be 9600)")
        print("  3. Arduino is stuck/frozen - try unplugging and replugging USB")
    
    ser.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("  1. Close Arduino IDE and Serial Monitor")
    print("  2. Unplug and replug Arduino USB cable")
    print("  3. Try again")
