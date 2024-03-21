from abc import ABC
from pydantic import BaseModel
from typing import Dict, List, Optional
from datamodel_enum import *


class Metric(BaseModel):
    metric_name: ServiceMetricNameEnum | MlSpecificMetricNameEnum | str
    records: List[dict | float | int]
    unit: Optional[str]


class Condition(BaseModel):
    operator: OperatorEnum
    value: dict | float | int


class MetricConstraint(BaseModel):
    metrics: Metric
    condition: Condition
    aggregate_function: AggregateFunctionEnum


class BaseConstraint(BaseModel):
    name: str
    constraint_list: List[MetricConstraint]
