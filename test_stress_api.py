import requests
import threading

API_URL = "http://localhost:5000/analyze"

def send_request(i):
    try:
        with open("api_tests/test_data/normal_chest_xray.jpg", "rb") as f:
            response = requests.post(API_URL, files={"image": f})
            print(f"[{i}] Status: {response.status_code}")
    except Exception as e:
        print(f"[{i}] Error: {e}")

def test_concurrent_requests():
    threads = []
    for i in range(50):  # 50 concurrent requests
        thread = threading.Thread(target=send_request, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    test_concurrent_requests()
