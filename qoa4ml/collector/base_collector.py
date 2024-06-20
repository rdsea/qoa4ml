from abc import ABC, abstractmethod


class BaseCollector(ABC):
    @abstractmethod
    def start_collecting(self):
        pass
