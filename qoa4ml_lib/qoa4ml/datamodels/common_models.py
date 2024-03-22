from typing import List, Optional, Union
from pydantic import BaseModel
import datamodel_enum



class Metric(BaseModel):
<<<<<<< HEAD
    metric_name: Union[
        datamodel_enum.ServiceMetricNameEnum, datamodel_enum.MlSpecificMetricNameEnum
    ]
    records: List[Union[dict, float, int]] = []
    unit: Optional[str] = None


class Condition(BaseModel):
    operator: datamodel_enum.OperatorEnum
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
    aggregate_function: datamodel_enum.AggregateFunctionEnum



class BaseConstraint(BaseModel):
    name: str
    constraint_list: List[MetricConstraint]
