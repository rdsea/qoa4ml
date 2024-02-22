import requests
import time

# Define the URL of the FastAPI endpoint
url = "http://127.0.0.1:8000/latest_timestamp"

# Define the interval between requests (1 second)
interval = 1

# Continuously request the endpoint
while True:
    # Send a GET request to the endpoint
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Extract the data from the response
        data = response.json()
        latest_timestamp = data["latest_timestamp"]
        print("Latest Timestamp:", latest_timestamp)
    else:
        print("Failed to retrieve latest timestamp. Status code:", response.status_code)

    # Wait for the defined interval before making the next request
    time.sleep(interval)
