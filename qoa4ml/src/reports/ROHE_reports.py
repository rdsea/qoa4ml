import copy
import sys
import time
import traceback
from typing import List, Optional, Union

from qoa4ml.metric import PrometheusMetric

from ..datamodels.configs import Client

from ..datamodels.ml_report import (
    ExecutionGraph,
    InferenceQuality,
    LinkedInstance,
    ROHEReport,
)

from .generic_report import Report

from ..qoaUtils import get_dict_at, load_config, mergeReport, qoaLogger


class QoaReport(Report):
    def __init__(self, clientConfig: Client):
        self.client_config = copy.deepcopy(clientConfig)
        self.reset()
        self.init_time = time.time()

    def reset(self):
        self.report_list = []
        self.previous_report_instance = []
        self.previous_inference = []
        self.quality_report = InferenceQuality()
        self.execution_graph = ExecutionGraph(linked_list=[])
        self.report = ROHEReport()

    def import_report_from_file(self, file_path):
        report = load_config(file_path)
        self.quality_report = InferenceQuality(**report["quality"])
        self.execution_graph = ExecutionGraph(**report["computationGraph"])
        self.metadata = report["metadata"]

    def process_previous_report(self, previous_report: ROHEReport):
        report = copy.deepcopy(previous_report)
        self.report_list.append(report)
        if report.execution_graph:
            self.previous_report_instance.append(report.execution_graph.end_point)
        if report.quality and report.quality.ml_specific:
            self.previous_inference.append(report.quality.ml_specific.end_point)

    def import_previous_report(self, reports: Union[List[ROHEReport], ROHEReport]):
        try:
            if isinstance(reports, list):
                for report in reports:
                    self.process_previous_report(report)
            else:
                self.process_previous_report(reports)
        except Exception as e:
            qoaLogger.error(
                "Error {} in importPReport: {}".format(type(e), e.__traceback__)
            )
            traceback.print_exception(*sys.exc_info())

    def build_execution_graph(self):
        try:
            self.execution_graph["instances"] = {}
            self.execution_graph["instances"][self.client_config["instances_id"]] = {}
            self.execution_graph["instances"][self.client_config["instances_id"]][
                "instance_name"
            ] = self.client_config["instance_name"]
            self.execution_graph["instances"][self.client_config["instances_id"]][
                "method"
            ] = self.client_config["method"]
            self.execution_graph["instances"][self.client_config["instances_id"]][
                "previous_instance"
            ] = self.previous_report_instance
            for report in self.report_list:
                i_graph = report["computationGraph"]
                self.execution_graph = mergeReport(self.execution_graph, i_graph)
            self.execution_graph["last_instance"] = self.client_config["instances_id"]

            self.execution_graph.linked_list.append(LinkedInstance(microservice=Micr))
        except Exception as e:
            qoaLogger.error(
                "Error {} in buildComputationGraph: {}".format(type(e), e.__traceback__)
            )
            traceback.print_exception(*sys.exc_info())
        return self.execution_graph

    def build_quality_report(self):
        for report in self.report_list:
            i_quality = report["quality"]
            # self.quality_report = mergeReport(self.quality_report, i_quality)
        return self.quality_report

    def generate_report(self, reset=True):
        # Todo: only report on specific metrics

        self.report.computation_graph = self.build_execution_graph()
        self.report.quality = self.build_quality_report()
        self.report.metadata = copy.deepcopy(self.client_config)
        self.report.metadata["timestamp"] = time.time()
        self.report.metadata["runtime"] = (
            self.report.metadata["timestamp"] - self.init_time
        )
        report = copy.deepcopy(self.report)
        if reset:
            self.reset()
        return report

    def observe_metric(self, metric: PrometheusMetric):
        metricReport = {}
        metricReport[self.client_config["stageID"]] = {}
        metricReport[self.client_config["stageID"]][metric.name] = {}
        metricReport[self.client_config["stageID"]][metric.name][
            self.client_config["instances_id"]
        ] = metric.value

        if metric.category == 0:
            if (
                metric.name
                in self.quality_report.service[self.client_config.stage].metric.keys()
            ):
                self.quality_report.service[self.client_config.stage].metric[
                    metric.name
                ].records.append(metric.value)

        elif metric.category == 1:
            if "data" not in self.quality_report:
                self.quality_report["data"] = {}
            self.quality_report["data"] = mergeReport(
                self.quality_report["data"], metricReport
            )
        elif metric.category == 2:
            key, value = get_dict_at(metricReport)
            metricReport[key]["source"] = self.previousInference
            if "inference" not in self.qualityReport:
                self.qualityReport["inference"] = {}
            self.qualityReport["inference"] = mergeReport(
                self.qualityReport["inference"], metricReport
            )
            self.qualityReport["inference"]["last_inference"] = key

    def observe_inference_metric(
        self, infReport: ROHEReport, dependency: Optional[List[LinkedInstance]] = None
    ):
        key, value = get_dict_at(infReport)
        if dependency:
            infReport[key]["source"] = dependency
        else:
            infReport[key]["source"] = self.previous_inference
        if "inference" not in self.quality_report:
            self.quality_report["inference"] = {}
        self.quality_report["inference"] = mergeReport(
            self.quality_report["inference"], infReport
        )
        self.quality_report["inference"]["last_inference"] = key

    def sort_computation_graph(self):
        instanceList = {}
        source = [self.execution_graph["last_instance"]]
        rank = 0
        while len(source) != 0:
            new_source = []
            for ikey in source:
                instanceList.update({ikey: rank})
                new_source.extend(
                    self.execution_graph["instances"][ikey]["previous_instance"]
                )
            source = new_source
            rank += 1
        return instanceList

    def get_metric(self, metric_name):
        metricReport = []
        for stage in self.quality_report:
            if metric_name in self.quality_report[stage]:
                pass
            # Todo
