import copy
import time

from ..config.configs import ClientInfo
from ..lang.common_models import Metric
from ..reports.ml_report_model import GeneralApplicationReportModel
from .abstract_report import AbstractReport


class GeneralApplicationReport(AbstractReport):
    def __init__(self, clientConfig: ClientInfo):
        self.client_config = copy.deepcopy(clientConfig)
        self.reset()
        self.init_time = time.time()

    def reset(self):
        self.report = GeneralApplicationReportModel()

    def process_previous_report(self, previous_report: GeneralApplicationReportModel):
        for metric in previous_report.metrics:
            self.report.metrics.append(metric)

    def observe_metric(self, report_type, stage, metric: Metric):
        pass
