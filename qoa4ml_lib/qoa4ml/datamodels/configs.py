from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from .datamodel_enum import (
    EnvironmentEnum,
    FunctionalityEnum,
    MetricClassEnum,
    MetricNameEnum,
    ServiceAPIEnum,
    StageNameEnum,
)


class ClientInfo(BaseModel):
    id: Optional[str] = ""
    name: Optional[str] = ""
    user_id: Optional[str] = ""
    instance_id: Optional[str] = ""
    stage_id: Optional[str] = ""
    functionality: Optional[str] = ""
    application_name: Optional[str] = ""
    role: Optional[str] = ""
    run_id: Optional[str] = ""


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


class SocketConnectorConfig(BaseModel):
    host: str
    port: int


class SocketCollectorConfig(BaseModel):
    host: str
    port: int
    backlog: int
    bufsize: int


class PrometheusConnectorConfig(BaseModel):
    pass


# TODO: test if loading the config, the type of the config can be found
CollectorConfigClass = Union[AMQPCollectorConfig, SocketCollectorConfig, Dict]
ConnectorConfigClass = Union[AMQPConnectorConfig, SocketConnectorConfig, Dict]


class CollectorConfig(BaseModel):
    name: str
    collector_class: ServiceAPIEnum
    config: CollectorConfigClass


class ConnectorConfig(BaseModel):
    name: str
    connector_class: ServiceAPIEnum
    config: ConnectorConfigClass


class ClientConfig(BaseModel):
    client: ClientInfo
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


class ProbeConfig(BaseModel):
    frequency: int
    require_register: bool
    obs_service_url: Optional[str] = None
    log_latency_flag: bool
    latency_logging_path: str
    environment: EnvironmentEnum


class ProcessProbeConfig(ProbeConfig):
    pid: Optional[int] = None


class SystemProbeConfig(ProbeConfig):
    node_name: Optional[str] = None


class NodeAggregatorConfig(BaseModel):
    socket_collector_config: SocketCollectorConfig
    environment: EnvironmentEnum
    query_method: str
    data_separator: str
    unit_conversion: dict


class ExporterConfig(BaseModel):
    host: str
    port: int
    node_aggregator: NodeAggregatorConfig


class OdopObsConfig(BaseModel):
    process: ProcessProbeConfig
    system: SystemProbeConfig
    probe_connector: SocketConnectorConfig
    exporter: ExporterConfig
