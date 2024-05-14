import importlib
import logging
import os
import time
from typing import TYPE_CHECKING

import lazy_import
import psutil

from qoa4ml.connector.base_connector import BaseConnector
from qoa4ml.datamodels.datamodel_enum import EnvironmentEnum

from ..datamodels.configs import ProcessProbeConfig
from ..qoa_utils import (
    convert_to_mbyte,
    get_process_allowed_cpus,
    get_process_allowed_memory,
    report_proc_child_cpu,
    report_proc_mem,
)
from .probe import Probe

if TYPE_CHECKING:
    from ..datamodels.resources_report import (
        ProcessMetadata,
        ProcessReport,
        ResourceReport,
    )
else:
    ProcessReport = lazy_import.lazy_class(
        "..datamodels.resources_report", "ProcessReport"
    )
    ProcessMetadata = lazy_import.lazy_class(
        "..datamodels.resources_report", "ProcessMetadata"
    )
    ResourceReport = lazy_import.lazy_class(
        "..datamodels.resources_report", "ResourceReport"
    )
logging.basicConfig(
    format="%(asctime)s:%(levelname)s -- %(message)s", level=logging.INFO
)


class ProcessMonitoringProbe(Probe):
    def __init__(self, config: ProcessProbeConfig, connector: BaseConnector) -> None:
        super().__init__(config, connector)
        self.config = config
        if not config.pid:
            self.pid = os.getpid()
        else:
            self.pid = config.pid
            if not psutil.pid_exists(self.pid):
                raise RuntimeError(f"No process with pid {self.pid}")
        self.environment = config.environment
        self.process = psutil.Process(self.pid)
        if self.config.require_register:
            self.obs_service_url = self.config.obs_service_url
        if self.environment == EnvironmentEnum.hpc:
            self.metadata = {"pid": str(self.pid), "user": self.process.username()}
        else:
            self.metadata = ProcessMetadata(
                pid=str(self.pid), user=self.process.username()
            )

    def get_cpu_usage(self):
        process_usage = report_proc_child_cpu(self.process)
        return process_usage

    def get_mem_usage(self):
        data = report_proc_mem(self.process)
        return {
            "rss": {"value": convert_to_mbyte(data["rss"]), "unit": "Mb"},
            "vms": {"value": convert_to_mbyte(data["vms"]), "unit": "Mb"},
        }

    def create_report(self):
        timestamp = time.time()
        cpu_usage = self.get_cpu_usage()
        mem_usage = self.get_mem_usage()
        allowed_cpu_list = get_process_allowed_cpus()
        allowed_memory_size = get_process_allowed_memory()
        report = None
        if self.environment == EnvironmentEnum.hpc:
            report = {
                "type": "process",
                "metadata": {
                    "pid": str(self.pid),
                    "user": self.process.username(),
                    "allowed_cpu_list": str(allowed_cpu_list),
                    "allowed_memory_size": str(allowed_memory_size),
                },
                "timestamp": round(timestamp),
                "cpu": {
                    "usage": cpu_usage,
                },
                "mem": {
                    "usage": mem_usage,
                },
            }
        else:
            report = ProcessReport(
                metadata=self.metadata,
                timestamp=round(timestamp),
                cpu=ResourceReport(usage=cpu_usage),
                mem=ResourceReport(usage=mem_usage),
            )
        if self.log_latency_flag:
            self.write_log(
                (time.time() - timestamp) * 1000,
                self.latency_logging_path + "calculating_process_metric_latency.txt",
            )
        return report


if __name__ == "__main__":
    argparse = importlib.import_module("argparse")
    yaml = importlib.import_module("yaml")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="config path", default="config/process_probe_conf.yaml"
    )
    args = parser.parse_args()
    config_file = args.config
    with open(config_file, encoding="utf-8") as file:
        proces_config = yaml.safe_load(file)
    process_monitoring_probe = ProcessMonitoringProbe(proces_config)
    del proces_config
    process_monitoring_probe.start_reporting()
    while True:
        time.sleep(10)
