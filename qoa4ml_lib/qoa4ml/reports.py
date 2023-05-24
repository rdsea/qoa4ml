from typing import List
from .connector.amqp_connector import Amqp_Connector
from .connector.mqtt_connector import Mqtt_Connector
from .connector.prom_connector import Prom_Connector
from .probes import Gauge, Counter, Summary, Histogram
import json, uuid, time, traceback,sys
from .utils import merge_report, get_dict_at, load_config


class QoA_Report(object):
    # Init QoA Client
    def __init__(self):
        self.reset()

    def reset(self):
        self.report_list = []
        self.previous_report_instance = []
        self.previous_inference = []
        self.quality_report = {}
        self.execution_graph = {}
        self.report = {}

    def import_report_from_file(self, file_path):
        report = load_config(file_path)
        self.quality_report = report["quality"]
        self.execution_graph = report["execution_graph"]

    def import_pReport(self, reports):
        try:
            if isinstance(reports, list):
                for report in reports:
                    self.report_list.append(report)
                    self.previous_report_instance.append(report["execution_graph"]["last_instance"])
                    if "inference" in report["quality"]:
                        self.previous_inference.append(report["quality"]["inference"]["last_inference"])
            else:
                self.report_list.append(reports)
                self.previous_report_instance.append(reports["execution_graph"]["last_instance"])
                if "inference" in reports["quality"]:
                        self.previous_inference.append(reports["quality"]["inference"]["last_inference"])
        except Exception as e:
            print("[ERROR] - Error {} in import_pReport: {}".format(type(e),e.__traceback__))
            traceback.print_exception(*sys.exc_info())
        
        
    def build_execution_graph(self,metadata):
        try:
            self.execution_graph["instances"] = {}
            self.execution_graph["instances"][metadata["instances_id"]] = {}
            self.execution_graph["instances"][metadata["instances_id"]]["instance_name"] = metadata["instance_name"]
            self.execution_graph["instances"][metadata["instances_id"]]["method"] = metadata["method"]
            self.execution_graph["instances"][metadata["instances_id"]]["previous_instance"] = self.previous_report_instance
            for report in self.report_list:
                i_graph = report["execution_graph"]
                self.execution_graph = merge_report(self.execution_graph, i_graph)
            self.execution_graph["last_instance"] = metadata["instances_id"]
        except Exception as e:
            print("[ERROR] - Error {} in build_execution_graph: {}".format(type(e),e.__traceback__))
            traceback.print_exception(*sys.exc_info())
        return self.execution_graph
    
    def build_quality_report(self):
        for report in self.report_list:
            i_quality = report["quality"]
            self.quality_report = merge_report(self.quality_report,i_quality)
        return self.quality_report

    def generate_report(self, metadata, metric:list=None,reset=True):
        self.report["execution_graph"] = self.build_execution_graph(metadata)
        self.report["quality"] = self.build_quality_report()
        report = self.report.copy()
        if reset:
            self.reset()
        return report
    
    def observe_metric(self, metric, quality=True, service_quality=False, data_quality=False, infer_quality=False):
        if quality == True:
            if service_quality == True:
                if "service" not in self.quality_report:
                    self.quality_report["service"] = {}
                self.quality_report["service"] = merge_report(self.quality_report["service"],metric)
            elif data_quality == True:
                if "data" not in self.quality_report:
                    self.quality_report["data"] = {}
                self.quality_report["data"] = merge_report(self.quality_report["data"],metric)
            elif infer_quality == True:
                key,value = get_dict_at(metric)
                metric[key]["source"] = self.previous_inference
                if "inference" not in self.quality_report:
                    self.quality_report["inference"] = {}
                self.quality_report["inference"] = merge_report(self.quality_report["inference"],metric)
                self.quality_report["inference"]["last_inference"] = key