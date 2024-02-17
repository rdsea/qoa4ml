import time, json
from threading import Thread
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
    ]
    def __init__(self, config: dict) -> None:
        self.config = config
        self.frequency = self.config["frequency"]
        self.current_report = None
        self.started = False
        self.report_thread = None

    def register(self, cpu_metadata: dict, gpu_metadata: dict, mem_metadata: dict):
        import requests
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
            time.sleep(1)

    def start_reporting(self):
        self.started = True
        self.report_thread = Thread(target=self.reporting)
        self.report_thread.daemon = True
        self.report_thread.start()

    def stop_reporting(self):
        self.started = False
        self.report_thread.join()
