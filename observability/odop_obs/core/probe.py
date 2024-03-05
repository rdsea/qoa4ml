import math
import pickle
import socket
import sys
from typing import Union
from threading import Thread
import logging
import time
from .common import ODOP_PATH, ProcessReport, SystemReport

logging.basicConfig(
    format="%(asctime)s:%(levelname)s -- %(message)s", level=logging.INFO
)


class Probe:
    __slots__ = [
        "config",
        "node_name",
        "frequency",
        "obs_service_url",
        "cpu_metadata",
        "gpu_metadata",
        "mem_metadata",
        "current_report",
        "execution_flag",
        "report_thread",
        "monitoring_service_url",
        "metrics",
        "monitoring_interval",
        "latency_logging_path",
        "max_latency",
        "log_latency_flag",
    ]

    def __init__(self, config: dict) -> None:
        self.config = config
        self.frequency = self.config["frequency"]
        self.monitoring_interval = 1.0 / self.frequency
        self.execution_flag = False
        self.report_thread = None
        self.log_latency_flag = self.config["log_latency_flag"]
        if self.log_latency_flag:
            self.latency_logging_path = ODOP_PATH + config["latency_logging_path"]
        self.current_report: Union[SystemReport, ProcessReport]
        self.max_latency = 0.0

    def create_report(self):
        pass

    def reporting(self):
        current_time = time.time()
        time.sleep(math.ceil(current_time) - current_time)
        while self.execution_flag:
            start = time.time()
            self.create_report()
            self.send_report_socket(self.current_report)
            self.max_latency = max(time.time() - start, self.max_latency)
            time.sleep(
                round(time.time())
                + self.monitoring_interval
                - self.max_latency
                - time.time()
            )

    def start_reporting(self):
        self.execution_flag = True
        self.report_thread = Thread(target=self.reporting)
        self.report_thread.daemon = True
        self.report_thread.start()

    def stop_reporting(self):
        self.execution_flag = False

    def send_report_socket(self, report):
        start = time.time()
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(
                (self.config["aggregator_host"], self.config["aggregator_port"])
            )
            serialized_dict = pickle.dumps(report)
            client_socket.sendall(serialized_dict)
            client_socket.close()
        except ConnectionRefusedError:
            logging.error("Connection to aggregator refused")
        if self.log_latency_flag:
            self.write_log(
                (time.time() - start) * 1000,
                self.latency_logging_path + "report_latency.txt",
            )

    def write_log(self, latency, filepath: str):
        with open(filepath, "a", encoding="utf-8") as file:
            file.write(str(latency) + "\n")
