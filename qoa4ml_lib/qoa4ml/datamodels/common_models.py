from typing import List, Optional, Union
from pydantic import BaseModel
import datamodel_enum


class Metric(BaseModel):
    metric_name: Union[
        datamodel_enum.ServiceMetricNameEnum, datamodel_enum.MlSpecificMetricNameEnum
    ]
    records: List[Union[dict, float, int]] = []
    unit: Optional[str] = None


class Condition(BaseModel):
    operator: datamodel_enum.OperatorEnum
    value: Union[dict, float, int]


class MetricConstraint(BaseModel):
    metrics: Metric
    condition: Condition
    aggregate_function: datamodel_enum.AggregateFunctionEnum


class BaseConstraint(BaseModel):
    name: str
    constraint_list: List[MetricConstraint]
