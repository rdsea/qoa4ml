from abc import ABC, abstractmethod


class BaseConnector(ABC):
    @abstractmethod
    def send_report(self, body_message: str):
        pass
