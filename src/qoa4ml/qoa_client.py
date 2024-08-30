import copy
import os
import sys
import threading
import time
import traceback
import uuid
from threading import Thread
from typing import Any, Generic, Optional, TypeVar, Union

import requests
from pydantic import create_model

# from .connector.mqtt_connector import Mqtt_Connector
from .config.configs import (
    AMQPConnectorConfig,
    ClientConfig,
    ClientInfo,
    ConnectorConfig,
    DebugConnectorConfig,
    DockerProbeConfig,
    ProbeConfig,
    ProcessProbeConfig,
    SystemProbeConfig,
)
from .connector.amqp_connector import AmqpConnector
from .connector.base_connector import BaseConnector
from .connector.debug_connector import DebugConnector
from .lang.common_models import Metric
from .lang.datamodel_enum import (
    MetricNameEnum,
    ReportTypeEnum,
    ServiceAPIEnum,
    ServiceMetricNameEnum,
)
from .probes.docker_monitoring_probe import DockerMonitoringProbe
from .probes.probe import Probe
from .probes.process_monitoring_probe import ProcessMonitoringProbe
from .probes.system_monitoring_probe import SystemMonitoringProbe
from .reports.abstract_report import AbstractReport
from .reports.ml_reports import MLReport
from .utils.logger import qoa_logger
from .utils.qoa_utils import (
    load_config,
    set_logger_level,
)

headers = {"Content-Type": "application/json"}


# NOTE: T must be a subtype of AbstractReport
T = TypeVar("T", bound=AbstractReport)


