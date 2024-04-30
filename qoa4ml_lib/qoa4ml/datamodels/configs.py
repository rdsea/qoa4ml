from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from .datamodel_enum import (
    FunctionalityEnum,
    MetricCategoryEnum,
    MetricClassEnum,
    MetricNameEnum,
    ServiceAPIEnum,
    StageNameEnum,
)


class Client(BaseModel):
    id: UUID
    name: str
    stage: StageNameEnum
    functionality: FunctionalityEnum
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


class MQTTConnectorConfig(BaseModel):
    in_queue: str
    out_queue: str
    broker_url: str
    broker_port: int
    broker_keepalive: int
    client_id: str


class PrometheusConnectorConfig(BaseModel):
    pass


# TODO: test if loading the config, the type of the config can be found
CollectorConfigClass = Union[AMQPCollectorConfig, Dict]
ConnectorConfigClass = Union[AMQPConnectorConfig, Dict]


class CollectorConfig(BaseModel):
    name: str
    collector_class: ServiceAPIEnum
    config: CollectorConfigClass


class ConnectorConfig(BaseModel):
    name: str
    connector_class: ServiceAPIEnum
    config: ConnectorConfigClass


class ClientConfig(BaseModel):
    client: Client
    registration_url: Optional[str] = None
    collector: Optional[List[CollectorConfig]] = None
    connector: Optional[List[ConnectorConfig]] = None


class MetricConfig(BaseModel):
    name: MetricNameEnum
    metric_class: MetricClassEnum
    description: Optional[str] = None
    default_value: int
    category: int
    # NOTE: for getting the metric key when calling external libs like psutil
    key: Optional[str] = None


class GroupMetricConfig(BaseModel):
    name: str
    metric_configs: List[MetricConfig]
