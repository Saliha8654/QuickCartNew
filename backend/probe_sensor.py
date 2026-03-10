import serial
import time

def probe_sensor(port='COM5', baudrate=9600):
    print(f"🚀 Probing sensor on {port}...")
    try:
        ser = serial.Serial(port, baudrate, timeout=2)
        print(f"✅ Connected to {port}")
        time.sleep(3) # Wait for reset
        ser.flushInput()
        
        commands = [b"r\n", b"READ\n", b"GET\n", b"t\n"]
        for cmd in commands:
            print(f"📡 Sending command: {cmd.strip()}")
            ser.write(cmd)
            time.sleep(1)
            
            start_time = time.time()
            while time.time() - start_time < 2:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        print(f"   📥 Received: {line}")
                time.sleep(0.1)
        
        ser.close()
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    probe_sensor()
