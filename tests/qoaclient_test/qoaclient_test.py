import os
from random import random

from qoa4ml.qoa_client import QoaClient
from qoa4ml.reports.ml_reports import MLReport

dir_path = os.path.dirname(os.path.realpath(__file__))


def test_creating_qoaclient_from_file():
    _ = QoaClient(config_path=f"{dir_path}/config/client.yaml")


def test_creating_qoaclient_from_dict():
    config = {
        "client": {
            "name": "qoa_client_test",
            "username": "aaltosea",
            "user_id": "1",
            "instance_id": "b6f83293-cf67-44dd-a7b5-77229d384012",
            "instance_name": "aaltosea_instance_test1",
            "stage_id": "gateway",
            "functionality": "REST",
            "application_name": "test",
            "role": "ml",
            "run_id": "test1",
            "custom_info": {"your_custom_info": 1},
        },
        "connector": [
            {
                "name": "debug_connector",
                "connector_class": "Debug",
                "config": {"silence": True},
            }
        ],
    }
    _ = QoaClient(config_dict=config)


def test_submiting_report():
    qoa_client = QoaClient(
        report_cls=MLReport, config_path=f"{dir_path}/config/client.yaml"
    )
    qoa_client.observe_metric("test", random())
    qoa_client.report(submit=True)


def test_submiting_custom_report():
    qoa_client = QoaClient(
        report_cls=MLReport, config_path=f"{dir_path}/config/client.yaml"
    )
    qoa_client.observe_metric("test", random())
    report = {
        "test": "123456",
    }
    qoa_client.report(report=report, submit=True)
