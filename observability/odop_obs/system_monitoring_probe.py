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
import json
import time
from probe import Probe


class SystemMonitoringProbe(Probe):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.node_name = "aaltosea_test"  # TODO: find somehow to get node name
        if self.config["requireRegister"]:
            self.obs_service_url = self.config["obsServiceUrl"]
        self.cpu_metadata = self.get_cpu_metadata()
        self.gpu_metadata = self.get_gpu_metadata()
        self.mem_metadata = self.get_mem_metadata()

    def get_cpu_metadata(self):
        return get_sys_cpu_metadata()

    def get_cpu_usage(self):
        report = get_sys_cpu_util()
        return report

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
        return {"mem_usage": convert_to_mbyte(mem["used"])}

    def create_report(self):
        timestamp = time.time()
        cpu_usage = self.get_cpu_usage()
        gpu_usage = self.get_gpu_usage()
        mem_usage = self.get_mem_usage()
        report = {
            "node_name": self.node_name,
            "timestamp": int(timestamp),
            "cpu_usage": cpu_usage,
            "gpu_usage": gpu_usage,
            "mem_usage": mem_usage,
        }
        self.current_report = report
        self.send_report_socket(self.current_report)
        print(f"Latency {(time.time() - timestamp) * 1000}ms")


if __name__ == "__main__":
    conf = json.load(open("./system_probe_conf.json"))

    sys_monitoring_probe = SystemMonitoringProbe(conf)
    del conf
    while True:
        sys_monitoring_probe.create_report()
        time.sleep(1)
