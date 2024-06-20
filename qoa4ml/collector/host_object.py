from abc import ABC, abstractmethod


class HostObject(ABC):
    @abstractmethod
    def message_processing(self, ch, method, props, body):
        pass
