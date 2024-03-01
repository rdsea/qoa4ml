import os, argparse
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
import yaml
import time
from core.probe import Probe

NODE_NAME = os.getenv("NODE_NAME")
if not NODE_NAME:
    NODE_NAME = "node_default"


class SystemMonitoringProbe(Probe):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.node_name = NODE_NAME  # TODO: find somehow to get node name
        if self.config["requireRegister"]:
            self.obs_service_url = self.config["obsServiceUrl"]
        self.cpu_metadata = self.get_cpu_metadata()
        self.gpu_metadata = self.get_gpu_metadata()
        self.mem_metadata = self.get_mem_metadata()

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
        report = {
            "node_name": self.node_name,
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
        self.current_report = report
        if self.log_latency_flag:
            self.write_log(
                (time.time() - timestamp) * 1000,
                self.latency_logging_path + "calculating_system_metric_latency.txt",
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="config path", default="config/process_probe_conf.yaml"
    )
    args = parser.parse_args()
    config_file = args.config
    config = yaml.safe_load(open(config_file))

    sys_monitoring_probe = SystemMonitoringProbe(config)
    del config
    sys_monitoring_probe.start_reporting()
    while True:
        time.sleep(1)
