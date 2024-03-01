import requests
import time
import json

url = "http://127.0.0.1:8000/metrics"
interval = 1
json_filename = "latest_timestamp.json"
cpu_free_threshold = 10.0  # Threshold for considering CPU as free


def get_free_cpu_cores(cpu_data):
    free_cores = []
    for core, usage in cpu_data["value"].items():
        if usage < cpu_free_threshold:
            free_cores.append(core)
    return free_cores


while True:
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        print(data)
        for item in data:
            if item["type"] == "node":
                cpu_data = item["cpu"]["usage"]
                free_cores = get_free_cpu_cores(cpu_data)
                if free_cores:
                    print("Free CPU cores:", free_cores)
                else:
                    print("No CPU cores are free.")
    else:
        print(
            "Failed to retrieve data from the endpoint. Status code:",
            response.status_code,
        )

    time.sleep(interval)
