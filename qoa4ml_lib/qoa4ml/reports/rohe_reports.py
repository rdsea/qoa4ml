import copy
import time
from typing import Dict, List, Optional


from qoa4ml.datamodels.common_models import Metric
from qoa4ml.datamodels.datamodel_enum import ReportTypeEnum, StageNameEnum

from ..datamodels.configs import Client
from ..datamodels.ml_report import (
    ExecutionGraph,
    InferenceInstance,
    InferenceReport,
    LinkedInstance,
    MicroserviceInstance,
    RoheReportModel,
    StageReport,
)
from ..qoa_utils import load_config


class RoheReport:
    def __init__(self, clientConfig: Client, file_path: Optional[str] = None):
        self.client_config = copy.deepcopy(clientConfig)
        self.reset()
        self.init_time = time.time()

        if file_path:
            self.import_report_from_file(file_path)

    def reset(self):
        self.previous_report: List[RoheReportModel] = []
        self.inference_report = InferenceReport()
        self.execution_graph = ExecutionGraph(linked_list={})
        self.report = RoheReportModel()
        self.previous_microservice_instance = []

    def import_report_from_file(self, file_path: str):
        report = load_config(file_path)
        self.inference_report = InferenceReport(**report["inference_report"])
        self.execution_graph = ExecutionGraph(**report["execution_graph"])
        self.report = RoheReportModel(
            inference_report=self.inference_report, execution_graph=self.execution_graph
        )

    def combine_stage_report(
        self,
        current_stage_report: Dict[StageNameEnum, StageReport],
        previous_stage_report: Dict[StageNameEnum, StageReport],
    ):
        combined_stage_report: Dict[StageNameEnum, StageReport] = {}
        for stage_name, stage_report in previous_stage_report.items():
            new_stage_report = StageReport(name=stage_name, metrics={})
            if not stage_name in current_stage_report:
                current_stage_report[stage_name] = StageReport(
                    name=stage_name, metrics={}
                )
            for metric_name, instance_report_dict in stage_report.metrics.items():
                if not metric_name in current_stage_report[stage_name].metrics:
                    current_stage_report[stage_name].metrics[metric_name] = {}
                new_stage_report.metrics[metric_name] = {
                    **current_stage_report[stage_name].metrics[metric_name],
                    **instance_report_dict,
                }
            combined_stage_report[stage_name] = new_stage_report
        return combined_stage_report

    def process_previous_report(self, previous_report: RoheReportModel):
        self.previous_report.append(previous_report)
        if (
            not previous_report.inference_report
            or not previous_report.inference_report.ml_specific
            or not previous_report.inference_report.data
            or not previous_report.inference_report.service
            or not previous_report.execution_graph
        ):
            raise ValueError("Can't process empty previous report")

        # NOTE: service quality report
        self.inference_report.service = self.combine_stage_report(
            self.inference_report.service, previous_report.inference_report.service
        )

        # NOTE: data quality report
        self.inference_report.data = self.combine_stage_report(
            self.inference_report.data, previous_report.inference_report.data
        )

        # NOTE: ml-specific quality report
        if not self.inference_report.ml_specific:
            self.inference_report.ml_specific = (
                previous_report.inference_report.ml_specific
            )
            self.inference_report.ml_specific.end_point = None
        else:
            self.inference_report.ml_specific.linked_list.update(
                previous_report.inference_report.ml_specific.linked_list
            )

        # NOTE: execution graph
        if not self.execution_graph:
            self.execution_graph = previous_report.execution_graph

            self.inference_report.ml_specific.end_point = None
        else:
            self.execution_graph.linked_list.update(
                previous_report.execution_graph.linked_list
            )
        self.previous_microservice_instance.append(
            previous_report.execution_graph.end_point
        )
        self.report = RoheReportModel(
            inference_report=self.inference_report, execution_graph=self.execution_graph
        )

    def build_execution_graph(self):
        end_point = LinkedInstance(
            instance=MicroserviceInstance(
                id=self.client_config.id,
                name=self.client_config.name,
                functionality=self.client_config.functionality,
                stage=self.client_config.stage,
            ),
            previous=[
                previous_instance
                for previous_instance in self.previous_microservice_instance
            ],
        )
        self.execution_graph.linked_list[end_point.instance.id] = end_point
        self.execution_graph.end_point = end_point.instance

    def observe_metric(
        self, report_type: ReportTypeEnum, stage: StageNameEnum, metric: Metric
    ):
        if report_type == ReportTypeEnum.service or report_type == ReportTypeEnum.data:
            self.inference_report.service[stage].metrics[metric.metric_name].update(
                {self.client_config.id: metric}
            )
        else:
            raise ValueError(f"Can't handle report type {report_type}")

    def observe_inference(self, linked_instance: LinkedInstance[InferenceInstance]):
        if self.inference_report.ml_specific:
            self.inference_report.ml_specific.linked_list.update(
                {self.client_config.id: linked_instance}
            )
            self.inference_report.ml_specific.end_point = linked_instance.instance

    def observe_inference_metric(
        self,
        metric: Optional[Metric] = None,
        metric_list: Optional[List[Metric]] = None,
    ):
        if (
            self.inference_report.ml_specific
            and self.inference_report.ml_specific.end_point
        ):
            if metric:
                self.inference_report.ml_specific.end_point.metrics.append(metric)
            elif metric_list:
                self.inference_report.ml_specific.end_point.metrics.extend(metric_list)
        else:
            raise Exception("Can't observe new metric to missing end_point")

    def generate_report(self, reset: bool = True):
        self.report.metadata["client_config"] = copy.deepcopy(self.client_config)
        self.report.metadata["timestamp"] = time.time()
        self.report.metadata["runtime"] = (
            self.report.metadata["timestamp"] - self.init_time
        )
        report = copy.deepcopy(self.report)
        if reset:
            self.reset()
        return report
