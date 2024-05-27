from typing import Dict, Generic, List, Optional, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel

from ..lang.common_models import Metric
from ..lang.datamodel_enum import MetricNameEnum


class MicroserviceInstance(BaseModel):
    id: UUID
    name: str
    functionality: str = ""
    stage: Optional[str] = None
    # stage: Optional[StageNameEnum] = None


class StageReport(BaseModel):
    # name: StageNameEnum
    name: str
    metrics: Dict[MetricNameEnum, Dict[UUID, Metric]]


class InferenceInstance(BaseModel):
    id: UUID
    execution_instance_id: UUID
    metrics: List[Metric] = []
    prediction: Optional[Union[dict, float]] = None


InstanceType = TypeVar("InstanceType")


class LinkedInstance(BaseModel, Generic[InstanceType]):
    previous: List[InstanceType] = []
    instance: InstanceType


class ExecutionGraph(BaseModel):
    end_point: Optional[MicroserviceInstance] = None
    linked_list: Dict[UUID, LinkedInstance[MicroserviceInstance]]


class InferenceGraph(BaseModel):
    end_point: Optional[InferenceInstance] = None
    linked_list: Dict[UUID, LinkedInstance[InferenceInstance]] = {}


# NOTE: use dict so that we know which stage to add metric to
#
class BaseReport(BaseModel):
    metadata: Dict = {}


class FlattenMetric(Metric):
    stage: str
    instance: MicroserviceInstance
    previous_instances: List[MicroserviceInstance]


class GeneralApplicationReportModel(BaseReport):
    metrics: List[FlattenMetric] = []


class MlQualityReport(BaseModel):
    service: Dict[str, StageReport] = {}
    data: Dict[str, StageReport] = {}


class EnsembleInferenceReport(MlQualityReport):
    ml_specific: Optional[InferenceGraph] = None


class RoheReportModel(BaseReport):
    inference_report: Optional[EnsembleInferenceReport] = None
    execution_graph: Optional[ExecutionGraph] = None
