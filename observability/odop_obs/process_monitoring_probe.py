import psutil
from qoa4ml.qoaUtils import (
    report_proc_cpu,
    get_sys_mem,
    convert_to_gbyte,
    convert_to_mbyte,
    get_sys_cpu_metadata,
    report_proc_child_cpu, 
    report_proc_mem
)
from qoa4ml.gpuUtils import (
    get_sys_gpu_metadata,
    get_sys_gpu_usage,
)
import json
import time
from probe import Probe

class ProcessMonitoringProbe(Probe):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.pid = config["pid"]
        if not psutil.pid_exists(self.pid): 
            raise Exception(f"No process with pid {self.pid}")
        self.process = psutil.Process(self.pid)
        if self.config["requireRegister"]:
            self.obs_service_url = self.config["obsServiceUrl"]

    def get_cpu_usage(self):
        report = report_proc_child_cpu(self.process)
        return {"usage": report}

    def get_gpu_usage(self):
        report = None
        return report

    def get_mem_usage(self):
        data = report_proc_mem(self.process)
        return {
            "rss": {
                "value": convert_to_mbyte(data["rss"]),
                "unit": "Mb"
            }, 
            "vms": {
                "value": convert_to_mbyte(data["vms"]), 
                "unit": "Mb"
            }
        }
    def create_report(self):
        timestamp = time.time()
        cpu_usage = self.get_cpu_usage()
        gpu_usage = self.get_gpu_usage()
        mem_usage = self.get_mem_usage()
        report = {
            "node_name": self.node_name,
            "timestamp": int(timestamp),
            "cpu": { "usage": cpu_usage},
            "gpu": { "usage": gpu_usage},
            "mem": { "usage": mem_usage},
        }
        self.current_report = report
        print(f"Latency {(time.time() - timestamp) * 1000}ms")


if __name__ == "__main__":
    conf = json.load(open("./proces_probe_conf.json"))

    process_monitoring_probe = ProcessMonitoringProbe(conf)
    del conf
    while True:
        print(process_monitoring_probe.get_mem_usage())
        time.sleep(1)
