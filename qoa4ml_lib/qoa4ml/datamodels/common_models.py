from typing import List, Optional, Union
from pydantic import BaseModel
<<<<<<< HEAD
from typing import Dict, List, Optional, Union
from .datamodel_enum import *
=======
from datamodel_enum import (
    ServiceMetricNameEnum,
    MlSpecificMetricNameEnum,
    DataQualityEnum,
    OperatorEnum,
    AggregateFunctionEnum,
)
>>>>>>> 95f62ac (update config)



class Metric(BaseModel):
<<<<<<< HEAD
<<<<<<< HEAD
    metric_name: MetricNameEnum
    unit: Optional[str]


class MetricRecord(Metric):
    records: List[Union[dict, float, int]]
=======
<<<<<<< HEAD
    metric_name: Union[
        datamodel_enum.ServiceMetricNameEnum, datamodel_enum.MlSpecificMetricNameEnum
    ]
=======
    metric_name: Union[ServiceMetricNameEnum, MlSpecificMetricNameEnum, DataQualityEnum]
>>>>>>> 95f62ac (update config)
    records: List[Union[dict, float, int]] = []
    unit: Optional[str] = None
>>>>>>> 6b135f6 (fix conflict)


class Condition(BaseModel):
    operator: OperatorEnum
    value: Union[dict, float, int]
=======
    metric_name: ServiceMetricNameEnum | MlSpecificMetricNameEnum | str
    records: List[dict | float | int]
    unit: Optional[str]


class Condition(BaseModel):
    operator: OperatorEnum
    value: dict | float | int
>>>>>>> c0719ca (update)


class MetricConstraint(BaseModel):
    metrics: Metric
    condition: Condition
    aggregate_function: AggregateFunctionEnum



class BaseConstraint(BaseModel):
    name: str
    constraint_list: List[MetricConstraint]


# TODO: can have image size class
