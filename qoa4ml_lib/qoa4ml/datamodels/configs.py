from typing import Dict, List, Generic, Optional, TypeVar, Union
from pydantic import BaseModel

from .datamodel_enum import (
    MethodEnum,
    MetricCategoryEnum,
    MetricClassEnum,
    ServiceAPIEnum,
    StageNameEnum,
    MetricNameEnum,
)
from .common_models import Metric


class Client(BaseModel):
    id: str
    name: str
    stage: StageNameEnum
    method: MethodEnum
    # TODO: need to be more clear
    application: str
    role: str


class AMQPCollectorConfig(BaseModel):
    end_point: str
    exchange_name: str
    exchange_type: str
    in_routing_key: str
    in_queue: str


class AMQPConnectorConfig(BaseModel):
    end_point: str
    exchange_name: str
    exchange_type: str
    out_routing_key: str


CollectorConfigClass = Union[AMQPCollectorConfig, Dict]
ConnectorConfigClass = Union[AMQPConnectorConfig, Dict]


class CollectorConfig(BaseModel):
    collector_class: ServiceAPIEnum
    config: CollectorConfigClass


class ConnectorConfig(BaseModel):
    connector_class: ServiceAPIEnum
    config: ConnectorConfigClass


class ClientConfig(BaseModel):
    client: Client
    collector: List[CollectorConfig]
    connector: List[ConnectorConfig]


class MetricConfig(Metric):
    name: MetricNameEnum
    metric_class: MetricClassEnum
    description: Optional[str] = None
    default_value: Optional[float] = None
    category: Optional[List[MetricCategoryEnum]] = None
    # NOTE: for getting the metric key when calling external libs like psutil
    key: Optional[str] = None
