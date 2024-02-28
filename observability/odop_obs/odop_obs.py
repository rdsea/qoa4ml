import multiprocessing, subprocess
from process_monitoring_probe import ProcessMonitoringProbe
from system_monitoring_probe import SystemMonitoringProbe


class OdopObs:
    def __init__(self, config: dict) -> None:
        self.process_config = config["process"]
        self.system_config = config["system"]
        self.process_probe = ProcessMonitoringProbe(self.process_config)
        self.system_probe = SystemMonitoringProbe(self.system_config)

    def start(self):
        self.exporter_process = multiprocessing.Process(target=self.start_exporter)
        self.exporter_process.start()
        self.system_probe.start_reporting()
        self.process_probe.start_reporting()

    def start_exporter(self):
        subprocess.run(["uvicorn", "exporter:app", "--port", "8000"])

    def stop(self):
        self.process_probe.stop_reporting()
        self.system_probe.stop_reporting()
        self.exporter_process.kill()
