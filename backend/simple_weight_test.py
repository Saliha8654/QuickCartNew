"""
Simple Weight Sensor Test

This script tests if your HX711 load cell is properly connected
and communicating with the Arduino.
"""

import serial
import time
import sys
import glob

def list_serial_ports():
    """Lists serial port names"""
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.usb*') + glob.glob('/dev/cu*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def test_connection():
    print("=" * 50)
    print("	HX711 Weight Sensor Connection Test")
    print("=" * 50)
    
    # List available ports
    ports = list_serial_ports()
    print(f"\nFound {len(ports)} serial port(s):")
    for i, port in enumerate(ports):
        print(f"  {i+1}. {port}")
    
    if not ports:
        print("❌ No serial ports found!")
        return
    
    # Try common Arduino ports first
    common_ports = ['COM3', 'COM4', 'COM5']
    ports_to_try = [p for p in common_ports if p in ports] + [p for p in ports if p not in common_ports]
    
    print(f"\nTesting ports in order: {ports_to_try}")
    
    for port in ports_to_try:
        print(f"\n🔌 Trying {port}...")
        try:
            # Connect to serial port
            ser = serial.Serial(port, 9600, timeout=2)
            print(f"✅ Connected to {port}")
            
            # Wait for Arduino to reset
            print("⏳ Waiting for Arduino initialization...")
            time.sleep(3)
            
            # Flush input
            ser.flushInput()
            
            print("📡 Listening for data from Arduino...")
            
            # Listen for data for 5 seconds
            start_time = time.time()
            data_received = False
            
            while time.time() - start_time < 5:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        print(f"  🔍 Data received: {line}")
                        data_received = True
                time.sleep(0.1)
            
            ser.close()
            
            if data_received:
                print(f"🎉 SUCCESS! {port} is receiving data from Arduino")
                print(f"✅ Your HX711 load cell setup is working!")
                return
            else:
                print(f"⚠️  No data received from {port}")
                
        except Exception as e:
            print(f"❌ Error with {port}: {e}")
    
    print("\n🔍 Troubleshooting tips:")
    print("  1. Check USB cable connection")
    print("  2. Verify Arduino sketch is uploaded")
    print("  3. Check HX711 wiring (VCC, GND, DT, SCK)")
    print("  4. Try different COM port")
    print("  5. Restart Arduino IDE and check Serial Monitor")

if __name__ == "__main__":
    test_connection()