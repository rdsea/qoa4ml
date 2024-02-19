import psutil
from qoa4ml.qoaUtils import convert_to_mbyte, report_proc_child_cpu, report_proc_mem
import json
import time
from probe import Probe


class ProcessMonitoringProbe(Probe):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        self.pids = config["pid"]
        for pid in self.pids:
            if not psutil.pid_exists(pid):
                raise Exception(f"No process with pid {pid}")
        self.processes = [psutil.Process(pid) for pid in self.pids]
        if self.config["requireRegister"]:
            self.obs_service_url = self.config["obsServiceUrl"]

    def get_cpu_usage(self):
        report = []
        for process in self.processes:
            process_usage = report_proc_child_cpu(process)
            report.append(process_usage)
        return report

    def get_mem_usage(self):
        report = []
        for process in self.processes:
            data = report_proc_mem(process)
            report.append(
                {
                    "rss": {"value": convert_to_mbyte(data["rss"]), "unit": "Mb"},
                    "vms": {"value": convert_to_mbyte(data["vms"]), "unit": "Mb"},
                }
            )
        return report

    def create_report(self):
        timestamp = time.time()
        cpu_usage = self.get_cpu_usage()
        mem_usage = self.get_mem_usage()
        report = []
        for process, cpu_usage, mem_usage in zip(self.processes, cpu_usage, mem_usage):
            report.append(
                {
                    "metadata": {"pid": process.pid, "user": process.username()},
                    "usage": {"cpu": cpu_usage, "mem": mem_usage},
                }
            )
        self.current_report = report
        print(f"Latency {(time.time() - timestamp) * 1000}ms")


if __name__ == "__main__":
    conf = json.load(open("./proces_probe_conf.json"))

    process_monitoring_probe = ProcessMonitoringProbe(conf)
    del conf
    process_monitoring_probe.start_reporting()
    while True:
        time.sleep(10)
