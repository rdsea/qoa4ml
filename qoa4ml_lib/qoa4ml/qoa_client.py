from typing import List
from .connector.amqp_connector import Amqp_Connector
from .connector.mqtt_connector import Mqtt_Connector
from .connector.prom_connector import Prom_Connector
from .probes import Gauge, Counter, Summary, Histogram
import json, uuid
import threading
from threading import Thread
import time, uuid, requests
from datetime import datetime
import os, sys, traceback
from .utils import get_proc_cpu, get_proc_mem
from .reports import QoA_Report

headers = {
    'Content-Type': 'application/json'
}

class Qoa_Client(object):
    # Init QoA Client
    def __init__(self, client_conf: dict, registration_url: str):
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
        self.qoa_report = QoA_Report()
        self.start_time = time.time()
        self.config = client_conf
        self.metrics = {}
        self.connector = {}
        self.timer_flag = False
        self.timer_start = 0
        self.method = client_conf["method"]
        self.stage_id = client_conf["stage_id"]
        self.instance_id  = os.environ.get('INSTANCE_ID')
        if not self.instance_id:
            print("INSTANCE_ID is not defined")
            self.instance_id  = str(uuid.uuid4())
        self.proc_monitor_flag = False
        # Init all connectors in for loop 
        self.registration_flag = False
        try:
            registration_data = self.registration(registration_url)
            json_data = registration_data.json()
            response = json_data["response"]
            
            if isinstance (response,dict):
                self.registration_flag = True
                connector_conf = response["connector"]

                for key in connector_conf:
                    self.connector[key] = self.init_connector(connector_conf[key])
            else: 
                print("Unable to register Qoa Client")
        except Exception as e:
            print("[ERROR] - Error {} when register QoA client: {}".format(type(e),e.__traceback__))
            traceback.print_exception(*sys.exc_info())
        

        # Set default connector for sending monitoring data if not specify
        self.default_connector = list(self.connector.keys())[0]
        # self.add_metric(metric_conf)
        self.lock = threading.Lock()

    def registration(self, url):
        return requests.request("POST", url, headers=headers, data=json.dumps(self.config))
        

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
            return Gauge(name, configuration["description"], configuration["default"],configuration["category"])
        elif configuration["class"] == "Counter":
            return Counter(name, configuration["description"], configuration["default"],configuration["category"])
        elif configuration["class"] == "Summary":
            return Summary(name, configuration["description"], configuration["default"],configuration["category"])
        elif configuration["class"] == "Histogram":
            return Histogram(name, configuration["description"], configuration["default"],configuration["category"])

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
            print("[ERROR] - Error {} in reset_metric: {}".format(type(e),e.__traceback__))
            traceback.print_exception(*sys.exc_info())

    def set_config(self, key, value):
        # TO DO:
        try:
            self.config[key] = value
        except Exception as e:
            print("[ERROR] - Error {} in set_config: {}".format(type(e),e.__traceback__))
            traceback.print_exception(*sys.exc_info())
    

    def set_metric(self, metric_name, value, quality=True, service_quality=False, data_quality=False, cl="Gauge", des="", def_val=-1):
        if metric_name not in self.metrics:
            metric_config = {}
            metric_config["class"] = cl
            metric_config["default"]= def_val
            metric_config["description"]= des
            metric_config["category"]= []
            if quality == True:
                metric_config["category"].append("quality")
                if service_quality == True:
                    metric_config["category"].append("service")
                elif data_quality == True:
                    metric_config["category"].append("data")
            self.add_metric({metric_name:metric_config})
        self.metrics[metric_name].set(value)
        metric = {}
        metric[self.stage_id] = {}
        metric[self.stage_id][metric_name] = {}
        metric[self.stage_id][metric_name][self.instance_id] = value
        self.qoa_report.observe_metric(metric=metric,quality=quality,service_quality=service_quality,data_quality=data_quality,infer_quality=False)

    def inference_report(self, value, confidence=None, accuracy=None,inference_id=None):
        report = {}
        if not inference_id:
            inference_id = str(uuid.uuid4())
        report[inference_id] = {}
        report[inference_id]["value"] = value
        if confidence:
            report[inference_id]["confidence"] = confidence
        if accuracy:
            report[inference_id]["accuracy"] = accuracy
        report[inference_id]["instance_id"] = self.instance_id
        self.qoa_report.observe_metric(report,quality=True,infer_quality=True)
        return inference_id

    def timer(self):
        if self.timer_flag == False:
            self.timer_flag = True
            self.timer_start = time.time()
            return {}
        else:
            self.timer_flag = False
            response_time = {"start_time":self.start_time, "response_time":time.time()-self.timer_start}
            self.set_metric("Response Time", response_time, quality=True,service_quality=True)
            return response_time

    def generate_report(self, metric:list=None,reset=True):
        # TO DO: Generate report for list of metric
        #  Inprogress
        meta_data = {}
        meta_data["instance_name"] = self.config["instance_name"]
        meta_data["instances_id"] = self.instance_id
        meta_data["method"] = self.config["method"]
        return self.qoa_report.generate_report(meta_data, reset=reset)

    def import_pReport(self, reports):
        self.qoa_report.import_pReport(reports)


    def get_report(self, submit=False,reset=True):
        report = self.generate_report(reset=reset)
        if submit:
            self.report(report=report)
        return report


    def asyn_report(self, metrics:list=None, report:dict = None, connectors:list=None):
        client_inf = {}
        client_inf["metadata"] = self.config.copy()
        client_inf["metadata"]['timestamp'] = time.time()
        client_inf["metadata"]['runtime'] = time.time() - self.start_time

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
        if self.registration_flag:
            sub_thread = Thread(target=self.asyn_report, args=(metrics, report, connectors))
            sub_thread.start()
        else:
            print("This QoA client has not been registered")


    def __str__(self):
        return str(self.config) + '\n' + str(self.connector)
    
    def process_report(self, interval:int, pid:int = None):
        report = {}
        while self.proc_monitor_flag:
            try:
                report["proc_cpu_stats"] = get_proc_cpu()
            except Exception as e:
                print("[ERROR] - Error {} in process cpu stat: {}".format(type(e),e.__traceback__))
                traceback.print_exception(*sys.exc_info())
            try:
                report["proc_mem_stats"] = get_proc_mem()
            except Exception as e:
                print("[ERROR] - Error {} in process memory stat: {}".format(type(e),e.__traceback__))
                traceback.print_exception(*sys.exc_info())
            try:
                self.report(report=report)
            except Exception as e:
                print("[ERROR] - Error {} in send process report: {}".format(type(e),e.__traceback__))
                traceback.print_exception(*sys.exc_info())
            time.sleep(interval)


    def process_monitor(self, interval:int, pid:int = None):
        if (pid == None):
            pid = os.getpid()
        sub_thread = Thread(target=self.process_report, args=(interval, pid))
        sub_thread.start()