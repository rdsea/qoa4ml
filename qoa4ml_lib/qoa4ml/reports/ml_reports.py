import copy
import time
from typing import Dict

from ..config.configs import ClientInfo
from ..lang.common_models import Metric
from ..reports.ml_report_model import BaseReport
from .abstract_report import AbstractReport


class MLReport(AbstractReport):
    def __init__(self, clientConfig: ClientInfo):
        self.client_config = copy.deepcopy(clientConfig)
        self.reset()
        self.init_time = time.time()

    def reset(self):
        pass

    def process_previous_report(self, previous_report_dict: Dict):
        return super().process_previous_report(previous_report_dict)

    def observe_metric(self, report_type, stage, metric: Metric):
        return super().observe_metric(report_type, stage, metric)

    def observe_inference(self, inference_value):
        return super().observe_inference(inference_value)

    def observe_inference_metric(self, metric: Metric):
        return super().observe_inference_metric(metric)

    def generate_report(self, reset: bool = True) -> BaseReport:
        return super().generate_report(reset)
