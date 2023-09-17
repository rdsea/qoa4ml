from .connector.amqp_connector import Amqp_Connector
from .connector.mqtt_connector import Mqtt_Connector
from .probes.dataquality import eva_duplicate, eva_erronous, eva_missing, eva_none, image_quality
from .probes.mlquality import *
from .metric import Gauge, Counter, Summary, Histogram
import json, uuid
import threading
from threading import Thread
import time, uuid, requests
import os, sys, traceback, copy
from .qoaUtils import get_proc_cpu, get_proc_mem, load_config, qoaLogger, set_logger_level
from .reports import QoaReport


headers = {
    'Content-Type': 'application/json'
}

class QoaClient(object):
    # Init QoA Client
    def __init__(self, config_dict:dict=None, config_path: str=None, registration_url: str=None, logging_level=2, config_format = 0):
        """
        The 'config_dict' contains the information about the client and its configuration in form of dictionary
        Example: 
        { 
            "client":{
                "client_id": "aaltosea4",
                "instance_name": "ML02",
                "stage_id": "ML",
                "method": "REST",
                "application": "test",
                "role": "ml"
            },
            "connector":{
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
        }
        The 'connector' is the dictionary containing multiple connector configuration (amqp, mqtt, kafka)
        If 'connector' is not define, developer must give 'registration_url'
        The 'registration_url' specify the service where the client register for monitoring service. If it's set, the client register with the service and receive connector configuration
        Example: "http://127.0.0.1:5001/registration"
        """
        set_logger_level(logging_level)
        
        if config_dict != None:
            self.configuration = config_dict

        if config_path != None:
            self.configuration = load_config(config_path, config_format)

        self.clientConf = self.configuration["client"]
        
        self.metricList = {}
        self.connectorList = {}
        self.timerFlag = False
        self.method = self.clientConf["method"]
        self.stageID = self.clientConf["stage_id"]
        self.procMonitorFlag = 0
        self.inferenceFlag = False

        self.instanceID  = os.environ.get('INSTANCE_ID')
        if not self.instanceID:
            print("INSTANCE_ID is not defined")
            self.instanceID  = str(uuid.uuid4())

        self.clientConf["instances_id"] = self.instanceID
        self.qoaReport = QoaReport(self.clientConf)

        if "connector" in self.configuration:
            # init connectors offline if it's specified
            connector_conf = self.configuration["connector"]
            try:
                for key in connector_conf:
                    self.connectorList[key] = self.initConnector(connector_conf[key])
            except Exception as e:
                qoaLogger.error(str("[ERROR] - Error {} when configuring connector in QoaClient: {}".format(type(e),e.__traceback__)))
        elif (registration_url != None) or ("registration_url" in self.configuration):
            # init connectors using configuration received from monitoring service, if it's specified
            try:
                if registration_url == None:
                    registration_url = self.configuration["registration_url"]
                registration_data = self.registration(registration_url)
                json_data = registration_data.json()
                response = json_data["response"]
                if isinstance (response,dict):
                    connector_conf = response["connector"]
                    for key in connector_conf:
                        self.connectorList[key] = self.initConnector(connector_conf[key])
                else: 
                    qoaLogger.warning("Unable to register Qoa Client: connector configuration must be dictionary")
            except Exception as e:
                qoaLogger.error(str("[ERROR] - Error {} when registering QoA client: {}".format(type(e),e.__traceback__)))
                traceback.print_exception(*sys.exc_info())
  
        if not any(self.connectorList):
            qoaLogger.warning("No connector initiated")
            self.default_connector = None
        else:
            # Set default connector for sending monitoring data if not specify
            self.default_connector = list(self.connectorList.keys())[0]
        
        # lock report to guarantee consistency
        self.lock = threading.Lock()


    def registration(self, url):
        # get connector configuration by registering with the monitoring service
        return requests.request("POST", url, headers=headers, data=json.dumps(self.clientConf))
        

    def initConnector(self, configuration: dict):
        # init connector from configuration
        if configuration["class"] == "amqp":
            return Amqp_Connector(configuration["conf"])
        if configuration["class"] == "mqtt":
            return Mqtt_Connector(configuration["conf"])

    def addMetric(self, metric_conf: dict):
        # Add multiple metrics 
        for key in metric_conf:
            self.metricList[key] = self.initMetric(key, metric_conf[key])

    def initMetric(self, name, configuration: dict):
        # init individual metrics
        if configuration["class"] == "Gauge":
            return Gauge(name, configuration["description"], configuration["default"],configuration["category"])
        elif configuration["class"] == "Counter":
            return Counter(name, configuration["description"], configuration["default"],configuration["category"])
        elif configuration["class"] == "Summary":
            return Summary(name, configuration["description"], configuration["default"],configuration["category"])
        elif configuration["class"] == "Histogram":
            return Histogram(name, configuration["description"], configuration["default"],configuration["category"])

    def getClientConfig(self):
        # TO DO:
        return self.clientConf


    def getMetric(self, key=None):
        # TO DO:
        try:
            if key == None:
                # Get all metric
                return self.metricList
            elif isinstance(key, list):
                # Get a list of metrics
                return dict((k, self.metricList[k]) for k in key)
            else: 
                # Get a specific metric
                return self.metricList[key]
        except Exception as e:
            qoaLogger.error(str("[ERROR] - Error {} when getting metric from QoA client: {}".format(type(e),e.__traceback__)))
    
    def resetMetric(self, key=None):
        # TO DO:
        try:
            if key == None:
                for key in self.metricList:
                    self.metricList[key].reset()
            elif isinstance(key, list):
                for k in key:
                    self.metricList[k].reset()
            else: 
                return self.metricList[key].reset()
        except Exception as e:
            qoaLogger.error(str("[ERROR] - Error {} when reseting metric in QoA client: {}".format(type(e),e.__traceback__)))
            
    def setConfig(self, key, value):
        # TO DO:
        try:
            self.clientConf[key] = value
        except Exception as e:
            qoaLogger.error(str("[ERROR] - Error {} when setConfig in QoA client: {}".format(type(e),e.__traceback__)))


    def observeMetric(self, metric_name, value, category=0, cl="Gauge", des="", def_val=-1):
        if metric_name not in self.metricList:
            metric_config = {}
            metric_config["class"] = cl
            metric_config["default"]= def_val
            metric_config["description"]= des
            metric_config["category"]= category
            self.addMetric({metric_name:metric_config})
        self.metricList[metric_name].set(value)
        
        self.qoaReport.observeMetric(metric=self.metricList[metric_name])


    def timer(self):
        if self.timerFlag == False:
            self.timerFlag = True
            self.timerStart = time.time()
            return {}
        else:
            self.timerFlag = False
            responseTime = {"startTime":self.timerStart, "responseTime":time.time()-self.timerStart}
            self.observeMetric("responseTime", responseTime, category=0)
            return responseTime


    def importPReport(self, reports):
        self.qoaReport.importPReport(reports)

    def __str__(self):
        return str(self.clientConf) + '\n' + str(self.connectorList)


    def process_report(self, interval:int, pid:int = None):
        report = {}
        while self.procMonitorFlag == 1:
            try:
                report["proc_cpu_stats"] = get_proc_cpu()
            except Exception as e:
                qoaLogger.error("Error {} in process cpu stat: {}".format(type(e),e.__traceback__))
                traceback.print_exception(*sys.exc_info())
            try:
                report["proc_mem_stats"] = get_proc_mem()
            except Exception as e:
                qoaLogger.error("Error {} in process memory stat: {}".format(type(e),e.__traceback__))
                traceback.print_exception(*sys.exc_info())
            try:
                self.report(report=report,submit=True)
            except Exception as e:
                qoaLogger.error("Error {} in send process report: {}".format(type(e),e.__traceback__))
                traceback.print_exception(*sys.exc_info())
            time.sleep(interval)


    def process_monitor_start(self, interval:int, pid:int = None):
        if self.procMonitorFlag == 0:
            if (pid == None):
                pid = os.getpid()
            self.procMonitorFlag = 1
            sub_thread = Thread(target=self.process_report, args=(interval, pid))
            sub_thread.start()
        self.procMonitorFlag = 1
        

    def process_monitor_stop(self):
        self.procMonitorFlag = 2
    
    def asyn_report(self, report:dict, connectors:list=None):
        body_mess = json.dumps(report)
        self.lock.acquire()
        if connectors == None:
            # if connectors are not specify, use default
            self.connectorList[self.default_connector].send_data(body_mess,str(uuid.uuid4()))
        else:
            # iterate connector to send report
            for connector in connectors:
                print(connector)
        self.lock.release()

    def report(self, metrics:list=None, report: dict = None, connectors:list=None, submit=False,reset=True):
        if (report == None):
            report = self.qoaReport.generateReport(metrics, reset=reset)
        else:
            report["metadata"] = copy.deepcopy(self.clientConf)
            report["metadata"]["timestamp"] = time.time()

        if submit:
            if self.default_connector != None:
                sub_thread = Thread(target=self.asyn_report, args=(report, connectors))
                sub_thread.start()
            else:
                qoaLogger.warning("No connector available")
        return report

    def observeInferenceMetric(self, metric_name, value, new_inf=False, inference_id=None, dependency=None):
        report = {}
        
        if new_inf:
            infID = str(uuid.uuid4())
        else:
            if inference_id != None:
                infID = inference_id
            else:
                if self.inferenceFlag == False:
                    self.infID = str(uuid.uuid4())
                    self.inferenceFlag = True
                infID = self.infID
        report[infID] = {}
        report[infID]["instance_id"] = self.instanceID

        report[infID][metric_name] = {}
        report[infID][metric_name]["value"] = value
        
        self.qoaReport.observeInferenceMetric(report,dependency=dependency)
        return infID
    
    def observeErronous(self, data, errors=None):
        results = eva_erronous(data, errors=errors)
        if results != None:
            for key in results:
                self.observeMetric(key,results[key],1)

    def observeDuplicate(self, data):
        results = eva_duplicate(data)
        if results != None:
            for key in results:
                self.observeMetric(key,results[key],1)
    
    def observeMissing(self, data, null_count=True, correlations=False, predict=False, random_state=0):
        results = eva_missing(data, null_count=null_count, correlations=correlations, predict=predict, random_state=random_state)
        if results != None:
            for key in results:
                self.observeMetric(key,results[key],1)
    
    def observeImgQuality(self, image):
        results = image_quality(image)
        if results != None:
            for key in results:
                self.observeMetric(key,results[key],1)

    def observeNone(self, data):
        results = eva_none(data)
        if results != None:
            for key in results:
                self.observeMetric(key,results[key],1)


        # self.qoaReport = QoA_Report()
        # self.start_time = time.time()
        # self.clientConf = client_conf
        # self.metricList = {}
        # self.connectorList = {}
        # self.timerFlag = False
        self.timer_start = 0
        # self.method = client_conf["method"]
        # self.stageID = client_conf["stage_id"]
        # self.instanceID  = os.environ.get('INSTANCE_ID')
        # if not self.instanceID:
        #     print("INSTANCE_ID is not defined")
        #     self.instanceID  = str(uuid.uuid4())
        # self.procMonitorFlag = False
        # Init all connectors in for loop 
        # self.registration_flag = False
        # try:
        #     registration_data = self.registration(registration_url)
        #     json_data = registration_data.json()
        #     response = json_data["response"]
            
        #     if isinstance (response,dict):
        #         self.registration_flag = True
        #         connector_conf = response["connector"]

        #         for key in connector_conf:
        #             self.connectorList[key] = self.initConnector(connector_conf[key])
        #     else: 
        #         print("Unable to register Qoa Client")
        # except Exception as e:
        #     qoaLogger.error("Error {} when register QoA client: {}".format(type(e),e.__traceback__))
        #     traceback.print_exception(*sys.exc_info())
        

        # Set default connector for sending monitoring data if not specify
        # self.default_connector = list(self.connectorList.keys())[0]
        # self.addMetric(metric_conf)
        # self.lock = threading.Lock()


    








    
