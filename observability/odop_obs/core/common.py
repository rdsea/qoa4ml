import os
import logging
from typing import Optional
from pydantic import BaseModel

ODOP_PATH = os.getenv("ODOP_PATH")
if not ODOP_PATH:
    logging.error("No ODOP_PATH environment variable")


class ProcessMetadata(BaseModel):
    pid: str
    user: str


class SystemMetadata(BaseModel):
    node_name: str


class ResourceReport(BaseModel):
    metadata: Optional[dict] = None
    usage: dict


class ProcessReport(BaseModel):
    metadata: ProcessMetadata
    timestamp: float
    cpu: ResourceReport
    gpu: Optional[ResourceReport] = None
    mem: ResourceReport


class SystemReport(BaseModel):
    metadata: SystemMetadata
    timestamp: float
    cpu: ResourceReport
    gpu: Optional[ResourceReport] = None
    mem: ResourceReport


class ProcessProbeConfig(BaseModel):
    frequency: int
    requireRegister: bool
    log_latency_flag: bool
    latency_logging_path: str
    aggregator_host: str
    aggregator_port: int


class SystemProbeConfig(BaseModel):
    frequency: int
    requireRegister: bool
    latency_logging_path: str
    log_latency_flag: bool
    aggregator_host: str
    aggregator_port: int


class NodeAggregator(BaseModel):
    host: str
    port: int
    database_path: str
    query_method: str
    backlog_number: int
    socket_package_size: int
    data_separator: str
    unit_conversion: dict


class ExporterConfig(BaseModel):
    host: str
    port: int
    node_aggregator: NodeAggregator


class OdopObsConfig(BaseModel):
    process: ProcessProbeConfig
    system: SystemProbeConfig
    exporter: ExporterConfig