class QoaClient(Generic[T]):
    def __init__(
        self,
        # NOTE: use text, number, enum
        report_cls: type[T] = MLReport,
        config_dict: Optional[dict] = None,
        config_path: Optional[str] = None,
        registration_url: Optional[str] = None,
        logging_level=2,
    ):
        set_logger_level(logging_level)

        if config_dict is not None:
            self.configuration = ClientConfig.model_validate(config_dict)

        if config_path is not None:
            self.configuration = ClientConfig.model_validate(load_config(config_path))

        self.client_config = self.configuration.client
        self.connector_list: dict[str, BaseConnector] = {}
        self.timer_flag = False
        self.functionality = self.client_config.functionality
        self.stage_id = self.client_config.stage_id
        self.process_monitor_flag = 0
        self.inference_flag = False

        self.instance_id = os.environ.get("INSTANCE_ID")
        if self.instance_id:
            qoa_logger.info("Setting instance_id with INSTANCE_ID")
            self.instance_id = uuid.UUID(self.instance_id)
        elif self.configuration.client.instance_id:
            qoa_logger.info("Setting instance_id with client.instance_id")
            self.instance_id = uuid.UUID(self.configuration.client.instance_id)
        else:
            self.instance_id = str(uuid.uuid4())

        self.client_config.instance_id = str(self.instance_id)
        self.client_config.id = str(uuid.uuid4())
        self.qoa_report = report_cls(self.client_config)
        if self.configuration.connector:
            # init connectors offline if it's specified
            connector_conf = self.configuration.connector
            try:
                for connector in connector_conf:
                    self.connector_list[connector.name] = self.init_connector(connector)
            except Exception as e:
                qoa_logger.exception(
                    f"Error {type(e)} when configuring connector in QoaClient"
                )
        elif registration_url or self.configuration.registration_url:
            # init connectors using configuration received from monitoring service, if it's specified
            try:
                if registration_url:
                    registration_data = self.registration(registration_url)
                else:
                    # NOTE: logically true
                    registration_data = self.registration(
                        self.configuration.registration_url
                    )
                json_data = registration_data.json()
                response = json_data["response"]
                if isinstance(response, dict):
                    connector_configs = response["connector"]
                    if isinstance(connector_configs, dict):
                        connector_config = ConnectorConfig(**connector_configs)
                        self.connector_list[connector_config.name] = (
                            self.init_connector(connector_config)
                        )
                    elif isinstance(connector_configs, list):
                        for config in connector_configs:
                            connector_config = ConnectorConfig(**config)
                            self.connector_list[connector_config.name] = (
                                self.init_connector(connector_config)
                            )
                else:
                    qoa_logger.warning(
                        "Unable to register Qoa Client: connector configuration must be dictionary"
                    )
            except Exception as e:
                qoa_logger.exception(f"Error {type(e)} when registering QoA client")
                traceback.print_exception(*sys.exc_info())

        if not self.connector_list:
            qoa_logger.warning("No connector initiated")
            self.default_connector = None
        else:
            # Set default connector for sending monitoring data if not specify
            self.default_connector = next(iter(self.connector_list.keys()))

        self.probes_list = None
        if self.configuration.probes:
            self.probes_list = self.init_probes(
                self.configuration.probes, self.configuration.client
            )
        # lock report to guarantee consistency
        self.lock = threading.Lock()

    def registration(self, url: str):
        # get connector configuration by registering with the monitoring service

        return requests.request(
            "POST", url, headers=headers, data=self.client_config.json()
        )

    def init_probes(
        self, probe_config_list: list[ProbeConfig], client_info: ClientInfo
    ):
        probes_list: list[Probe] = []
        # TODO: each probe can have their own connector
        if self.default_connector:
            selected_connector = self.connector_list[self.default_connector]
        else:
            qoa_logger.warning("No default connector, using debug connector")
            selected_connector = DebugConnector()

        for probe_config in probe_config_list:
            # TODO: can be simplify for less duplicate code
            if isinstance(probe_config, DockerProbeConfig):
                probes_list.append(
                    DockerMonitoringProbe(probe_config, selected_connector, client_info)
                )
            elif isinstance(probe_config, ProcessProbeConfig):
                probes_list.append(
                    ProcessMonitoringProbe(
                        probe_config, selected_connector, client_info
                    )
                )
            elif isinstance(probe_config, SystemProbeConfig):
                probes_list.append(
                    SystemMonitoringProbe(probe_config, selected_connector, client_info)
                )
            else:
                raise ValueError(
                    f"Probe config type {type(probe_config)} is not supported yet"
                )
        return probes_list

    def init_connector(self, configuration: ConnectorConfig) -> BaseConnector:
        # init connector from configuration
        if configuration.connector_class == ServiceAPIEnum.amqp and isinstance(
            configuration.config, AMQPConnectorConfig
        ):
            return AmqpConnector(configuration.config)
        elif configuration.connector_class == ServiceAPIEnum.debug and isinstance(
            configuration.config, DebugConnectorConfig
        ):
            return DebugConnector(configuration.config)

        # TODO: MQTT is both connector and collector
        #
        # if (
        #    configuration.connector_class == ServiceAPIEnum.mqtt
        #    and type(configuration.config) is MQTTConnectorConfig
        # ):
        #    return Mqtt_Connector(configuration.config)
        raise RuntimeError("Connector config is not of correct type")

    def get_client_config(self):
        # TODO: what to do exactly?
        return self.client_config

    def set_config(self, key, value):
        try:
            self.client_config.__setattr__(key, value)
        except Exception as e:
            qoa_logger.exception(f"Error {type(e)} when setConfig in QoA client")

    def observe_metric(
        self,
        metric_name: MetricNameEnum,
        value,
        category: int = 0,
        description: str = "",
    ):
        if category == 0:
            report_type = ReportTypeEnum.service
        elif category == 1:
            report_type = ReportTypeEnum.data
        elif category == 2:
            report_type = ReportTypeEnum.security
        else:
            raise RuntimeError("Report type not supported")

        self.qoa_report.observe_metric(
            report_type,
            self.stage_id,
            Metric(metric_name=metric_name, records=[value], description=description),
        )

    def timer(self):
        if self.timer_flag is False:
            self.timer_flag = True
            self.timerStart = time.time()
            return {}
        else:
            self.timer_flag = False
            response_time = {
                "startTime": self.timerStart,
                "responseTime": time.time() - self.timerStart,
            }
            self.observe_metric(
                ServiceMetricNameEnum.response_time, response_time, category=0
            )
            return response_time

    def import_previous_report(self, reports: Union[dict, list[dict]]):
        if isinstance(reports, list):
            for report in reports:
                self.qoa_report.process_previous_report(report)
        else:
            self.qoa_report.process_previous_report(reports)

    def __str__(self):
        return self.client_config.model_dump_json() + "\n" + str(self.connector_list)

    def asyn_report(self, body_mess: str, connectors: Optional[list] = None):
        self.lock.acquire()
        if connectors is None:
            # if connectors are not specify, use default
            if self.default_connector:
                chosen_connector = self.connector_list[self.default_connector]
                if isinstance(chosen_connector, AmqpConnector):
                    chosen_connector.send_report(body_mess, corr_id=str(uuid.uuid4()))
                else:
                    chosen_connector.send_report(body_mess)
            else:
                qoa_logger.error(
                    "No default connector, please specify the connector to use"
                )
        else:
            # iterate connector to send report
            # for connector in connectors:
            # print(connector)
            # Todo: send by multiple connector
            pass

        self.lock.release()

    def report(
        self,
        report: Optional[dict] = None,
        connectors: Optional[list] = None,
        submit=False,
        reset=True,
        corr_id=None,
    ):
        """
        submit=True to submit the report through the default connector
        """
        if report is None:
            return_report = self.qoa_report.generate_report(reset, corr_id=corr_id)
        else:
            user_defined_report_model = create_model(
                "UserDefinedReportModel",
                metadata=(dict, ...),
                timestamp=(float, ...),
                report=(dict, ...),
            )
            return_report = user_defined_report_model(
                report=report,
                metadata=copy.deepcopy(self.client_config.__dict__),
                timestamp=time.time(),
            )

        if submit:
            if self.default_connector is not None:
                sub_thread = Thread(
                    target=self.asyn_report,
                    args=(return_report.model_dump_json(), connectors),
                )
                sub_thread.start()
            else:
                qoa_logger.warning("No connector available")
        return return_report.model_dump(mode="json")

    def start_all_probes(self):
        """
        Start all probes in the background, will be killed when the main process exited
        NOTE: if the probe takes long to report, and the main process exit, no report may be sent
        """
        if not self.probes_list:
            raise RuntimeError(
                "There is no initiated probes, please recheck the config"
            )
        for probe in self.probes_list:
            probe.start_reporting()

    def stop_all_probes(self):
        if not self.probes_list:
            raise RuntimeError(
                "There is no initiated probes, please recheck the config"
            )
        for probe in self.probes_list:
            probe.stop_reporting()

    def observe_inference(
        self,
        inference_value,
    ):
        self.qoa_report.observe_inference(inference_value)

    def observe_inference_metric(
        self,
        metric_name: MetricNameEnum,
        value: Any,
    ):
        metric = Metric(metric_name=metric_name, records=[value])
        self.qoa_report.observe_inference_metric(metric)
