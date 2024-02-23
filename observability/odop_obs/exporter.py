import socket
import pickle
from threading import Thread
import time

import yaml
from pydantic import BaseModel, ValidationError
from tinyflux.storages import MemoryStorage
from tinyflux import TinyFlux, Point, TimeQuery
from datetime import datetime
from fastapi import FastAPI
from flatten_dict import flatten, unflatten


class ProcessReport(BaseModel):
    metadata: dict
    timestamp: int
    usage: dict


class SystemReport(BaseModel):
    node_name: str
    timestamp: int
    cpu: dict
    gpu: dict
    mem: dict


class NodeExporter:
    def __init__(self, config, unit_conversion):
        self.config = config
        self.unit_conversion = unit_conversion
        # self.db = TinyFlux(storage=MemoryStorage)
        self.db = TinyFlux("./db.csv")
        self.last_timestamp = time.time()

    def insert_metric(self, timestamp: int, tags: dict, fields: dict):
        datapoint = Point(
            time=datetime.fromtimestamp(timestamp), tags=tags, fields=fields
        )
        self.db.insert(datapoint)

    def start_server(self, host, port):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(5)

        print("Node Exporter server listening on", (host, port))
        last_print = time.time()
        while True:
            client_socket, addr = server_socket.accept()
            print("Connected to", addr)
            self.handle_client(client_socket)
            if time.time() - last_print > 1:
                self.query_get_lastest_timestamp()
                last_print = time.time()

    def handle_client(self, client_socket):
        data = b""
        while True:
            packet = client_socket.recv(4096)
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
            print("Validation error:", e)
        except Exception as e:
            print("Error processing report:", e)

        client_socket.close()

    def process_report(self, report):
        try:
            if isinstance(report, SystemReport):
                node_name = report.node_name
                timestamp = report.timestamp
                del report.node_name, report.timestamp
                fields = self.convert_unit(flatten(report.__dict__, "dot"))
                self.insert_metric(
                    timestamp,
                    {
                        "type": "node",
                        "node_name": node_name,
                    },
                    fields,
                )
            else:
                metadata = flatten({"metadata": report.metadata}, "dot")
                timestamp = report.timestamp
                del report.metadata, report.timestamp
                fields = self.convert_unit(flatten(report.__dict__, "dot"))
                self.insert_metric(timestamp, {"type": "process", **metadata}, fields)
        except Exception as e:
            print("Error processing report:", e)

    def convert_unit(self, report: dict):
        converted_report = report
        for key, value in report.items():
            if isinstance(value, str):
                if "frequency" in key:
                    converted_report[key] = self.unit_conversion["frequency"][value]
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
                elif "mem" in key:
                    converted_report[key] = self.unit_conversion["mem"][value]
        return converted_report

    def query_get_lastest_timestamp(self):
        time_query = TimeQuery()
        data = self.db.search(
            time_query > datetime.fromtimestamp(self.last_timestamp - 1)
        )
        self.last_timestamp = time.time()
        return [unflatten({**datapoint.tags, **datapoint.fields}, 'dot') for datapoint in data]


node_exporter = NodeExporter({}, yaml.safe_load(open("./unit_conversion.yaml")))
node_exporter_handle_client_thread = Thread(
    target=node_exporter.start_server, args=("127.0.0.1", 12345)
)
node_exporter_handle_client_thread.daemon = True
node_exporter_handle_client_thread.start()
app = FastAPI()


@app.get("/latest_timestamp")
async def get_latest_timestamp():
    return {"latest_timestamp": node_exporter.query_get_lastest_timestamp()}
