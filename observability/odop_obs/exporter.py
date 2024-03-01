from fastapi import FastAPI
import uvicorn, argparse, yaml, time, os, logging, sys
from node_aggregator import NodeAggregator

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
    config = yaml.safe_load(open(ODOP_PATH + config_file))
    exporter = Exporter(config)
    exporter.start()
