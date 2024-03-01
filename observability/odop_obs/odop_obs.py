import multiprocessing, subprocess, os

import yaml, argparse, sys

from .core.common import ODOP_PATH

sys.path.append(ODOP_PATH)
from process_monitoring_probe import ProcessMonitoringProbe
from system_monitoring_probe import SystemMonitoringProbe
from exporter import Exporter


class OdopObs:
    def __init__(self, config: dict) -> None:
        self.process_config = config["process"]
        self.system_config = config["system"]
        self.exporter_config = config["exporter"]
        self.process_probe = ProcessMonitoringProbe(self.process_config)
        self.system_probe = SystemMonitoringProbe(self.system_config)
        self.exporter = Exporter(self.exporter_config)

    def start(self):
        self.monitoring_process = multiprocessing.Process(target=self.start_monitoring)
        self.monitoring_process.start()

    def start_monitoring(self):
        self.system_probe.start_reporting()
        self.process_probe.start_reporting()
        self.exporter.start()

    def stop(self):
        self.process_probe.stop_reporting()
        self.system_probe.stop_reporting()
        self.monitoring_process.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="config path", default="config/odop_obs_conf.yaml"
    )
    args = parser.parse_args()
    config_file = args.config
    config = yaml.safe_load(open(ODOP_PATH + config_file))
    odop_obs = OdopObs(config)
    try:
        odop_obs.start()
    except KeyboardInterrupt:
        odop_obs.stop()
