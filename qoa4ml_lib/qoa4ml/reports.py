from typing import List
from .connector.amqp_connector import Amqp_Connector
from .connector.mqtt_connector import Mqtt_Connector
from .connector.prom_connector import Prom_Connector
from .probes import Gauge, Counter, Summary, Histogram
import json, uuid
import threading
from threading import Thread
import time, uuid
from datetime import datetime
import os
from .utils import get_proc_cpu, get_proc_mem

class Qoa_Client(object):
    # Init QoA Client
    def __init__(self, client_conf: dict, connector_conf: dict):
        '''
        Client configuration contains the information about the client and its configuration in form of dictionary
        Example: 
        { 
            "client_id": "aaltosea1",
            "component_id": "data_processing"
        }
        The `connector_conf` is the dictionary containing multiple connector configuration (amqp, mqtt, kafka)
        Example: 
        {
            "amqp_connector":{
                "class": "amqp",
                "conf":{
                    "end_point": "localhost",
                    "exchange_name": "qoa4ml",
                    "exchange_type": "topic",
                    "out_routing_key": "qoa.report.ml"
                }
            }
        }
        '''
        self.start_time = time.time()
        self.config = client_conf
        self.metrics = {}
        self.ex_metrics = {}
        self.connector = {}
        self.ex_report = {}
        self.timer_flag = False
        self.timer_start = 0
        self.report_list = []
        self.cur_instance_id = None
        self.cur_method = None
        self.cur_stage_id = None
        self.qoa_uuid = str(uuid.uuid4())
        self.cur_report = None
        self.data_quality = []
        self.proc_monitor_flag = False
        # Init all connectors in for loop 
        for key in connector_conf:
            self.connector[key] = self.init_connector(connector_conf[key])
        
        # Set default connector for sending monitoring data if not specify
        self.default_connector = list(self.connector.keys())[0]
        # self.add_metric(metric_conf)
        self.lock = threading.Lock()
        

    def init_connector(self, configuration: dict):
        if configuration["class"] == "amqp":
            return Amqp_Connector(configuration["conf"])
        if configuration["class"] == "mqtt":
            return Mqtt_Connector(configuration["conf"])

    def add_metric(self, metric_conf: dict):
        # Add multiple metrics 
        for key in metric_conf:
            self.metrics[key] = self.init_metric(key, metric_conf[key])

    def init_metric(self, name, configuration: dict):
        # init individual metrics
        if configuration["class"] == "Gauge":
            return Gauge(name, configuration["description"], configuration["default"])
        elif configuration["class"] == "Counter":
            return Counter(name, configuration["description"], configuration["default"])
        elif configuration["class"] == "Summary":
            return Summary(name, configuration["description"], configuration["default"])
        elif configuration["class"] == "Histogram":
            return Histogram(name, configuration["description"], configuration["default"])

    def get(self):
        # TO DO:
        return self.config


    def get_metric(self, key=None):
        # TO DO:
        if key == None:
            return self.metrics
        elif isinstance(key, list):
            return dict((k, self.metrics[k]) for k in key)
        else: 
            return self.metrics[key]
    
    def reset_metric(self, key=None):
        # TO DO:
        try:
            if key == None:
                for key in self.metrics:
                    self.metrics[key].reset()
            elif isinstance(key, list):
                for k in key:
                    self.metrics[k].reset()
            else: 
                return self.metrics[key].reset()
        except Exception as e:
            print("[Error]: {}".format(e))

    def set(self, key, value):
        # TO DO:
        try:
            self.config[key] = value
        except Exception as e:
            print("{} not found - {}".format(key,e))
    

    def generate_report(self, metric:list=None):
        report = {}
        report["metric"] = {}
        if metric == None:
            metric = list(self.metrics.keys())
        for key in metric:
            report["metric"][key] = self.metrics[key].get_val()
        return report
    
    def get_reports(self, report):
        self.report_list.append(report)

    def init_report(self, instance_id, method, stage_id):
        self.cur_instance_id = instance_id
        self.cur_method = method
        self.cur_stage_id = stage_id
        self.cur_report = {}
        self.cur_report[self.qoa_uuid] = {}
        self.cur_report[self.qoa_uuid]["instance_id"] = instance_id
        self.cur_report[self.qoa_uuid]["method"] = method
        self.cur_report["data_quality"] = {}
        self.cur_report["data_quality"][stage_id] = {}
        self.cur_report["performance"] = {}
        self.cur_report["performance"][stage_id] = {}
        self.cur_report["performance"][stage_id]["response_time"] = {}
        self.ex_report = {"prediction":{},"execution_graph":{"instances":{},"last_instance":[]},"data_quality":{}, "performance":{stage_id:{"response_time": {}}}}


    def build_report(self, response_time):
        for metric in self.data_quality:
            self.cur_report["data_quality"][self.cur_stage_id][metric["name"]] = {self.qoa_uuid:{"value": metric["value"]}}
        self.cur_report["performance"][self.cur_stage_id]["response_time"][self.qoa_uuid] = {"start_time":response_time[0], "execution_time":response_time[1]}


    def process_ex_report(self, response_time):
        self.build_report(response_time)
        f_report = self.ex_report
        f_prediction = f_report["prediction"]
        f_graph = f_report["execution_graph"]
        f_data_quality = f_report["data_quality"]
        f_performance = f_report["performance"]
        previous_instance = f_graph["last_instance"]
        for report in self.report_list:
            i_graph = report["execution_graph"]
            previous_instance.append(i_graph["last_instance"])
            f_graph["instances"].update(i_graph["instances"])

            i_data_quality = report["data_quality"]
            for stage in i_data_quality:
                if stage in f_data_quality:
                    for metric in i_data_quality[stage]:
                        if metric in f_data_quality[stage]:
                            f_data_quality[stage][metric].update(i_data_quality[stage][metric])
                        else:
                            f_data_quality[stage][metric] = i_data_quality[stage][metric]
                else:
                    f_data_quality[stage] = i_data_quality[stage]
            
            i_performance = report["performance"]
            for stage in i_performance:
                if stage in f_performance:
                    for metric in i_performance[stage]:
                        if metric in f_performance[stage]:
                            f_performance[stage][metric].update(i_performance[stage][metric])
                        else:
                            f_performance[stage][metric] = i_performance[stage][metric]
                else:
                    f_performance[stage] = i_performance[stage]
            f_prediction.update(report["prediction"])


        f_graph["last_instance"] = self.qoa_uuid
        self.cur_report[self.qoa_uuid]["previous_instance"] = previous_instance
        f_graph["instances"].update({self.qoa_uuid:self.cur_report[self.qoa_uuid]})
        f_data_quality.update(self.cur_report["data_quality"])
        f_performance[self.cur_stage_id].update(self.cur_report["performance"][self.cur_stage_id])
        self.report_list = []

    def ex_observe_confidence(self, value, confidence, dependency=[]):
        pre_uuid = str(uuid.uuid4())
        predictions = {}
        if dependency:
            for prediction in dependency:
                predictions.update(prediction)
            source = list(predictions.keys())
        else:
            source = []
        curr_prediction = {pre_uuid:{"value": value, "confidence": confidence, "source":source, "qoa_id": self.qoa_uuid}}
        self.ex_report["prediction"].update(curr_prediction)
        return curr_prediction
    
    def ex_observe_accuracy(self, prediction, accuracy):
        keys = list(prediction.keys())
        prediction[keys[0]]["accuracy"] = accuracy
        self.ex_report["prediction"].update(prediction)
    
    def ex_observe_data_quality(self, name, value):
        self.data_quality.append({"name":name, "value":value})

    def timer(self):
        if self.timer_flag == False:
            self.timer_flag = True
            self.timer_start = time.time()
            return []
        else:
            self.timer_flag = False
            return [self.timer_start,time.time()-self.timer_start]

    
    def ex_set_metric(self, metric, value):
        if "performance" not in self.ex_report:
            self.ex_report["performance"] = {}
        self.ex_report["performance"][self.cur_stage_id].update({metric:{self.qoa_uuid:{"value":value}}})

    def ex_reset(self):
        self.ex_report = {"prediction":{},"execution_graph":{"instances":{},"last_instance":[]},"data_quality":{}, "performance":{self.cur_stage_id:{"response_time": {}}}}
        self.report_list = []

    def ex_remove(self, metric):
        self.ex_report["Metrics"].pop(metric)

    def report_external(self, response_time, submit=False):
        self.process_ex_report(response_time)
        if submit:
            self.report(report=self.ex_report)
        report = self.ex_report.copy()
        self.ex_reset()
        return report

    


    def asyn_report(self, metrics:list=None, report:dict = None, connectors:list=None):
        client_inf = self.config.copy()
        client_inf['timestamp'] = time.time()
        client_inf['runtime'] = time.time() - self.start_time

        if (report == None):
            report = self.generate_report(metrics)
        report.update(client_inf)
        body_mess = json.dumps(report)
        self.lock.acquire()
        if connectors == None:
            self.connector[self.default_connector].send_data(body_mess,str(uuid.uuid4()))
        else:
            for connector in connectors:
                print(connector)
        self.lock.release()

    def report(self, metrics:list=None, report: dict = None, connectors:list=None):
        sub_thread = Thread(target=self.asyn_report, args=(metrics, report, connectors))
        sub_thread.start()


    def __str__(self):
        return str(self.config) + '\n' + str(self.connector)
    
    def process_report(self, interval:int, pid:int = None):
        report = {}
        while self.proc_monitor_flag:
            try:
                report["proc_cpu_stats"] = get_proc_cpu()
            except Exception as e:
                print("Unable to report process CPU stat: ", e)
            try:
                report["proc_mem_stats"] = get_proc_mem()
            except Exception as e:
                print("Unable to report process memory stat: ", e)
            try:
                self.report(report=report)
            except Exception as e:
                print("Unable to send process report: ", e)
            time.sleep(interval)


    def process_monitor(self, interval:int, pid:int = None):
        if (pid == None):
            pid = os.getpid()
        sub_thread = Thread(target=self.process_report, args=(interval, pid))
        sub_thread.start()