from typing import List
from .connector.amqp_connector import Amqp_Connector
from .connector.mqtt_connector import Mqtt_Connector
from .connector.prom_connector import Prom_Connector
from .metric import Gauge, Counter, Summary, Histogram
import json, uuid, time, traceback,sys
from .utils import merge_report, get_dict_at, load_config


class QoaReport(object):
    # Init QoA Client
    def __init__(self, clientConfig):
        self.clientConfig = clientConfig.copy()
        self.reset()
        self.initTime = time.time()

    def reset(self):
        self.reportList = []
        self.previousReportInstance = []
        self.previousInference = []
        self.qualityReport = {}
        self.computationGraph = {}
        self.report = {}

    def import_report_from_file(self, file_path):
        report = load_config(file_path)
        self.qualityReport = report["quality"]
        self.computationGraph = report["computationGraph"]
    
    def processPReport(self, report):
        self.reportList.append(report)
        self.previousReportInstance.append(report["computationGraph"]["last_instance"])
        if "inference" in report["quality"]:
            self.previousInference.append(report["quality"]["inference"]["last_inference"])

    def importPReport(self, reports):
        try:
            if isinstance(reports, list):
                for report in reports:
                    self.processPReport(report)
            else:
                self.processPReport(reports)
        except Exception as e:
            print("[ERROR] - Error {} in importPReport: {}".format(type(e),e.__traceback__))
            traceback.print_exception(*sys.exc_info())
        
        
    def buildComputationGraph(self):
        try:
            self.computationGraph["instances"] = {}
            self.computationGraph["instances"][self.clientConfig["instances_id"]] = {}
            self.computationGraph["instances"][self.clientConfig["instances_id"]]["instance_name"] = self.clientConfig["instance_name"]
            self.computationGraph["instances"][self.clientConfig["instances_id"]]["method"] = self.clientConfig["method"]
            self.computationGraph["instances"][self.clientConfig["instances_id"]]["previous_instance"] = self.previousReportInstance
            for report in self.reportList:
                i_graph = report["computationGraph"]
                self.computationGraph = merge_report(self.computationGraph, i_graph)
            self.computationGraph["last_instance"] = self.clientConfig["instances_id"]
        except Exception as e:
            print("[ERROR] - Error {} in buildComputationGraph: {}".format(type(e),e.__traceback__))
            traceback.print_exception(*sys.exc_info())
        return self.computationGraph
    
    def build_qualityReport(self):
        for report in self.reportList:
            i_quality = report["quality"]
            self.qualityReport = merge_report(self.qualityReport,i_quality)
        return self.qualityReport

    def generateReport(self, metric:list=None,reset=True):
        # Todo: only report on specific metrics
        self.report["computationGraph"] = self.buildComputationGraph()
        self.report["quality"] = self.build_qualityReport()
        self.report["metadata"] = self.clientConfig.copy()
        self.report["metadata"]["timestamp"] = time.time()
        self.report["metadata"]["runtime"] = self.report["metadata"]["timestamp"] - self.initTime
        report = self.report.copy()
        if reset:
            self.reset()
        return report
    
    def observeMetric(self, metric, quality=True, service_quality=False, data_quality=False, infer_quality=False):
        if quality == True:
            if service_quality == True:
                if "service" not in self.qualityReport:
                    self.qualityReport["service"] = {}
                self.qualityReport["service"] = merge_report(self.qualityReport["service"],metric)
            elif data_quality == True:
                if "data" not in self.qualityReport:
                    self.qualityReport["data"] = {}
                self.qualityReport["data"] = merge_report(self.qualityReport["data"],metric)
            elif infer_quality == True:
                key,value = get_dict_at(metric)
                metric[key]["source"] = self.previousInference
                if "inference" not in self.qualityReport:
                    self.qualityReport["inference"] = {}
                self.qualityReport["inference"] = merge_report(self.qualityReport["inference"],metric)
                self.qualityReport["inference"]["last_inference"] = key


class Report(object):
    def __init__(self, report:dict=None):
        self.report = report
        if report:
            self.load_metadata()
        self.t_report = self.report.copy()
    
    def set_report(self, report:dict):
        self.report = report
        self.t_report = self.report.copy()
        self.load_metadata()

    def load_metadata(self):
        self.application = self.report["application"]
        self.client_id = self.report["client_id"]
        self.instance_name = self.report["instance_name"]
        self.stageID = self.report["stage_id"]
        self.method = self.report["method"]
        self.roles = self.report["roles"]
        self.timestamp = self.report["timestamp"]
        self.runtime = self.report["runtime"]
    
    def load_computationGraph(self):
        self.computationGraph = self.report["computationGraph"]

    def load_metric(self):
        if self.t_report:
            pass

    def getMetric(self, metric_name, data_quality=False, service_quality=False, inference_quality=False):
        if data_quality:
            return self.get_data_quality(metric_name)
        elif service_quality:
            return self.get_service_quality(metric_name)
        elif inference_quality:
            return self.get_inference_quality(metric_name)
        else:
            return self.get_data_quality(metric_name)

    def get_responsetime_list(self, sum=True):
        if self.t_report:
            data = self.t_report["quality"]["data"]
            result = 0
            responsetimes = []
            for stage in data:
                stage_i = data[stage]
                if "Response Time" in stage_i:
                    dict_res = stage_i.pop("Response Time")
                    for instance in dict_res:
                        res = dict_res[instance]
                        res["instance_id"] = instance
                        responsetimes.append(res)

    def get_data_quality(self, metric_name):
        if self.t_report:
            data = self.t_report["quality"]["data"]
        else:
            return None

    def get_service_quality(self, metric_name):
        if self.t_report:
            data = self.t_report["quality"]["service"]
        else:
            return None

    def get_inference_quality(self, metric_name):
        pass