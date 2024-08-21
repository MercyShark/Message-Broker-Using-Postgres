import requests
import time
url = "http://localhost:8080/message"

while True:
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json() 
            time.sleep(3) # Simulate processing time
            response = requests.delete(f"{url}/{data['receipt_handle']}") 
            print(response.json())
        else:
            print(f"Request failed with status code {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        break
