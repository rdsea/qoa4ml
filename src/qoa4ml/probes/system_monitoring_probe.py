import json
import socket
import time
from typing import TYPE_CHECKING

import lazy_import

from ..config.configs import ClientInfo, SystemProbeConfig
from ..connector.base_connector import BaseConnector
from ..lang.datamodel_enum import EnvironmentEnum
from ..utils.gpu_utils import get_sys_gpu_metadata, get_sys_gpu_usage
from ..utils.qoa_utils import (
    convert_to_gbyte,
    convert_to_mbyte,
    get_sys_cpu_metadata,
    get_sys_cpu_util,
    get_sys_mem,
)
from .probe import Probe

if TYPE_CHECKING:
    from ..reports import resources_report_model
else:
    resources_report_model = lazy_import.lazy_module(
        "qoa4ml.reports.resources_report_model"
    )


class SystemMonitoringProbe(Probe):
    def __init__(
        self,
        config: SystemProbeConfig,
        connector: BaseConnector,
        client_info: ClientInfo,
    ) -> None:
        super().__init__(config, connector, client_info)
        self.config = config
        if self.config.node_name is None:
            self.node_name = socket.gethostname().split(".")[0]
        else:
            self.node_name = self.config.node_name
        if self.config.require_register:
            self.obs_service_url = self.config.obs_service_url
        self.environment = config.environment
        self.cpu_metadata = self.get_cpu_metadata()
        self.gpu_metadata = self.get_gpu_metadata()
        self.mem_metadata = self.get_mem_metadata()
        self.metadata = {"node_name": self.node_name}

    def get_cpu_metadata(self):
        return get_sys_cpu_metadata()

    def get_cpu_usage(self):
        value = get_sys_cpu_util()
        return {"value": value, "unit": "percentage"}

    def get_gpu_metadata(self):
        report = get_sys_gpu_metadata()
        return report

    def get_gpu_usage(self):
        report = get_sys_gpu_usage()
        return report

    def get_mem_metadata(self):
        mem = get_sys_mem()
        return {"mem": {"capacity": convert_to_gbyte(mem["total"]), "unit": "Gb"}}

    def get_mem_usage(self):
        mem = get_sys_mem()
        return {"value": convert_to_mbyte(mem["used"]), "unit": "Mb"}

    def create_report(self):
        timestamp = time.time()
        cpu_usage = self.get_cpu_usage()
        gpu_usage = self.get_gpu_usage()
        mem_usage = self.get_mem_usage()
        if self.environment == EnvironmentEnum.hpc:
            report = {
                "type": "system",
                "metadata": {**self.metadata},
                "timestamp": round(timestamp),
                "cpu": {
                    "metadata": self.cpu_metadata,
                    "usage": cpu_usage,
                },
                "gpu": {
                    "metadata": self.gpu_metadata,
                    "usage": gpu_usage,
                },
                "mem": {
                    "metadata": self.mem_metadata,
                    "usage": mem_usage,
                },
            }
        else:
            report = resources_report_model.SystemReport(
                metadata=resources_report_model.SystemMetadata(
                    node_name=self.node_name, client_info=self.client_info
                ),
                timestamp=round(timestamp),
                cpu=resources_report_model.ResourceReport(
                    metadata=self.cpu_metadata, usage=cpu_usage
                ),
                gpu=resources_report_model.ResourceReport(
                    metadata=self.gpu_metadata, usage=gpu_usage
                ),
                mem=resources_report_model.ResourceReport(
                    metadata=self.mem_metadata, usage=mem_usage
                ),
            ).model_dump()
        return json.dumps(report)
