from abc import ABC, abstractmethod


class BaseConnector(ABC):
    @abstractmethod
    def send_data(self, body_message: str, *args, **kwargs):
        pass
