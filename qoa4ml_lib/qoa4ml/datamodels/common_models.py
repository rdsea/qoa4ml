from typing import List, Optional, Union
from pydantic import BaseModel
from typing import Dict, List, Optional, Union
from .datamodel_enum import *



class Metric(BaseModel):
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
