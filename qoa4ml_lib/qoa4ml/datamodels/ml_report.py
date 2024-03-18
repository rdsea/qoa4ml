from typing import List, Optional, Union
from pydantic import BaseModel
from datamodel_enum import StageNameEnum
from common_models import Metric


class Microservice(BaseModel):
    id: str
    name: str
    stage: Optional[str] = None


class MicroserviceInstance(BaseModel):
    id: str
    microservice: List[Microservice]
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
