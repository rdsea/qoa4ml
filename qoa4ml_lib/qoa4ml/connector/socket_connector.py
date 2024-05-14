import logging
import pickle
import socket

from qoa4ml.datamodels.configs import SocketConnectorConfig

from .base_connector import BaseConnector


class SocketConnector(BaseConnector):
    def __init__(self, config: SocketConnectorConfig):
        self.config = config
        self.host = config.host
        self.port = config.port

    def send_report(self, body_message: str):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((self.host, self.port))
            serialized_message = pickle.dumps(body_message)
            client_socket.sendall(serialized_message)
            client_socket.close()
        except ConnectionRefusedError:
            logging.error("Connection to aggregator refused")
