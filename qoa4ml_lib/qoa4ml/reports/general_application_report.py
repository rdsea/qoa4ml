import copy
import time
from typing import Dict, List
from uuid import UUID

from ..config.configs import ClientInfo
from ..lang.common_models import Metric
from ..lang.datamodel_enum import ReportTypeEnum
from ..reports.ml_report_model import (
    FlattenMetric,
    GeneralApplicationReportModel,
    MicroserviceInstance,
)
from .abstract_report import AbstractReport


class GeneralApplicationReport(AbstractReport):
    def __init__(self, clientConfig: ClientInfo):
        self.client_config = copy.deepcopy(clientConfig)
        self.reset()
        self.init_time = time.time()

    def reset(self):
        self.report = GeneralApplicationReportModel()

        self.execution_instance = MicroserviceInstance(
            id=UUID(self.client_config.id),
            name=self.client_config.name,
            functionality=self.client_config.functionality,
            stage=self.client_config.stage_id,
        )
        self.previous_reports: List[MicroserviceInstance] = []

    def process_previous_report(self, previous_report_dict: Dict):
        previous_report = GeneralApplicationReportModel(**previous_report_dict)
        # NOTE: assume that the last metric is observed by the previous instance
        self.previous_reports.append(previous_report.metrics[-1].instance)
        for metric in previous_report.metrics:
            self.report.metrics.append(metric)

    def observe_metric(self, report_type, stage, metric: Metric):
        flatten_metric = FlattenMetric(
            metric_name=metric.metric_name,
            records=metric.records,
            unit=metric.unit,
            description=metric.description,
            stage=stage,
            report_type=report_type,
            instance=self.execution_instance,
            previous_instances=self.previous_reports,
        )
        self.report.metrics.append(flatten_metric)

    def observe_inference(self, inference_value):
        # TODO: may not be a great idea
        flatten_metric = FlattenMetric(
            metric_name="Inference",
            records=inference_value,
            stage=self.client_config.stage_id,
            report_type=ReportTypeEnum.ml_specific,
            instance=self.execution_instance,
            previous_instances=self.previous_reports,
        )
        self.report.metrics.append(flatten_metric)

    def observe_inference_metric(self, metric: Metric):
        flatten_metric = FlattenMetric(
            metric_name=metric.metric_name,
            records=metric.records,
            unit=metric.unit,
            description=metric.description,
            stage=self.client_config.stage_id,
            report_type=ReportTypeEnum.ml_specific,
            instance=self.execution_instance,
            previous_instances=self.previous_reports,
        )
        self.report.metrics.append(flatten_metric)
