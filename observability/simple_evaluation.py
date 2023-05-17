# a simple python showing how to invoke the QoA4ML OPA service
import requests
import argparse
import json
parser = argparse.ArgumentParser()
parser.add_argument('--purl', help='qoa4ml OPA service', default=' http://localhost:8181/v1/data/qoa4ml/bts/alarm/contract_violation')
parser.add_argument('--input',help='json input file of metrics')
args = parser.parse_args()

with open(args.input, 'r') as input_file:
    data=input_file.read()
input_metrics = json.loads(data)
payload = {"input":input_metrics}
headers = {
  'Content-Type': 'application/json'
}
response = requests.request("POST", args.purl, headers=headers, data = json.dumps(payload))

print(response.text.encode('utf8'))
