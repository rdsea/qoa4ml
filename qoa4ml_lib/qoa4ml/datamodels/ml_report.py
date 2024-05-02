from typing import Dict, Generic, List, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel

from .common_models import Metric
from .datamodel_enum import FunctionalityEnum, MetricNameEnum, StageNameEnum


class MicroserviceInstance(BaseModel):
    id: UUID
    name: str
    functionality: FunctionalityEnum
    stage: Optional[StageNameEnum] = None


class StageReport(BaseModel):
    name: StageNameEnum
    metrics: Dict[MetricNameEnum, Dict[UUID, Metric]]


class InferenceInstance(BaseModel):
    id: UUID
    execution_instance_id: UUID
    metrics: List[Metric]
    prediction: Union[dict, float]


InstanceType = TypeVar("InstanceType")


class LinkedInstance(BaseModel, Generic[InstanceType]):
    previous: List[InstanceType] = []
    instance: InstanceType


class ExecutionGraph(BaseModel):
    end_point: Optional[MicroserviceInstance] = None
    linked_list: Dict[UUID, LinkedInstance[MicroserviceInstance]]


class InferenceGraph(BaseModel):
    end_point: Optional[InferenceInstance] = None
    linked_list: Dict[UUID, LinkedInstance[InferenceInstance]]


# NOTE: use dict so that we know which stage to add metric to
class QualityReport(BaseModel):
    service: Dict[StageNameEnum, StageReport] = {}


class InferenceReport(QualityReport):
    ml_specific: Optional[InferenceGraph] = None
    data: Dict[StageNameEnum, StageReport] = {}


class RoheReportModel(BaseModel):
    inference_report: Optional[InferenceReport] = None
    metadata: Dict = {}
    execution_graph: Optional[ExecutionGraph] = None
