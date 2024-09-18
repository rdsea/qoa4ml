import argparse
import json

from qoa4ml.lang.ml_contract import ML_CONTRACT_NAME, ML_CONTRACT_VERSION, MLContract

parser = argparse.ArgumentParser()
parser.add_argument(
    "--target-dir", help="Target directory to save the JSON file", default="../language"
)
args = parser.parse_args()

target_dir = args.target_dir

main_model_schema = MLContract.model_json_schema()
with open(f"{target_dir}/{ML_CONTRACT_NAME}-{ML_CONTRACT_VERSION}.json", "w") as f:
    f.write(json.dumps(main_model_schema, indent=4))
