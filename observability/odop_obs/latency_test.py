import requests
import time


def check_latency(url):
    try:
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        latency = end_time - start_time
        if response.status_code == 200:
            return latency
        else:
            print(
                f"Failed to retrieve data from {url}. Status code: {response.status_code}"
            )
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to {url}: {e}")
        return None


if __name__ == "__main__":
    url = "http://localhost:9100/metrics"
    total_latency = 0
    successful_requests = 0
    num_requests = 20

    for _ in range(num_requests):
        latency = check_latency(url)
        if latency is not None:
            total_latency += latency
            successful_requests += 1
        time.sleep(1)

    if successful_requests > 0:
        average_latency = (
            total_latency / successful_requests
        ) * 1000  # Convert to milliseconds
        print(
            f"Average latency over {successful_requests} requests: {average_latency} ms"
        )
    else:
        print("No successful requests made.")
