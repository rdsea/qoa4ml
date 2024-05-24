import logging
import os
import time
from typing import TYPE_CHECKING

import lazy_import
import psutil

from ..config.configs import ProcessProbeConfig
from ..connector.base_connector import BaseConnector
from ..lang.datamodel_enum import EnvironmentEnum
from ..utils.qoa_utils import (
    convert_to_mbyte,
    get_process_allowed_cpus,
    get_process_allowed_memory,
    report_proc_child_cpu,
    report_proc_mem,
)
from .probe import Probe

if TYPE_CHECKING:
    from ..reports.resources_report_model import (
        ProcessMetadata,
        ProcessReport,
        ResourceReport,
    )
else:
    ProcessReport = lazy_import.lazy_class(
        "..datamodels.resources_report_model", "ProcessReport"
    )
    ProcessMetadata = lazy_import.lazy_class(
        "..datamodels.resources_report_model", "ProcessMetadata"
    )
    ResourceReport = lazy_import.lazy_class(
        "..datamodels.resources_report_model", "ResourceReport"
    )
logging.basicConfig(
    format="%(asctime)s:%(levelname)s -- %(message)s", level=logging.INFO
)


class ProcessMonitoringProbe(Probe):
    def __init__(self, config: ProcessProbeConfig, connector: BaseConnector) -> None:
        super().__init__(config, connector)
        self.config = config
        if self.config.pid is None:
            self.pid = os.getpid()
        else:
            self.pid = self.config.pid
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
        # if self.log_latency_flag:
        #     self.write_log(
        #         (time.time() - timestamp) * 1000,
        #         self.latency_logging_path + "calculating_process_metric_latency.txt",
        #     )
        return report
