import argparse
import logging
import yaml
from fastapi import FastAPI
import uvicorn
from .node_aggregator import NodeAggregator
from .core.common import ODOP_PATH

logging.basicConfig(
    format="%(asctime)s:%(levelname)s -- %(message)s", level=logging.INFO
)


class Exporter:
    def __init__(self, config: dict) -> None:
        self.app = FastAPI()
        self.config = config
        self.node_aggregator = NodeAggregator(self.config["node_aggregator"])
        self.app.include_router(self.node_aggregator.router)

    def start(self):
        self.node_aggregator.start()
        uvicorn.run(self.app, host=self.config["host"], port=self.config["port"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="config path", default="config/exporter_config.yaml"
    )
    args = parser.parse_args()
    config_file = args.config
    with open(ODOP_PATH + config_file, encoding="utf-8") as file:
        exporter_config = yaml.safe_load(file)
    exporter = Exporter(exporter_config)
    exporter.start()
