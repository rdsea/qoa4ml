import json
import unittest
from devtools import debug
from unittest.mock import MagicMock

from qoa4ml.datamodels.configs import Client
from qoa4ml.reports.rohe_reports import RoheReport


class TestQoaReport(unittest.TestCase):
    def setUp(self):
        with open("./data/client_config.json") as f:
            client_config_dict = json.load(f)
            self.client_config = Client(**client_config_dict)
            self.rohe_report = RoheReport(self.client_config)

    def test_reset(self):
        self.rohe_report.reset()
        self.assertEqual(len(self.rohe_report.previous_report), 0)
        self.assertIsNone(self.rohe_report.inference_report.ml_specific)
        self.assertEqual(len(self.rohe_report.inference_report.service), 0)
        self.assertEqual(len(self.rohe_report.inference_report.data), 0)
        self.assertEqual(len(self.rohe_report.execution_graph.linked_list), 0)
        self.assertIsNone(self.rohe_report.execution_graph.end_point)

    def test_import_report_from_file(self):
        self.rohe_report.import_report_from_file("./data/imported_report.json")

    #
    # def test_combine_stage_report(self):
    #     # self.rohe_report.import_report_from_file("./data/current_report.json")
    #     previous_report = RoheReport(
    #         self.client_config, "./data/previous_report_1.json"
    #     )
    #     test = self.rohe_report.combine_stage_report(
    #         self.rohe_report.inference_report.service,
    #         previous_report.inference_report.service,
    #     )
    #     debug(test)

    def test_process_previous_report(self):
        # self.rohe_report.import_report_from_file("./data/previous_report_2.json")
        previous_report_1 = RoheReport(
            self.client_config, "./data/previous_report_1.json"
        )
        previous_report_2 = RoheReport(
            self.client_config, "./data/previous_report_2.json"
        )
        self.rohe_report.process_previous_report(previous_report_1.report)
        self.rohe_report.process_previous_report(previous_report_2.report)
        debug(self.rohe_report.report)


if __name__ == "__main__":
    unittest.main()
