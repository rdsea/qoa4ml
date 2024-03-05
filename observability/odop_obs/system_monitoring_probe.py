import os
import time
import argparse
import yaml
from qoa4ml.qoaUtils import (
    get_sys_cpu_util,
    get_sys_mem,
    convert_to_gbyte,
    convert_to_mbyte,
    get_sys_cpu_metadata,
)
from qoa4ml.gpuUtils import (
    get_sys_gpu_metadata,
    get_sys_gpu_usage,
)
from odop.odop_obs.core.common import ResourceReport, SystemMetadata, SystemReport
from .core.probe import Probe

NODE_NAME = os.getenv("NODE_NAME")
if not NODE_NAME:
    NODE_NAME = "node_default"


class SystemMonitoringProbe(Probe):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.node_name = NODE_NAME  # TODO: find somehow to get node name
        if self.config["requireRegister"]:
            self.obs_service_url = self.config["obsServiceUrl"]
        self.cpu_report = ResourceReport(metadata=self.get_cpu_metadata(), usage={})
        self.gpu_report = ResourceReport(metadata=self.get_gpu_metadata(), usage={})
        self.mem_report = ResourceReport(metadata=self.get_mem_metadata(), usage={})
        self.metadata = SystemMetadata(node_name=self.node_name)

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
        self.cpu_report.usage = self.get_cpu_usage()
        self.gpu_report.usage = self.get_gpu_usage()
        self.mem_report.usage = self.get_mem_usage()
        self.current_report = SystemReport(
            metadata=self.metadata,
            timestamp=round(timestamp),
            cpu=self.cpu_report,
            gpu=self.gpu_report,
            mem=self.mem_report,
        )
        if self.log_latency_flag:
            self.write_log(
                (time.time() - timestamp) * 1000,
                self.latency_logging_path + "calculating_system_metric_latency.txt",
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="config path", default="config/system_probe_config.yaml"
    )
    args = parser.parse_args()
    config_file = args.config
    with open(config_file, encoding="utf-8") as file:
        system_probe_config = yaml.safe_load(file)

    sys_monitoring_probe = SystemMonitoringProbe(system_probe_config)
    del system_probe_config
    sys_monitoring_probe.start_reporting()
    while True:
        time.sleep(1)
