from typing import List

from common_models import BaseConstraint
from datamodel_enum import (
    DataFormatEnum,
    DataTypeEnum,
    DevelopmentEnvironmentEnum,
    InferenceModeEnum,
    InfrastructureEnum,
    ModelCategoryEnum,
    ProcessorEnum,
    ResourceEnum,
    ServiceAPIEnum,
    ServingPlatformEnum,
    StakeholderRoleEnum,
)
from pydantic import BaseModel


class Stakeholder(BaseModel):
    id: str
    name: str
    roles: List[StakeholderRoleEnum]
    provisioning: List[ResourceEnum]


class MicroserviceSpecs(BaseModel):
    id: str
    name: str
    service_api: List[ServiceAPIEnum]
    infrastructure: List[InfrastructureEnum]
    processor_types: List[ProcessorEnum]


class DataSpecs(BaseModel):
    id: str
    name: str
    types: List[DataTypeEnum]
    formats: List[DataFormatEnum]


class MLSpecs(BaseModel):
    id: str
    name: str
    development_environment: List[DevelopmentEnvironmentEnum]
    serving_platform: List[ServingPlatformEnum]
    model_classes: List[ModelCategoryEnum]
    inference_modes: List[InferenceModeEnum]


class ResourceSpecs(BaseModel):
    services_specs: List[MicroserviceSpecs]
    data_specs: DataSpecs
    ml_specs: MLSpecs


class CostConstraint(BaseConstraint):
    name: str = "cost_constraint"


class InterpretabilityConstraint(BaseModel):
    explainability: dict


class FairnessConstraint(BaseConstraint):
    name: str = "fairness_constraint"


class PrivacyConstraint:
    risks: dict


class SecurityConstraint(BaseModel):
    encryption: dict


class MLSpecificConstraint(BaseConstraint):
    name: str = "ml_specific_constraint"


class DataConstraint(BaseConstraint):
    name: str = "data_constaint"


class ServiceConstraint(BaseConstraint):
    name: str = "service_constraint"


class QualityConstraint(BaseModel):
    service: List[ServiceConstraint]
    data: List[DataConstraint]
    ml_specific: List[MLSpecificConstraint]
    security: List[SecurityConstraint]
    privacy: List[PrivacyConstraint]
    fairness: List[FairnessConstraint]
    interpretability: List[InterpretabilityConstraint]
    cost: List[CostConstraint]


class MLContract(BaseModel):
    stakeholders: List[Stakeholder]
    resources: ResourceSpecs
    quality: QualityConstraint
