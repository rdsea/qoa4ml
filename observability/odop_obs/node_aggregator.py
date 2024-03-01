import math
import socket
import pickle
import argparse
from threading import Thread
import time, logging, traceback
import sys, os
import odop_utils
import yaml
from pydantic import ValidationError
from tinyflux.storages import MemoryStorage
from tinyflux import TinyFlux, Point, TimeQuery
from datetime import datetime
from fastapi import APIRouter, FastAPI
from flatten_dict import flatten, unflatten
from core.common import SystemReport, ProcessReport

logging.basicConfig(
    format="%(asctime)s:%(levelname)s -- %(message)s", level=logging.INFO
)

from core.common import ODOP_PATH

sys.path.append(ODOP_PATH)
DEFAULT_DATABASE_FOLDER = ODOP_PATH + "tinyflux/"
odop_utils.make_folder(DEFAULT_DATABASE_FOLDER)
METRICS_URL_PATH = "/metrics"


class NodeAggregator:
    def __init__(self, config):
        self.config = config
        self.unit_conversion = self.config["unit_conversion"]
        # self.db = TinyFlux(storage=MemoryStorage)
        print(DEFAULT_DATABASE_FOLDER)
        self.db = TinyFlux(DEFAULT_DATABASE_FOLDER + str(self.config["database_path"]))
        self.server_thread = Thread(
            target=self.start_handling, args=(self.config["host"], self.config["port"])
        )
        self.server_thread.daemon = True
        self.execution_flag = False
        self.router = APIRouter()
        self.router.add_api_route(
            METRICS_URL_PATH,
            self.get_lastest_timestamp,
            methods=[self.config["query_method"]],
        )

    def insert_metric(self, timestamp: float, tags: dict, fields: dict):
        timestamp_datetime = datetime.fromtimestamp(timestamp)
        datapoint = Point(time=timestamp_datetime, tags=tags, fields=fields)
        self.db.insert(datapoint, compact_key_prefixes=True)

    def start_handling(self, host, port):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(self.config["backlog_number"])
        while self.execution_flag:
            client_socket, addr = server_socket.accept()
            self.handle_client(client_socket)

    def handle_client(self, client_socket):
        data = b""
        while True:
            packet = client_socket.recv(self.config["socket_package_size"])
            if not packet:
                break
            data += packet

        report_dict = pickle.loads(data)
        try:
            if "node_name" in report_dict:
                report = SystemReport(**report_dict)
            else:
                report = ProcessReport(**report_dict)
            self.process_report(report)
        except ValidationError as e:
            logging.error("ValidationError: ", e)
        except Exception as e:
            logging.error(
                msg="Can't parse metric report", exc_info=traceback.print_exc()
            )

        client_socket.close()

    def process_report(self, report):
        try:
            if isinstance(report, SystemReport):
                node_name = report.node_name
                timestamp = report.timestamp
                del report.node_name, report.timestamp
                fields = self.convert_unit(
                    flatten(report.__dict__, self.config["data_separator"])
                )
                self.insert_metric(
                    timestamp,
                    {
                        "type": "node",
                        "node_name": node_name,
                    },
                    fields,
                )
            else:
                metadata = flatten(
                    {"metadata": report.metadata}, self.config["data_separator"]
                )
                timestamp = report.timestamp
                del report.metadata, report.timestamp
                fields = self.convert_unit(
                    flatten(report.__dict__, self.config["data_separator"])
                )
                self.insert_metric(timestamp, {"type": "process", **metadata}, fields)
        except Exception as e:
            print("Error processing report:", e)

    def convert_unit(self, report: dict):
        converted_report = report
        for key, value in report.items():
            # TODO: for instead of hard coded
            if isinstance(value, str):
                if "frequency" in key:
                    converted_report[key] = self.unit_conversion["frequency"][value]
                elif "mem" in key:
                    converted_report[key] = self.unit_conversion["mem"][value]
                elif "cpu" in key:
                    if "usage" in key:
                        converted_report[key] = self.unit_conversion["cpu"]["usage"][
                            value
                        ]
                elif "gpu" in key:
                    if "usage" in key:
                        converted_report[key] = self.unit_conversion["gpu"]["usage"][
                            value
                        ]
        return converted_report

    def get_lastest_timestamp(self):
        time_query = TimeQuery()
        timestamp = datetime.fromtimestamp(math.floor(time.time()))
        data = self.db.search(time_query >= timestamp)
        return [
            unflatten(
                {**datapoint.tags, **datapoint.fields}, self.config["data_separator"]
            )
            for datapoint in data
        ]

    def start(self):
        self.execution_flag = True
        self.server_thread.start()
        logging.info("node aggregator started")

    def stop(self):
        self.execution_flag = False
        self.server_thread.join()
        logging.info("node aggregator stopped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        help="config path",
        default="config/node_aggregator_config.yaml",
    )
    args = parser.parse_args()
    config_file = args.config
    config = yaml.safe_load(open(ODOP_PATH + config_file))
    node_aggregator = NodeAggregator(config)
    node_aggregator.start()
    while True:
        time.sleep(1)
