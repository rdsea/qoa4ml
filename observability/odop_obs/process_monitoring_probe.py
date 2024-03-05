import logging
import argparse
import time
import os
import psutil
import yaml
from qoa4ml.qoaUtils import convert_to_mbyte, report_proc_child_cpu, report_proc_mem
from .core.probe import Probe
from .core.common import ProcessReport, ProcessMetadata, ResourceReport

logging.basicConfig(
    format="%(asctime)s:%(levelname)s -- %(message)s", level=logging.INFO
)


class ProcessMonitoringProbe(Probe):
    def __init__(self, config: dict) -> None:
        super().__init__(config)
        if "pid" not in config.keys():
            self.pid = os.getpid()
        else:
            self.pid = config["pid"]
            if not psutil.pid_exists(self.pid):
                raise RuntimeError(f"No process with pid {self.pid}")
        self.process = psutil.Process(self.pid)
        if self.config["requireRegister"]:
            self.obs_service_url = self.config["obsServiceUrl"]
        self.metadata = ProcessMetadata(pid=str(self.pid), user=self.process.username())

    def get_cpu_usage(self):
        process_usage = report_proc_child_cpu(self.process)
        del process_usage["unit"]
        return ResourceReport(usage=process_usage)

    def get_mem_usage(self):
        data = report_proc_mem(self.process)
        return ResourceReport(
            usage={
                "rss": {"value": convert_to_mbyte(data["rss"]), "unit": "Mb"},
                "vms": {"value": convert_to_mbyte(data["vms"]), "unit": "Mb"},
            }
        )

    def create_report(self):
        timestamp = time.time()
        cpu_report = self.get_cpu_usage()
        mem_report = self.get_mem_usage()
        report = ProcessReport(
            metadata=self.metadata,
            timestamp=round(timestamp),
            cpu=cpu_report,
            mem=mem_report,
        )
        self.current_report = report
        if self.log_latency_flag:
            self.write_log(
                (time.time() - timestamp) * 1000,
                self.latency_logging_path + "calculating_process_metric_latency.txt",
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="config path", default="config/process_probe_conf.yaml"
    )
    args = parser.parse_args()
    config_file = args.config
    with open(config_file, encoding="utf-8") as file:
        proces_config = yaml.safe_load(file)
    process_monitoring_probe = ProcessMonitoringProbe(proces_config)
    del proces_config
    process_monitoring_probe.start_reporting()
    while True:
        time.sleep(10)
