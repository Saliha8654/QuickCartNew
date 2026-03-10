import requests
import json

def test_sensor_reading():
    url = "http://localhost:5000/api/weight_sensor/read"
    print(f"Reading from {url}...")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sensor Reading: {data.get('weight_g')}g")
            return data.get('weight_g')
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_sensor_reading()
