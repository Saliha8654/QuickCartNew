"""
Test script for HX711 Load Cell with Arduino

This script communicates with the Arduino running the HX711 sketch
to test weight measurements.

Prerequisites:
1. Upload the HX711_Test.ino sketch to your Arduino
2. Connect Arduino to your computer via USB
3. Install required Python packages: pip install pyserial
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
        # this excludes your current terminal "/dev/tty"
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

def test_hx711():
    print("=" * 60)
    print("	HX711 Load Cell Test")
    print("=" * 60)
    
    # List available ports
    print("\nAvailable serial ports:")
    ports = list_serial_ports()
    for i, port in enumerate(ports):
        print(f"  {i+1}. {port}")
    
    if not ports:
        print("❌ No serial ports found!")
        return
    
    # Try to connect to Arduino
    ser = None
    port_to_try = None
    
    # First try common Arduino ports
    common_ports = ['COM3', 'COM4', 'COM5', '/dev/ttyUSB0', '/dev/ttyACM0']
    for port in common_ports:
        if port in ports:
            port_to_try = port
            break
    
    # If no common port found, use the first available
    if not port_to_try and ports:
        port_to_try = ports[0]
    
    print(f"\nTrying to connect to: {port_to_try}")
    
    try:
        # Connect to serial port
        ser = serial.Serial(port_to_try, 9600, timeout=2)
        print(f"✅ Connected to {port_to_try}")
        
        # Wait for Arduino to reset
        time.sleep(3)
        
        # Flush input
        ser.flushInput()
        
        print("\nTesting weight sensor...")
        print("Commands:")
        print("  't' - Tare the scale (set current weight as zero)")
        print("  'cXXX' - Calibrate with known weight (e.g., 'c500' for 500g)")
        print("  'r' - Continuous read mode")
        print("  'q' - Quit")
        print("\nListening for weight data (Ctrl+C to stop)...")
        
        # Listen for data
        start_time = time.time()
        while True:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    print(f"Arduino: {line}")
            
            # Check for user input (non-blocking)
            if time.time() - start_time > 30:  # Stop after 30 seconds if no data
                print("\nTimeout reached. Exiting...")
                break
                
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping test...")
    except serial.SerialException as e:
        print(f"❌ Serial error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("✅ Serial connection closed")

def interactive_mode():
    """Interactive mode for testing commands"""
    print("\n" + "=" * 60)
    print("	HX711 Interactive Test Mode")
    print("=" * 60)
    
    # List available ports
    print("\nAvailable serial ports:")
    ports = list_serial_ports()
    for i, port in enumerate(ports):
        print(f"  {i+1}. {port}")
    
    if not ports:
        print("❌ No serial ports found!")
        return
    
    # Get user selection
    try:
        choice = int(input(f"\nSelect port (1-{len(ports)}): ")) - 1
        if choice < 0 or choice >= len(ports):
            print("❌ Invalid selection!")
            return
        selected_port = ports[choice]
    except ValueError:
        print("❌ Invalid input!")
        return
    
    try:
        # Connect to serial port
        ser = serial.Serial(selected_port, 9600, timeout=1)
        print(f"✅ Connected to {selected_port}")
        
        # Wait for Arduino to reset
        time.sleep(3)
        
        # Flush input
        ser.flushInput()
        
        print("\nInteractive Mode - Send commands to Arduino")
        print("Commands:")
        print("  t - Tare scale")
        print("  c500 - Calibrate with 500g (replace with your known weight)")
        print("  r - Continuous read mode")
        print("  q - Quit")
        
        while True:
            command = input("\nEnter command: ").strip().lower()
            
            if command == 'q':
                break
            elif command == 'r':
                print("Entering continuous read mode. Press Ctrl+C to stop.")
                try:
                    while True:
                        if ser.in_waiting > 0:
                            line = ser.readline().decode('utf-8').strip()
                            if line and "Weight:" in line:
                                print(line)
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    print("\nExiting continuous mode...")
            else:
                # Send command to Arduino
                ser.write((command + '\n').encode())
                time.sleep(1)
                
                # Read response
                response_lines = []
                start_time = time.time()
                while time.time() - start_time < 2:  # Wait up to 2 seconds
                    if ser.in_waiting > 0:
                        line = ser.readline().decode('utf-8').strip()
                        if line:
                            response_lines.append(line)
                    time.sleep(0.1)
                
                if response_lines:
                    print("Arduino response:")
                    for line in response_lines:
                        print(f"  {line}")
                else:
                    print("No response from Arduino")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("✅ Serial connection closed")

if __name__ == "__main__":
    print("	HX711 Load Cell Test Script")
    print("=" * 60)
    
    mode = input("\nSelect mode:\n1. Automatic test\n2. Interactive mode\nEnter choice (1 or 2): ").strip()
    
    if mode == "2":
        interactive_mode()
    else:
        test_hx711()