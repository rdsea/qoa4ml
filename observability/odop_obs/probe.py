import time, json
from threading import Thread
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import requests, pickle, socket

HOST = "127.0.0.1"
PORT = 12345


class Probe:
    __slots__ = [
        "config",
        "node_name",
        "frequency",
        "obs_service_url",
        "cpu_metadata",
        "gpu_metadata",
        "mem_metadata",
        "current_report",
        "started",
        "report_thread",
        "monitoring_service_url",
        "metrics",
        "report_url",
        "monitoring_interval",
    ]

    def __init__(self, config: dict) -> None:
        self.config = config
        self.frequency = self.config["frequency"]
        self.monitoring_interval = 1.0 / self.frequency
        self.current_report = None
        self.started = False
        self.report_thread = None
        self.report_url = config["request_url"]

    def register(self, cpu_metadata: dict, gpu_metadata: dict, mem_metadata: dict):
        cpu_metadata = cpu_metadata
        gpu_metadata = gpu_metadata
        mem_metadata = mem_metadata
        data = {
            "node_name": self.node_name,
            "metadata": {"cpu": cpu_metadata, "gpu": gpu_metadata, "mem": mem_metadata},
        }
        response = requests.post(self.obs_service_url, json=data)
        if response.status_code == 200:
            register_info = json.loads(response.text)
            self.monitoring_service_url = register_info["reportUrl"]
            self.metrics = register_info["metrics"]
            self.frequency = register_info["frequency"]
        else:
            raise Exception(f"Can't register probe {self.node_name}")

    def create_report(self):
        pass

    def reporting(self):
        while self.started:
            self.create_report()
            time.sleep(self.monitoring_interval)

    def start_reporting(self):
        self.started = True
        self.report_thread = Thread(target=self.reporting)
        self.report_thread.daemon = True
        self.report_thread.start()

    def stop_reporting(self):
        self.started = False
        self.report_thread.join()

    def send_report(self, report: dict):
        start = time.time()
        response = requests.post(self.report_url, json=report)
        print(f"Sending data latency {(time.time() - start)*1000}ms")

    def send_report_socket(self, report: dict):
        start = time.time()
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((HOST, PORT))
        serialized_dict = pickle.dumps(report)
        client_socket.sendall(serialized_dict)
        client_socket.close()
        print(f"Sending data latency {(time.time() - start)*1000}ms")
