import requests
import time

def comprehensive_test():
    url = "http://localhost:5000/api/weight_sensor/read"
    print("🚀 Triggering 5 separate readings to flush any stale data...")
    
    for i in range(5):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                print(f"Reading {i+1}: {data.get('weight_g')}g")
            else:
                print(f"Reading {i+1}: Error {response.status_code}")
        except Exception as e:
            print(f"Reading {i+1}: Exception {e}")
        time.sleep(1)

if __name__ == "__main__":
    comprehensive_test()
