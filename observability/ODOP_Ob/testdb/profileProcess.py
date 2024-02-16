import psutil
import time


def print_process_info(pid):
    try:
        process = psutil.Process(pid)

        # Basic information
        print(f"PID: {process.pid}")
        print(f"Name: {process.name()}")
        print(f"Username: {process.username()}")
        print(f"Executable: {process.exe()}")
        print(f"Command line: {process.cmdline()}")

        # Resource usage
        print(f"CPU Usage: {process.cpu_percent()}%")
        print(f"Memory Usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
        print(
            f"Disk IO: Reads: {process.io_counters().read_bytes / 1024 / 1024:.2f} MB, Writes: {process.io_counters().write_bytes / 1024 / 1024:.2f} MB"
        )

        # Other information
        print(f"Status: {process.status()}")
        print(f"Threads: {process.num_threads()}")
        print(f"Open files: {len(process.open_files())}")
        print(f"Connections: {len(process.connections())}")

    except psutil.NoSuchProcess:
        print(f"Process with PID {pid} not found.")


if __name__ == "__main__":
    pid = int(input("Enter PID: "))
    print("Collecting process information...")

    while True:
        print_process_info(pid)
        print("-" * 50)
        time.sleep(1)
