from typing import List, Optional, Union

from pydantic import BaseModel

from .datamodel_enum import (
    AggregateFunctionEnum,
    DataQualityEnum,
    MlSpecificMetricNameEnum,
    OperatorEnum,
    ServiceMetricNameEnum,
)


class Metric(BaseModel):
    metric_name: Union[ServiceMetricNameEnum, MlSpecificMetricNameEnum, DataQualityEnum]
    records: List[Union[dict, float, int]] = []
    unit: Optional[str] = None


class Condition(BaseModel):
    operator: OperatorEnum
    value: Union[dict, float, int]


class MetricConstraint(BaseModel):
    metrics: Metric
    condition: Condition
    aggregate_function: AggregateFunctionEnum


class BaseConstraint(BaseModel):
    name: str
    constraint_list: List[MetricConstraint]
