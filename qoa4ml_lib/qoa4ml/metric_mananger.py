from typing import Dict, List, Optional, Union

from qoa4ml.datamodels.datamodel_enum import MetricClassEnum, MetricNameEnum

from .datamodels.configs import MetricConfig
from .metric import Counter, Gauge, Histogram, PrometheusMetric, Summary
from .probes.mlquality import *
from .qoaUtils import qoaLogger


class MetricManager:
    def __init__(self) -> None:
        self.metricList: Dict[MetricNameEnum, PrometheusMetric] = {}

    def add_metric(self, metric_configs: List[MetricConfig]):
        # Add multiple metrics
        for metric_config in metric_configs:
            self.metricList[metric_config.name] = self.init_metric(metric_config)

    def reset_metric(self, key: Optional[Union[List, str]] = None):
        # TO DO:
        try:
            if key == None:
                for metric_name in self.metricList:
                    self.metricList[metric_name].reset()
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

    def get_metric(self, key: Optional[Union[List, str]] = None):
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

    def init_metric(self, configuration: MetricConfig) -> PrometheusMetric:
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
        else:
            raise ValueError(
                f"Metric class {configuration.metric_class} is not supported"
            )

    def observe_metric(
        self,
        metric_name: MetricNameEnum,
        value,
        category=0,
        metric_class: MetricClassEnum = MetricClassEnum.gauge,
        description: str = "",
        default_value: int = -1,
    ):
        if metric_name not in self.metricList:
            metric_config = MetricConfig(
                name=metric_name,
                category=category,
                metric_class=metric_class,
                description=description,
                default_value=default_value,
            )
            self.metricList[metric_name] = self.init_metric(metric_config)
        self.metricList[metric_name].set(value)
