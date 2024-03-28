import copy
import json
import os
import sys
import threading
import time
import traceback
import uuid
from threading import Thread
from typing import List, Optional, Union

import requests
from qoa4ml.datamodels.datamodel_enum import MetricClassEnum, ServiceAPIEnum

from .connector.amqp_connector import Amqp_Connector

# from .connector.mqtt_connector import Mqtt_Connector
from .datamodels.configs import (
    AMQPCollectorConfig,
    AMQPConnectorConfig,
    ClientConfig,
    ConnectorConfig,
    GroupMetricConfig,
    MetricConfig,
    MQTTConnectorConfig,
)
from .metric import Counter, Gauge, Histogram, Metric, Summary
from .probes.dataquality import (
    eva_duplicate,
    eva_erronous,
    eva_missing,
    eva_none,
    image_quality,
)
from .probes.mlquality import *
from .qoaUtils import (
    get_proc_cpu,
    get_proc_mem,
    load_config,
    qoaLogger,
    set_logger_level,
)
from .reports import QoaReport

headers = {"Content-Type": "application/json"}


class QoaClient(object):
    # Init QoA Client
    def __init__(
        self,
        config_dict: Optional[ClientConfig] = None,
        config_path: Optional[str] = None,
        registration_url: Optional[str] = None,
        logging_level=2,
    ):
        set_logger_level(logging_level)

        if config_dict != None:
            self.configuration = config_dict

        if config_path != None:
            self.configuration = ClientConfig(**load_config(config_path))

        self.clientConf = self.configuration.client

        self.metricList = {}
        self.connectorList = {}
        self.timerFlag = False
        self.method = self.clientConf.method
        self.stageID = self.clientConf.stage
        self.procMonitorFlag = 0
        self.inferenceFlag = False

        self.instanceID = os.environ.get("INSTANCE_ID")
        if not self.instanceID:
            print("INSTANCE_ID is not defined")
            self.instanceID = str(uuid.uuid4())

        self.clientConf.instances_id = self.instanceID
        self.qoaReport = QoaReport(self.clientConf)

        if self.configuration.connector:
            # init connectors offline if it's specified
            connector_conf = self.configuration.connector
            try:
                for connector in connector_conf:
                    self.connectorList[connector.name] = self.initConnector(connector)
            except Exception as e:
                qoaLogger.error(
                    str(
                        "[ERROR] - Error {} when configuring connector in QoaClient: {}".format(
                            type(e), e.__traceback__
                        )
                    )
                )
        elif registration_url or self.configuration.registration_url:
            # init connectors using configuration received from monitoring service, if it's specified
            try:
                registration_url = (
                    self.configuration.registration_url
                    if self.configuration.registration_url
                    else registration_url
                )
                registration_data = self.registration(registration_url)
                json_data = registration_data.json()
                response = json_data["response"]
                if isinstance(response, dict):
                    connector_configs = response["connector"]
                    for connector in connector_configs:
                        connector_config = ConnectorConfig(**connector)
                        self.connectorList[connector_config.name] = self.initConnector(
                            connector_config
                        )
                else:
                    qoaLogger.warning(
                        "Unable to register Qoa Client: connector configuration must be dictionary"
                    )
            except Exception as e:
                qoaLogger.error(
                    str(
                        "[ERROR] - Error {} when registering QoA client: {}".format(
                            type(e), e.__traceback__
                        )
                    )
                )
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
        return requests.request(
            "POST", url, headers=headers, data=json.dumps(self.clientConf)
        )

    def initConnector(self, configuration: ConnectorConfig):
        # init connector from configuration
        if (
            configuration.connector_class == ServiceAPIEnum.amqp
            and type(configuration.config) is AMQPConnectorConfig
        ):
            return Amqp_Connector(configuration.config)

        # TODO: MQTT is both connector and collector
        #
        # if (
        #    configuration.connector_class == ServiceAPIEnum.mqtt
        #    and type(configuration.config) is MQTTConnectorConfig
        # ):
        #    return Mqtt_Connector(configuration.config)
        raise RuntimeError("Connector config is not of correct type")

    def addMetric(self, metric_configs: List[MetricConfig]):
        # Add multiple metrics
        for metric_config in metric_configs:
            self.metricList[metric_config.name] = self.initMetric(metric_config)

    def initMetric(self, configuration: MetricConfig):
        # init individual metrics
        if configuration.metric_class == MetricClassEnum.gauge:
            return Gauge(
                configuration.name,
                configuration.description,
                configuration.default_value,
                configuration.category,
            )
        elif configuration.metric_class == MetricClassEnum.counter:
            return Counter(
                configuration.name,
                configuration.description,
                configuration.default_value,
                configuration.category,
            )
        elif configuration.metric_class == MetricClassEnum.summary:
            return Summary(
                configuration.name,
                configuration.description,
                configuration.default_value,
                configuration.category,
            )
        elif configuration.metric_class == MetricClassEnum.histogram:
            return Histogram(
                configuration.name,
                configuration.description,
                configuration.default_value,
                configuration.category,
            )

    def getClientConfig(self):
        # TODO: what to do exactly?
        return self.clientConf

    def getMetric(self, key: Optional[Union[List, str]] = None):
        # TO DO:
        try:
            if key == None:
                # Get all metric
                return self.metricList
            elif isinstance(key, List):
                # Get a list of metrics
                return dict((k, self.metricList[k]) for k in key)
            else:
                # Get a specific metric
                return self.metricList[key]
        except Exception as e:
            qoaLogger.error(
                str(
                    "[ERROR] - Error {} when getting metric from QoA client: {}".format(
                        type(e), e.__traceback__
                    )
                )
            )

    def resetMetric(self, key: Optional[Union[List, str]] = None):
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
            qoaLogger.error(
                str(
                    "[ERROR] - Error {} when reseting metric in QoA client: {}".format(
                        type(e), e.__traceback__
                    )
                )
            )

    def setConfig(self, key, value):
        # TO DO:
        try:
            self.clientConf.__setattr__(key, value)
        except Exception as e:
            qoaLogger.error(
                str(
                    "[ERROR] - Error {} when setConfig in QoA client: {}".format(
                        type(e), e.__traceback__
                    )
                )
            )

    def observeMetric(
        self,
        metric_name,
        value,
        category=0,
        metric_class="Gauge",
        description: str = "",
        default_value: int = -1,
    ):
        if metric_name not in self.metricList:
            metric_config = {}
            metric_config["class"] = cl
            metric_config["default"] = def_val
            metric_config["description"] = des
            metric_config["category"] = category
            self.addMetric({metric_name: metric_config})
        self.metricList[metric_name].set(value)

        self.qoaReport.observeMetric(metric=self.metricList[metric_name])

    def timer(self):
        if self.timerFlag == False:
            self.timerFlag = True
            self.timerStart = time.time()
            return {}
        else:
            self.timerFlag = False
            responseTime = {
                "startTime": self.timerStart,
                "responseTime": time.time() - self.timerStart,
            }
            self.observeMetric("responseTime", responseTime, category=0)
            return responseTime

    def importPReport(self, reports):
        self.qoaReport.importPReport(reports)

    def __str__(self):
        return str(self.clientConf) + "\n" + str(self.connectorList)

    def process_report(self, interval: int, pid: Optional[int] = None):
        report = {}
        while self.procMonitorFlag == 1:
            try:
                report["proc_cpu_stats"] = get_proc_cpu()
            except Exception as e:
                qoaLogger.error(
                    "Error {} in process cpu stat: {}".format(type(e), e.__traceback__)
                )
                traceback.print_exception(*sys.exc_info())
            try:
                report["proc_mem_stats"] = get_proc_mem()
            except Exception as e:
                qoaLogger.error(
                    "Error {} in process memory stat: {}".format(
                        type(e), e.__traceback__
                    )
                )
                traceback.print_exception(*sys.exc_info())
            try:
                self.report(report=report, submit=True)
            except Exception as e:
                qoaLogger.error(
                    "Error {} in send process report: {}".format(
                        type(e), e.__traceback__
                    )
                )
                traceback.print_exception(*sys.exc_info())
            time.sleep(interval)

    def process_monitor_start(self, interval: int, pid: Optional[int] = None):
        if self.procMonitorFlag == 0:
            if pid == None:
                pid = os.getpid()
            self.procMonitorFlag = 1
            sub_thread = Thread(target=self.process_report, args=(interval, pid))
            sub_thread.start()
        self.procMonitorFlag = 1

    def process_monitor_stop(self):
        self.procMonitorFlag = 2

    def asyn_report(self, report: dict, connectors: Optional[list] = None):
        body_mess = json.dumps(report)
        self.lock.acquire()
        if connectors == None:
            # if connectors are not specify, use default
            self.connectorList[self.default_connector].send_data(
                body_mess, str(uuid.uuid4())
            )
        else:
            # iterate connector to send report
            for connector in connectors:
                print(connector)
        self.lock.release()

    def report(
        self,
        metrics: Optional[list] = None,
        report: Optional[dict] = None,
        connectors: Optional[list] = None,
        submit=False,
        reset=True,
    ):
        if report == None:
            report = self.qoaReport.generateReport(metrics, reset)
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

    def observeInferenceMetric(
        self, metric_name, value, new_inf=False, inference_id=None, dependency=None
    ):
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

        self.qoaReport.observeInferenceMetric(report, dependency=dependency)
        return infID

    def observeErronous(self, data, errors=None):
        results = eva_erronous(data, errors=errors)
        if results != None:
            for key in results:
                self.observeMetric(key, results[key], 1)

    def observeDuplicate(self, data):
        results = eva_duplicate(data)
        if results != None:
            for key in results:
                self.observeMetric(key, results[key], 1)

    def observeMissing(
        self, data, null_count=True, correlations=False, predict=False, random_state=0
    ):
        results = eva_missing(
            data,
            null_count=null_count,
            correlations=correlations,
            predict=predict,
            random_state=random_state,
        )
        if results != None:
            for key in results:
                self.observeMetric(key, results[key], 1)

    def observeImgQuality(self, image):
        results = image_quality(image)
        if results != None:
            for key in results:
                self.observeMetric(key, results[key], 1)

    def observeNone(self, data):
        results = eva_none(data)
        if results != None:
            for key in results:
                self.observeMetric(key, results[key], 1)
