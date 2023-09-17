from typing import List
from .connector.amqp_connector import Amqp_Connector
from .connector.mqtt_connector import Mqtt_Connector
from .connector.prom_connector import Prom_Connector
from .metric import Gauge, Counter, Summary, Histogram
import json, uuid, time, traceback,sys, copy
from .qoaUtils import mergeReport, get_dict_at, load_config, qoaLogger


class QoaReport(object):
    # Init QoA Client
    def __init__(self, clientConfig):
        self.clientConfig = copy.deepcopy(clientConfig)
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
        self.metadata = report["metadata"]
    
    def processPReport(self, pReport):
        report = copy.deepcopy(pReport)
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
            qoaLogger.error("Error {} in importPReport: {}".format(type(e),e.__traceback__))
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
                self.computationGraph = mergeReport(self.computationGraph, i_graph)
            self.computationGraph["last_instance"] = self.clientConfig["instances_id"]
        except Exception as e:
            qoaLogger.error("Error {} in buildComputationGraph: {}".format(type(e),e.__traceback__))
            traceback.print_exception(*sys.exc_info())
        return self.computationGraph
    
    def buildQualityReport(self):
        for report in self.reportList:
            i_quality = report["quality"]
            self.qualityReport = mergeReport(self.qualityReport,i_quality)
        return self.qualityReport

    def generateReport(self, metric:list=None,reset=True):
        # Todo: only report on specific metrics
        self.report["computationGraph"] = self.buildComputationGraph()
        self.report["quality"] = self.buildQualityReport()
        self.report["metadata"] = copy.deepcopy(self.clientConfig)
        self.report["metadata"]["timestamp"] = time.time()
        self.report["metadata"]["runtime"] = self.report["metadata"]["timestamp"] - self.initTime
        report = copy.deepcopy(self.report)
        if reset:
            self.reset()
        return report
    
    def observeMetric(self, metric):
        metricReport = {}
        metricReport[self.clientConfig["stage_id"]] = {}
        metricReport[self.clientConfig["stage_id"]][metric.name] = {}
        metricReport[self.clientConfig["stage_id"]][metric.name][self.clientConfig["instances_id"]] = metric.value

        if metric.category == 0:
            if "performance" not in self.qualityReport:
                self.qualityReport["performance"] = {}
            self.qualityReport["performance"] = mergeReport(self.qualityReport["performance"],metricReport)
        elif metric.category == 1:
            if "data" not in self.qualityReport:
                self.qualityReport["data"] = {}
            self.qualityReport["data"] = mergeReport(self.qualityReport["data"],metricReport)
        # elif metric.category == 2:
        #     key,value = get_dict_at(metricReport)
        #     metricReport[key]["source"] = self.previousInference
        #     if "inference" not in self.qualityReport:
        #         self.qualityReport["inference"] = {}
        #     self.qualityReport["inference"] = mergeReport(self.qualityReport["inference"],metricReport)
        #     self.qualityReport["inference"]["last_inference"] = key

    def observeInferenceMetric(self, infReport, dependency=None):

        key,value = get_dict_at(infReport)
        if dependency != None:
            infReport[key]["source"] = dependency
        else:
            infReport[key]["source"] = self.previousInference
        if "inference" not in self.qualityReport:
            self.qualityReport["inference"] = {}
        self.qualityReport["inference"] = mergeReport(self.qualityReport["inference"],infReport)
        self.qualityReport["inference"]["last_inference"] = key

    def sortComputationGraph(self):
        instanceList = {}
        source = [self.computationGraph["last_instance"]]
        rank = 0
        while len(source) != 0:
            new_source = []
            for ikey in source:
                instanceList.update({ikey:rank})
                new_source.extend(self.computationGraph["instances"][ikey]["previous_instance"])
            source = new_source
            rank += 1
        return instanceList




    def getMetric(self, metric_name):
        metricReport = []
        for stage in self.qualityReport:
            if metric_name in self.qualityReport[stage]:
                pass
            # Todo 
        
