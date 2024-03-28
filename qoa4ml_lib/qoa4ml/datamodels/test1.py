from qoa4ml.datamodels.datamodel_enum import (DataFormatEnum, DataTypeEnum,
                                              DevelopmentEnvironmentEnum,
                                              InferenceModeEnum,
                                              ModelCategoryEnum, ProcessorEnum,
                                              ResourceEnum, ServiceAPIEnum,
                                              ServingPlatformEnum,
                                              StakeholderRoleEnum)
from qoa4ml.datamodels.ml_contract import (DataSpecs, InfrastructureEnum,
                                           MicroserviceSpecs, MLSpecs,
                                           QualityConstraint, ResourceSpecs,
                                           Stakeholder)

stakeholder = Stakeholder(
    id="stakeholder_id",
    name="rdsea",
    roles=[StakeholderRoleEnum.ml_provider, StakeholderRoleEnum.ml_infrastructure],
    provisioning=[ResourceEnum.ml_service, ResourceEnum.ml_models],
)

resource_specs = ResourceSpecs(
    services_specs=[
        MicroserviceSpecs(
            id="service_id",
            name="rdsea_service",
            service_api=[ServiceAPIEnum.rest, ServiceAPIEnum.mqtt],
            infrastructure=[
                InfrastructureEnum.raspi4,
                InfrastructureEnum.nvidia_jetson_nano,
            ],
            processor_types=[ProcessorEnum.cpu, ProcessorEnum.gpu],
        )
    ],
    data_specs=DataSpecs(
        id="data_id",
        name="data_type",
        types=[DataTypeEnum.image, DataTypeEnum.video],
        formats=[DataFormatEnum.png, DataFormatEnum.mp4],
    ),
    ml_specs=MLSpecs(
        id="ml_spec_id",
        name="ml_spec_name",
        development_environment=[DevelopmentEnvironmentEnum.onnx],
        serving_platform=[ServingPlatformEnum.tensorflow],
        model_classes=[ModelCategoryEnum.ann, ModelCategoryEnum.cnn],
        inference_modes=[InferenceModeEnum.dynamic],
    ),
)

quality = QualityConstraint()
