from typing import List, Optional
from pydantic import BaseModel
from .datamodel_enum import *
from .common_models import *


class MicroserviceInstance(BaseModel):
    id: str
    name: str
    stage: Optional[str]


class Microservice(BaseModel):
    id: str
    microservice: List[MicroserviceInstance]
    functionality: str


class LinkedInstance(BaseModel):
    previous: List[MicroserviceInstance]
    microservice: Microservice


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
