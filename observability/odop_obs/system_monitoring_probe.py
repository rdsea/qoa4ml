import os
import time
import importlib
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
        self.environment = config["environment"]
        self.cpu_metadata = self.get_cpu_metadata()
        self.gpu_metadata = self.get_gpu_metadata()
        self.mem_metadata = self.get_mem_metadata()
        if self.environment == "HPC":
            self.metadata = {"node_name": self.node_name}
        else:
            self.custom_model = importlib.import_module("core.custom_model")
            self.metadata = self.custom_model.SystemMetadata(node_name=self.node_name)

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
        if self.environment == "HPC":
            self.current_report = {
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
            self.current_report = self.custom_model.SystemReport(
                metadata=self.custom_model.SystemMetadata(node_name=self.node_name),
                timestamp=round(timestamp),
                cpu=self.custom_model.ResourceReport(
                    metadata=self.cpu_metadata, usage=cpu_usage
                ),
                gpu=self.custom_model.ResourceReport(
                    metadata=self.gpu_metadata, usage=gpu_usage
                ),
                mem=self.custom_model.ResourceReport(
                    metadata=self.mem_metadata, usage=mem_usage
                ),
            )
        if self.log_latency_flag:
            self.write_log(
                (time.time() - timestamp) * 1000,
                self.latency_logging_path + "calculating_system_metric_latency.txt",
            )


if __name__ == "__main__":
    argparse = importlib.import_module("argparse")
    yaml = importlib.import_module("yaml")
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="config path", default="config/system_probe_conf.yaml"
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
