from typing import Dict, List, Optional
from pydantic import BaseModel
from datamodel_enum import (
    StakeholderRoleEnum,
    ResourceEnum,
    ServiceAPIEnum,
    InfrastructureEnum,
    ProcessorEnum,
    DataTypeEnum,
    DataFormatEnum,
    DevelopmentEnvironmentEnum,
    ServingPlatformEnum,
    ModelCategoryEnum, 
    InferenceModeEnum
)
from common_models import BaseConstraint


class Stakeholder(BaseModel):
    id: str
    name: str
    roles: StakeholderRoleEnum
    provisioning: ResourceEnum


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


class ResourceConstraint(BaseModel):
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
    resources: ResourceConstraint
    quality: QualityConstraint
