from observability.odop_obs.process_monitoring_probe import ProcessMonitoringProbe
from observability.odop_obs.system_monitoring_probe import SystemMonitoringProbe


class OdopObs:
    def __init__(self, config: dict) -> None:
        self.process_config = config["process"]
        self.system_config = config["system"]
        self.process_probe = ProcessMonitoringProbe(self.process_config)
        self.system_probe = SystemMonitoringProbe(self.system_config)

    def start(self):
        pass

    def start_process_monitoring(self):
        pass

    def start_system_monitoring(self):
        pass

    def stop(self):
        self.process_probe.stop_reporting()
        self.system_probe.stop_reporting()
