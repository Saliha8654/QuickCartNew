"""
QuickCart Weight Sensor Integration Test

This script tests the communication between the QuickCart backend
and the Arduino HX711 weight sensor.

Steps:
1. Upload QuickCart_Weight_Sensor.ino to your Arduino
2. Connect Arduino to your computer via USB
3. Run this script to test the integration
"""

import serial
import time
import json
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

def test_weight_sensor():
    print("=" * 60)
    print("	QuickCart Weight Sensor Integration Test")
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
        
        # Wait for Arduino to reset and initialize
        print("⏳ Waiting for Arduino to initialize...")
        time.sleep(4)
        
        # Flush input
        ser.flushInput()
        
        print("\nTesting weight sensor communication...")
        print("Sending READ command...")
        
        # Send READ command
        ser.write(b'READ\n')
        time.sleep(1)
        
        # Read response
        response_lines = []
        start_time = time.time()
        while time.time() - start_time < 3:  # Wait up to 3 seconds
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    response_lines.append(line)
                    # Try to parse as JSON
                    try:
                        data = json.loads(line)
                        if 'weight_g' in data:
                            print(f"✅ Weight reading received: {data['weight_g']}g")
                            break
                    except json.JSONDecodeError:
                        print(f"Arduino message: {line}")
            time.sleep(0.1)
        
        if not response_lines:
            print("❌ No response from Arduino")
            print("Please check:")
            print("  1. Arduino is properly connected")
            print("  2. Correct sketch is uploaded")
            print("  3. Correct serial port is selected")
            return
        
        print("\n" + "-" * 40)
        print("Testing TARE command...")
        
        # Send TARE command
        ser.write(b'TARE\n')
        time.sleep(1)
        
        # Read response
        tare_response = ""
        start_time = time.time()
        while time.time() - start_time < 2:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                if line:
                    tare_response = line
                    print(f"Arduino response: {line}")
                    break
            time.sleep(0.1)
        
        print("\n" + "-" * 40)
        print("Testing continuous weight readings...")
        print("Collecting 5 readings (one every 2 seconds)...")
        
        readings = []
        for i in range(5):
            # Wait for automatic weight update (every 2 seconds)
            line_received = False
            start_time = time.time()
            while time.time() - start_time < 3:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        try:
                            data = json.loads(line)
                            if 'weight_g' in data:
                                weight = data['weight_g']
                                readings.append(weight)
                                print(f"  Reading {i+1}: {weight}g")
                                line_received = True
                                break
                        except json.JSONDecodeError:
                            pass  # Not a JSON line, ignore
                time.sleep(0.1)
            
            if not line_received:
                print(f"  Reading {i+1}: No data received")
            
            if i < 4:  # Don't wait after the last reading
                time.sleep(2)
        
        if readings:
            avg_weight = sum(readings) / len(readings)
            print(f"\n📊 Average weight: {avg_weight:.2f}g")
            print("✅ Weight sensor integration test PASSED!")
        else:
            print("\n⚠️  No valid weight readings received")
            print("The sensor may be working but not sending data in expected format")
        
    except serial.SerialException as e:
        print(f"❌ Serial error: {e}")
        print("Please check USB connection and port permissions")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if ser and ser.is_open:
            ser.close()
            print("\n✅ Serial connection closed")

def interactive_test():
    """Interactive mode for advanced testing"""
    print("\n" + "=" * 60)
    print("	QuickCart Weight Sensor Interactive Test")
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
        print("  r - Read current weight")
        print("  t - Tare scale")
        print("  c500 - Calibrate with 500g (replace with known weight)")
        print("  m - Monitor continuous readings")
        print("  q - Quit")
        
        while True:
            command = input("\nEnter command: ").strip().lower()
            
            if command == 'q':
                break
            elif command == 'r':
                ser.write(b'READ\n')
            elif command == 't':
                ser.write(b'TARE\n')
            elif command.startswith('c'):
                weight = command[1:]
                cmd = f"CAL,{weight}\n"
                ser.write(cmd.encode())
            elif command == 'm':
                print("Monitoring mode - Press Ctrl+C to stop")
                try:
                    while True:
                        if ser.in_waiting > 0:
                            line = ser.readline().decode('utf-8').strip()
                            if line:
                                print(f"  {line}")
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    print("\nExiting monitoring mode...")
            else:
                print("Unknown command")
                continue
            
            # Read response (for non-monitoring commands)
            if command != 'm':
                response_lines = []
                start_time = time.time()
                while time.time() - start_time < 2:
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
    print("	QuickCart Weight Sensor Test")
    print("=" * 60)
    
    mode = input("\nSelect mode:\n1. Automated test\n2. Interactive test\nEnter choice (1 or 2): ").strip()
    
    if mode == "2":
        interactive_test()
    else:
        test_weight_sensor()