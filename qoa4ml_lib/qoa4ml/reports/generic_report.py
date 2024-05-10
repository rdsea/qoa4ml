from abc import ABC, abstractmethod

from ..datamodels.ml_report import QualityReport


class Report(ABC):
    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def generate_report(self, reset: bool = True) -> BaseReport:
        pass
