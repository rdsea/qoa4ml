"""
a simple python showing how to invoke the QoA4ML OPA service
"""

import argparse
import json
import sys

import requests

V1_API = "/v1/data/qoa4ml/bts/alarm/contract_violation"
parser = argparse.ArgumentParser()
parser.add_argument(
    "--purl", help="qoa4ml OPA service", default="http://localhost:8181"
)
parser.add_argument("--input", help="json input file of metrics")
args = parser.parse_args()

if args.input is None:
    print("Input file is not specified")
    sys.exit(0)
with open(args.input, encoding="utf-8") as input_file:
    data = input_file.read()
input_metrics = json.loads(data)
payload = {"input": input_metrics}
headers = {"Content-Type": "application/json"}
url = f"{args.purl}{V1_API}"
response = requests.request("POST", url, headers=headers, data=json.dumps(payload))

print(response.text.encode("utf8"))
