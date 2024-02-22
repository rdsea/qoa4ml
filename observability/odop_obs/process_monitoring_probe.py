import psutil
import yaml
from qoa4ml.qoaUtils import convert_to_mbyte, report_proc_child_cpu, report_proc_mem
import json
import time, os
from probe import Probe


class ProcessMonitoringProbe(Probe):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        if "pid" not in config.keys():
            self.pid = os.getpid()
        else:
            self.pid = config["pid"]
            if not psutil.pid_exists(self.pid):
                raise Exception(f"No process with pid {self.pid}")
        self.process = psutil.Process(self.pid)
        if self.config["requireRegister"]:
            self.obs_service_url = self.config["obsServiceUrl"]

    def get_cpu_usage(self):
        process_usage = report_proc_child_cpu(self.process)
        del process_usage["unit"]
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
        report = {
            "metadata": {"pid": str(self.pid), "user": self.process.username()},
            "timestamp": int(timestamp),
            "usage": {"cpu": cpu_usage, "mem": mem_usage},
        }

        self.current_report = self.flatten(report)
        self.write_log(
            (time.time() - timestamp) * 1000,
            self.logging_path + "calculating_process_metric_latency.txt",
        )
        self.send_report_socket(self.current_report)

    def flatten(self, report: dict):
        cpu_usage = report["usage"]["cpu"]
        mem_usage = report["usage"]["mem"]
        return {
            "metadata": {**report["metadata"]},
            "timestamp": report["timestamp"],
            "cpu_usage": {
                "child_process": cpu_usage["child_process"],
                **cpu_usage["value"],
                "total": cpu_usage["total"],
            },
            "mem_usage": {
                "rss": mem_usage["rss"]["value"],
                "vms": mem_usage["vms"]["value"],
            },
        }


if __name__ == "__main__":
    conf = yaml.safe_load(open("./process_probe_conf.yaml"))

    process_monitoring_probe = ProcessMonitoringProbe(conf)
    del conf
    process_monitoring_probe.start_reporting()
    while True:
        time.sleep(10)
