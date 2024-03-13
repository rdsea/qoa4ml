from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel
import json


class InstanceReport(BaseModel):
    instance_id: str
    value: float | Dict[str, float]


class MetricNameEnum(Enum):
    response_time = "responseTime"


class StageNameEnum(Enum):
    ml_inference_aggregate_stage = ""


class MethodEnum(Enum):
    REST = "REST"


class Metric(BaseModel):
    metric_name: MetricNameEnum
    record: dict | float | int


class Microservice(BaseModel):
    id: str
    name: str
    stage: Optional[str]


class MicroserviceInstance(BaseModel):
    id: str
    microservice: Microservice
    functionality: str


class LinkedInstance(BaseModel):
    previous: List[MicroserviceInstance]
    microservice_instance: MicroserviceInstance


class ExecutionGraph(BaseModel):
    end_point: MicroserviceInstance
    linked_list: List[LinkedInstance]


class StageReport(BaseModel):
    id: str
    name: StageNameEnum
    metric: List[Metric]


class InferenceInstance(MicroserviceInstance):
    metrics: List[Metric]
    prediction: dict | float


# TODO: test if InferenceInstance can be used in LinkedInstance
class InferenceGraph(BaseModel):
    end_point: InferenceInstance
    linked_list: List[LinkedInstance]


class InferenceQuality(BaseModel):
    service: List[StageReport]
    data: List[StageReport]
    ml_specific: InferenceGraph


class InferenceReport(BaseModel):
    execution_graph: ExecutionGraph | None
    quality: InferenceQuality | None
