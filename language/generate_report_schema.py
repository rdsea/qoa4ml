import argparse
import json

from qoa4ml.reports.ml_report_model import (
    ENSEMBLE_REPORT_NAME,
    ENSEMBLE_REPORT_VERSION,
    GENERAL_REPORT_NAME,
    GENERAL_REPORT_VERSION,
    ML_REPORT_NAME,
    ML_REPORT_VERSION,
    GeneralApplicationReportModel,
    GeneralMlInferenceReport,
    RoheReportModel,
)

parser = argparse.ArgumentParser()
parser.add_argument(
    "--target-dir", help="Target directory to save the JSON file", default="."
)
args = parser.parse_args()

target_dir = args.target_dir

main_model_schema = GeneralApplicationReportModel.model_json_schema()
with open(
    f"{target_dir}/{GENERAL_REPORT_NAME}-{GENERAL_REPORT_VERSION}.json", "w"
) as f:
    f.write(json.dumps(main_model_schema, indent=4))

main_model_schema = GeneralMlInferenceReport.model_json_schema()
with open(f"{target_dir}/{ML_REPORT_NAME}-{ML_REPORT_VERSION}.json", "w") as f:
    f.write(json.dumps(main_model_schema, indent=4))

main_model_schema = RoheReportModel.model_json_schema()
with open(
    f"{target_dir}/{ENSEMBLE_REPORT_NAME}-{ENSEMBLE_REPORT_VERSION}.json", "w"
) as f:
    f.write(json.dumps(main_model_schema, indent=4))
