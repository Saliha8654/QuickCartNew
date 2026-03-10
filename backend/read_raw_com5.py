import serial
import time

def read_raw_serial(port='COM5', baudrate=9600, duration=10):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        print(f"Connected to {port}. Reading for {duration} seconds...")
        start_time = time.time()
        while time.time() - start_time < duration:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    print(f"RAW: {line}")
            time.sleep(0.1)
        ser.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    read_raw_serial()
