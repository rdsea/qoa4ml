import argparse

from qoa4ml.collector.amqp_collector import AmqpCollector
from qoa4ml.config.configs import AMQPCollectorConfig

conf = {
    "end_point": "rabbitmq.aaltosea.csc",
    "exchange_name": "eemls",
    "exchange_type": "topic",
    "in_routing_key": "eemls.#",
    "in_queue": "collector_1",
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Node Monitoring")
    parser.add_argument("--conf", help="configuration file", default="collector.json")
    args = parser.parse_args()
    ampq_conf = AMQPCollectorConfig(**conf)
    collector = AmqpCollector(configuration=ampq_conf)
    collector.start_collecting()
