from qoa4ml.datamodels.configs import (
    GroupMetricConfig,
    MetricConfig,
)
from qoa4ml.datamodels.datamodel_enum import (
    MetricCategoryEnum,
    MetricClassEnum,
    MlSpecificMetricNameEnum,
    ServiceMetricNameEnum,
    ResourcesUtilizationMetricNameEnum,
)

accuracy_metric = MetricConfig(
    name=MlSpecificMetricNameEnum.acccuracy,
    metric_class=MetricClassEnum.gauge,
    description="model training accuracy",
    default_value=0,
    category=[MetricCategoryEnum.quality, MetricCategoryEnum.inference],
)
accuracy_metric = MetricConfig(
    name=ServiceMetricNameEnum.response_time,
    metric_class=MetricClassEnum.gauge,
    description="model training response time",
    default_value=0,
    category=[MetricCategoryEnum.quality, MetricCategoryEnum.service],
)

cpu_stat = GroupMetricConfig(
    name="cpu_stat",
    metric_configs=[
        MetricConfig(
            name=ResourcesUtilizationMetricNameEnum.cpu,
            metric_class=MetricClassEnum.gauge,
            description="monitor system cpu percentage",
            default_value=-1,
            key="used",
        )
    ],
)
proc_cpu = GroupMetricConfig(
    name="proc_cpu",
    metric_configs=[
        MetricConfig(
            name=ResourcesUtilizationMetricNameEnum.cpu,
            metric_class=MetricClassEnum.gauge,
            description="monitor process CPU precentage",
            default_value=0,
            key="used",
        )
    ],
)
mem_stat = GroupMetricConfig(
    name="mem_stat",
    metric_configs=[
        MetricConfig(
            name=ResourcesUtilizationMetricNameEnum.memory,
            metric_class=MetricClassEnum.gauge,
            description="monitor system memory used",
            default_value=0,
            key="used",
        )
    ],
)
proc_mem = GroupMetricConfig(
    name="proc_mem",
    metric_configs=[
        MetricConfig(
            name=ResourcesUtilizationMetricNameEnum.memory,
            metric_class=MetricClassEnum.gauge,
            description="monitor process memory precentage",
            default_value=0,
            key="used",
        )
    ],
)
