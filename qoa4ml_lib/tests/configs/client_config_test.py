from uuid import UUID

from qoa4ml.datamodels.configs import (
    AMQPCollectorConfig,
    AMQPConnectorConfig,
    ClientInfo,
    ClientConfig,
    CollectorConfig,
    ConnectorConfig,
)
from qoa4ml.datamodels.datamodel_enum import (
    FunctionalityEnum,
    ServiceAPIEnum,
    StageNameEnum,
)

client = ClientInfo(
    id=UUID("7191a40f-ac85-4ca8-aa25-8114213e006a"),
    name="data_handling01",
    stage=StageNameEnum.gateway,
    functionality=FunctionalityEnum.rest,
    application="test",
    role="ml",
)

collector_config = CollectorConfig(
    collector_class=ServiceAPIEnum.amqp,
    config=AMQPCollectorConfig(
        end_point="localhost",
        exchange_name="qoa4ml",
        exchange_type="topic",
        in_routing_key="qoa1.report.#",
        in_queue="collector_1",
    ),
)
connector_config = ConnectorConfig(
    connector_class=ServiceAPIEnum.amqp,
    config=AMQPConnectorConfig(
        end_point="localhost",
        exchange_name="qoa4ml",
        exchange_type="topic",
        out_routing_key="qoa1.report.ml",
    ),
)

client_config = ClientConfig(
    client=client, collector=collector_config, connector=connector_config
)

client_config.model_dump_json()
with open("client_config.json", "w") as file:
    file.write(client_config.model_dump_json())
