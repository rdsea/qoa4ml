import yaml
import argparse
import time

from qoa4ml.connector.socket_connector import SocketConnector
from qoa4ml.datamodels.configs import ProcessProbeConfig, SocketConnectorConfig
from qoa4ml.probes.process_monitoring_probe import ProcessMonitoringProbe

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c", "--config", help="config path", default="config/process_probe_conf.yaml"
    )
    args = parser.parse_args()
    config_file = args.config
    with open(config_file, encoding="utf-8") as file:
        proces_config = ProcessProbeConfig(**yaml.safe_load(file))
    connector = SocketConnector(SocketConnectorConfig(host="127.0.0.1", port=12345))
    process_monitoring_probe = ProcessMonitoringProbe(proces_config, connector)
    del proces_config
    process_monitoring_probe.start_reporting()
    time.sleep(10)
    process_monitoring_probe.stop_reporting()
