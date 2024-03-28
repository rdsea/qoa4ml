from typing import List

from qoa4ml.datamodels.common_models import Metric
from qoa4ml.datamodels.datamodel_enum import MetricNameEnum, ServiceMetricNameEnum
from qoa4ml.metric import PrometheusMetric


class TestMetricInherited(Metric):
    def say_something(self, something: str):
        print(something)


test = TestMetricInherited(
    metric_name=ServiceMetricNameEnum.response_time, records=[123, 123, 123]
)
