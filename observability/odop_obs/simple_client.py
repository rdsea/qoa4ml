import requests
import time
import json, math

# Define the URL of the FastAPI endpoint
url = "http://127.0.0.1:8000/metrics"

# Define the interval between requests (1 second)
interval = 1

# Define the filename for the JSON file
json_filename = "latest_timestamp.json"

# Continuously request the endpoint
while True:
    # Send a GET request to the endpoint
    response = requests.get(url, json={"timestamp": time.time()})

    if response.status_code == 200:
        data = response.json()
        print(data)
        print(len(data))
    else:
        print("Failed to retrieve latest timestamp. Status code:", response.status_code)

    time.sleep(1)
