import psutil
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
        process_usage = report_proc_child_cpu(self.process, True)
        del process_usage["unit"]
        return process_usage

    def get_mem_usage(self):
        data = report_proc_mem(self.process)
        return {
            "rss": convert_to_mbyte(data["rss"]),
            "vms": convert_to_mbyte(data["vms"]),
        }

    def create_report(self):
        timestamp = time.time()
        cpu_usage = self.get_cpu_usage()
        mem_usage = self.get_mem_usage()
        report = {
            "metadata": {"pid": str(self.pid), "user": self.process.username()},
            "timestamp": int(timestamp),
            "cpu_usage": cpu_usage,
            "mem_usage": mem_usage,
        }

        self.current_report = report
        #self.send_report(self.current_report)
        print(f"Latency {(time.time() - timestamp) * 1000}ms")


if __name__ == "__main__":
    conf = json.load(open("./proces_probe_conf.json"))

    process_monitoring_probe = ProcessMonitoringProbe(conf)
    del conf
    process_monitoring_probe.start_reporting()
    while True:
        time.sleep(10)
