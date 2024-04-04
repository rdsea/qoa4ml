import importlib
import multiprocessing
import sys
from typing import Optional

from .core.common import ODOP_PATH
from .process_monitoring_probe import ProcessMonitoringProbe
from .system_monitoring_probe import SystemMonitoringProbe
from .exporter import Exporter

sys.path.append(ODOP_PATH)


class OdopObs:
    def __init__(
        self, config: Optional[dict] = None, config_path: Optional[str] = None
    ) -> None:
        if not config and not config_path:
            raise ValueError("config or config_path must not be empty")
        if config_path:
            yaml = importlib.import_module("yaml")
            with open(config_path, encoding="utf-8") as file:
                self.config = yaml.safe_load(file)
        elif config:
            self.config = config
        self.process_probe = ProcessMonitoringProbe(self.config["process"])
        self.system_probe = SystemMonitoringProbe(self.config["system"])
        self.exporter = Exporter(self.config["exporter"])
        self.monitoring_process = multiprocessing.Process(target=self.start_monitoring)

    def start(self):
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
    yaml = importlib.import_module("yaml")
    argparse = importlib.import_module("argparse")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="config path", default="config/odop_obs_conf.yaml"
    )
    args = parser.parse_args()
    config_file_path = args.config
    odop_obs = OdopObs(config_path=config_file_path)
    try:
        odop_obs.start()
    except KeyboardInterrupt:
        odop_obs.stop()
