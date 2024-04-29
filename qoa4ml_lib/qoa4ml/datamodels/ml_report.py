from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel

from .common_models import Metric
from .datamodel_enum import MetricNameEnum, StageNameEnum


class MicroserviceInstance(BaseModel):
    id: UUID
    name: str
    functionality: str
    stage: Optional[str] = None


class StageReport(BaseModel):
    name: StageNameEnum
    metric: Dict[MetricNameEnum, Dict[UUID, Metric]]


class InferenceInstance(BaseModel):
    id: UUID
    execution_instance_id: UUID
    metrics: List[Metric]
    prediction: Union[dict, float]


InstanceType = Union[MicroserviceInstance, InferenceInstance]


class LinkedInstance(BaseModel):
    previous: List[InstanceType] = []
    instance: InstanceType


class ExecutionGraph(BaseModel):
    end_point: Optional[MicroserviceInstance] = None
    linked_list: Dict[str, LinkedInstance]


class InferenceGraph(BaseModel):
    end_point: InferenceInstance
    linked_list: Dict[UUID, LinkedInstance]


# NOTE: use dict so that we know which stage to add metric to
class QualityReport(BaseModel):
    service: Dict[StageNameEnum, StageReport] = {}


class InferenceReport(QualityReport):
    ml_specific: Optional[InferenceGraph] = None
    data: Dict[StageNameEnum, StageReport] = {}


class RoheReportModel(BaseModel):
    inference_report: Optional[InferenceReport] = None
    metadata: Optional[Dict] = None
    execution_graph: Optional[ExecutionGraph] = None
