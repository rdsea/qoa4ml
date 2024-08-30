import logging
import pickle
import socket
import time
from typing import Optional

from ..config.configs import SocketConnectorConfig
from .base_connector import BaseConnector


class SocketConnector(BaseConnector):
    def __init__(self, config: SocketConnectorConfig):
        self.config = config
        self.host = config.host
        self.port = config.port

    def send_report(self, body_message: str, log_path: Optional[str] = None):
        try:
            start = time.time()
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.host, self.port))
            serialized_message = pickle.dumps(body_message)
            client_socket.sendall(serialized_message)
            client_socket.close()
            if log_path:
                with open(log_path, "a", encoding="utf-8") as file:
                    file.write(str((time.time() - start) * 1000) + "\n")
        except ConnectionRefusedError:
            logging.error("Connection to aggregator refused")
