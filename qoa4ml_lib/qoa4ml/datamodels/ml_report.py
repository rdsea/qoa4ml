from typing import List, Optional, Union

from common_models import Metric
from datamodel_enum import StageNameEnum
from pydantic import BaseModel


class MicroserviceInstance(BaseModel):
    id: str
    name: str
    stage: Optional[str] = None


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
    prediction: Union[dict, float]


class InferenceGraph(BaseModel):
    end_point: InferenceInstance
    linked_list: List[LinkedInstance]


class InferenceQuality(BaseModel):
    service: List[StageReport]
    data: List[StageReport]
    ml_specific: InferenceGraph


class InferenceReport(BaseModel):
    execution_graph: Optional[ExecutionGraph] = None
    quality: Optional[InferenceQuality] = None
