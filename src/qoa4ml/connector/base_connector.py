from abc import ABC, abstractmethod


class BaseConnector(ABC):
    @abstractmethod
    def send_report(self, body_message: str):
        pass

    def check_connection(self) -> bool:
        return True
