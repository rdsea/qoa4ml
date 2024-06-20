import copy
import time
from typing import Dict, List
from uuid import UUID, uuid4

from ..config.configs import ClientInfo
from ..lang.common_models import Metric
from ..lang.datamodel_enum import ReportTypeEnum
from ..reports.ml_report_model import (
    BaseReport,
    GeneralMlInferenceReport,
    InferenceInstance,
    StageReport,
)
from .abstract_report import AbstractReport


class MLReport(AbstractReport):
    def __init__(self, clientConfig: ClientInfo):
        self.client_config = copy.deepcopy(clientConfig)
        self.reset()
        self.init_time = time.time()

    def reset(self):
        self.previous_report: List[GeneralMlInferenceReport] = []
        self.report = GeneralMlInferenceReport()

    def combine_stage_report(
        self,
        current_stage_report: Dict[str, StageReport],
        previous_stage_report: Dict[str, StageReport],
    ):
        combined_stage_report: Dict[str, StageReport] = {}
        for stage_name, stage_report in previous_stage_report.items():
            new_stage_report = StageReport(name=stage_name, metrics={})
            if stage_name not in current_stage_report:
                current_stage_report[stage_name] = StageReport(
                    name=stage_name, metrics={}
                )
            for metric_name, instance_report_dict in stage_report.metrics.items():
                if metric_name not in current_stage_report[stage_name].metrics:
                    current_stage_report[stage_name].metrics[metric_name] = {}
                new_stage_report.metrics[metric_name] = {
                    **current_stage_report[stage_name].metrics[metric_name],
                    **instance_report_dict,
                }
            combined_stage_report[stage_name] = new_stage_report
        return combined_stage_report

    def process_previous_report(self, previous_report_dict: Dict):
        previous_report = GeneralMlInferenceReport(**previous_report_dict)
        self.previous_report.append(previous_report)

        # NOTE: service quality report
        self.report.service = self.combine_stage_report(
            self.report.service, previous_report.service
        )

        # NOTE: data quality report
        self.report.data = self.combine_stage_report(
            self.report.data, previous_report.data
        )
        # NOTE: ml inference report
        #
        self.report.ml_inference |= previous_report.ml_inference

    def observe_metric(self, report_type, stage, metric: Metric):
        if stage == "":
            raise ValueError("Stage name can't be empty")
        if report_type == ReportTypeEnum.service:
            if stage not in self.report.service:
                self.report.service[stage] = StageReport(name=stage, metrics={})
            if metric.metric_name not in self.report.service[stage].metrics:
                self.report.service[stage].metrics[metric.metric_name] = {}

            self.report.service[stage].metrics[metric.metric_name] |= {
                UUID(self.client_config.id): metric
            }

        elif report_type == ReportTypeEnum.data:
            if stage not in self.report.data:
                self.report.data[stage] = StageReport(name=stage, metrics={})
            if metric.metric_name not in self.report.data[stage].metrics:
                self.report.data[stage].metrics[metric.metric_name] = {}

            self.report.data[stage].metrics[metric.metric_name] |= {
                UUID(self.client_config.id): metric
            }
        else:
            raise ValueError(f"Can't handle report type {report_type}")

    def observe_inference(self, inference_value):
        if self.client_config.id in self.report.ml_inference:
            raise RuntimeWarning(
                "Inference existed, will overrride the existing inference"
            )
        else:
            self.report.ml_inference[self.client_config.id] = InferenceInstance(
                inference_id=uuid4(),
                instance_id=UUID(self.client_config.id),
                functionality=self.client_config.functionality,
                prediction=inference_value,
            )

    def observe_inference_metric(self, metric: Metric):
        if self.client_config.id in self.report.ml_inference:
            self.report.ml_inference[self.client_config.id].metrics.append(metric)
        else:
            self.report.ml_inference[self.client_config.id] = InferenceInstance(
                inference_id=uuid4(),
                instance_id=UUID(self.client_config.id),
                functionality=self.client_config.functionality,
                metrics=[metric],
            )

    def generate_report(self, reset: bool = True) -> BaseReport:
        self.report.metadata["client_config"] = copy.deepcopy(self.client_config)
        self.report.metadata["timestamp"] = time.time()
        self.report.metadata["runtime"] = (
            self.report.metadata["timestamp"] - self.init_time
        )
        report = copy.deepcopy(self.report)
        if reset:
            self.reset()
        return report
