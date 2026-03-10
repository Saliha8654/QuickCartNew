
import serial
import time
import sys
import glob

def list_serial_ports():
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    else:
        ports = glob.glob('/dev/tty[A-Za-z]*')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def diagnose():
    print("🔍 Scanning all available serial ports...")
    ports = list_serial_ports()
    if not ports:
        print("❌ No serial ports found. Is the Arduino connected?")
        return

    print(f"✅ Found ports: {ports}")
    
    for port in ports:
        print(f"\n📡 Testing {port}...")
        try:
            ser = serial.Serial(port, 9600, timeout=2)
            time.sleep(2) # Wait for reset
            ser.write(b'r\n') # Try to trigger reading
            
            start_time = time.time()
            found_data = False
            while time.time() - start_time < 5:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(f"   📥 Received: {line}")
                        found_data = True
                time.sleep(0.1)
            
            if not found_data:
                print(f"   ⚠️ No data received from {port} in 5 seconds.")
            
            ser.close()
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    diagnose()
