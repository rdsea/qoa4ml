import socket
import pickle
from pydantic import BaseModel, ValidationError
from tinyflux import TinyFlux, Point
from datetime import datetime

class ProcessReport(BaseModel):
    metadata: dict
    timestamp: int
    cpu_usage: dict
    mem_usage: dict

class SystemReport(BaseModel):
    node_name: str
    timestamp: int
    cpu_usage: dict
    gpu_usage: dict
    mem_usage: dict

class NodeExporter:
    def __init__(self, config):
        self.config = config
        self.db = TinyFlux("./db.csv")

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

        while True:
            client_socket, addr = server_socket.accept()
            print("Connected to", addr)
            self.handle_client(client_socket)

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
            print(report)
            self.process_report(report)
        except ValidationError as e:
            print("Validation error:", e)
        except Exception as e:
            print("Error processing report:", e)

        client_socket.close()

    def process_report(self, report):
        try:
            if isinstance(report, SystemReport): 
                fields = {
                    **report.cpu_usage, 
                    **report.gpu_usage, 
                    **report.mem_usage
                }
                self.insert_metric(report.timestamp, {"node_name": report.node_name}, fields)
            else: 
                fields = {
                    **report.cpu_usage, 
                    **report.mem_usage
                }
                self.insert_metric(report.timestamp, report.metadata, fields)
        except Exception as e:
            print("Error processing report:", e)


if __name__ == "__main__":
    node_exporter = NodeExporter({})
    node_exporter.start_server("127.0.0.1", 12345)
