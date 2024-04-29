import copy
import sys
import time
import traceback
from typing import Dict, List, Optional, Union

from qoa4ml.datamodels.datamodel_enum import StageNameEnum
from qoa4ml.metric import PrometheusMetric

from ..datamodels.configs import Client
from ..datamodels.ml_report import (
    ExecutionGraph,
    InferenceReport,
    RoheReportModel,
    StageReport,
)
from ..qoa_utils import get_dict_at, load_config, mergeReport, qoaLogger

from devtools import debug


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
            new_stage_report = StageReport(name=stage_name, metric={})
            if not stage_name in current_stage_report:
                current_stage_report[stage_name] = StageReport(
                    name=stage_name, metric={}
                )
            for metric_name, instance_report_dict in stage_report.metric.items():
                if not metric_name in current_stage_report[stage_name].metric:
                    current_stage_report[stage_name].metric[metric_name] = {}
                new_stage_report.metric[metric_name] = (
                    current_stage_report[stage_name].metric[metric_name]
                    | instance_report_dict
                )
            combined_stage_report[stage_name] = new_stage_report
        return combined_stage_report

    def process_previous_report(self, previous_report: RoheReportModel):
        self.previous_report.append(previous_report)
        if (
            not previous_report.inference_report
            or not previous_report.inference_report.ml_specific
            or not previous_report.inference_report.data
            or not previous_report.inference_report.service
        ):
            raise ValueError("Can't process empty previous report")
        self.inference_report.service = self.combine_stage_report(
            self.inference_report.service, previous_report.inference_report.service
        )
        self.inference_report.data = self.combine_stage_report(
            self.inference_report.data, previous_report.inference_report.data
        )
        if not self.inference_report.ml_specific:
            self.inference_report.ml_specific = (
                previous_report.inference_report.ml_specific
            )
        else:
            self.inference_report.ml_specific.linked_list |= (
                previous_report.inference_report.ml_specific.linked_list
            )
        self.report = RoheReportModel(
            inference_report=self.inference_report, execution_graph=self.execution_graph
        )

    def generate_report(self, reset: bool = True):
        pass
