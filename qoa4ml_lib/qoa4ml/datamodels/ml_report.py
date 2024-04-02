from typing import Dict, List, Optional, Union

from common_models import Metric
from datamodel_enum import MetricNameEnum, StageNameEnum
from pydantic import BaseModel


class MicroserviceInstance(BaseModel):
    id: str
    name: str
    functionality: str
    stage: Optional[str] = None


class LinkedInstance(BaseModel):
    previous: List[MicroserviceInstance] = []
    microservice: MicroserviceInstance


class ExecutionGraph(BaseModel):
    end_point: Optional[MicroserviceInstance] = None
    linked_list: List[LinkedInstance]


class StageReport(BaseModel):
    id: str
    name: StageNameEnum
    metric: Dict[MetricNameEnum, Metric]


class InferenceInstance(MicroserviceInstance):
    metrics: List[Metric]
    prediction: Union[dict, float]


class InferenceGraph(BaseModel):
    end_point: InferenceInstance
    linked_list: List[LinkedInstance]


# NOTE: use dict so that we know which stage to add metric to
class InferenceQuality(BaseModel):
    service: Dict[StageNameEnum, StageReport] = {}
    data: Dict[StageNameEnum, StageReport] = {}
    ml_specific: Optional[InferenceGraph] = None


class BaseReport(BaseModel):
    quality: Optional[InferenceQuality] = None


class ROHEReport(BaseReport):
    metadata: Optional[Dict] = None
    execution_graph: Optional[ExecutionGraph] = None
