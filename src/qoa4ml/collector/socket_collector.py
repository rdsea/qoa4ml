import pickle
import socket
from typing import Callable

from ..config.configs import SocketCollectorConfig
from .base_collector import BaseCollector


class SocketCollector(BaseCollector):
    def __init__(self, config: SocketCollectorConfig, process_report: Callable) -> None:
        self.config = config
        self.host = config.host
        self.port = config.port
        self.backlog = config.backlog
        self.bufsize = config.bufsize
        self.process_report = process_report
        self.execution_flag = True

    def start_collecting(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((self.host, self.port))
        server_socket.listen(self.backlog)
        while self.execution_flag:
            client_socket, _ = server_socket.accept()
            data = b""
            while True:
                packet = client_socket.recv(self.bufsize)
                if not packet:
                    break
                data += packet

            report = pickle.loads(data)
            self.process_report(report)
            client_socket.close()
