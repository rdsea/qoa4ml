import argparse
import json
import random
import time

import pandas as pd
import requests
from qoa4ml import qoaUtils as qoa_utils
from qoa4ml.qoa_client import Qoa_Client

headers = {"Content-Type": "application/json"}


def denormalize(value):
    return value * data_normalize["max"] + data_normalize["mean"]


if __name__ == "__main__":
    # Load configuration
    parser = argparse.ArgumentParser(description="simple bts rest client")
    parser.add_argument("--config", default="./client.json")
    args = parser.parse_args()
    client_config = qoa_utils.load_config(args.config)
    ml_config = client_config["ml_service"]
    data_normalize = client_config["data_normalize"]

    # Load ML service configuration
    file = ml_config["file"]
    ml_serving_url = ml_config["url"] + "/predict"

    ############################################### INIT QOA CLIENT ##################################################################
    qoa_config = client_config["qoa_service"]
    qoa_client = Qoa_Client(qoa_config["client_info"], qoa_config["registration"])
    ####################################################################################################################################

    # Read data
    raw_dataset = pd.read_csv(file)
    raw_dataset = raw_dataset.astype(
        {
            "norm_value": "float",
            "norm_1": "float",
            "norm_2": "float",
            "norm_3": "float",
            "norm_4": "float",
            "norm_5": "float",
            "norm_6": "float",
        }
    )
    print("Sending request...")
    error = 0
    for index, line in raw_dataset.iterrows():
        time.sleep(random.uniform(0.2, 1))
        # Parse data
        dict_mess = {
            "norm_value": float(line["norm_value"]),
            "norm_1": float(line["norm_1"]),
            "norm_2": float(line["norm_2"]),
            "norm_3": float(line["norm_3"]),
            "norm_4": float(line["norm_4"]),
            "norm_5": float(line["norm_5"]),
            "norm_6": float(line["norm_6"]),
        }
        # print("Sending request: {}".format(line))
        # Publish data to a specific topi
        start_time = time.time()
        json_mess = {
            "model": "LSTM",
            "data": {
                "norm_value": float(dict_mess["norm_value"]),
                "norm_1": float(dict_mess["norm_1"]),
                "norm_2": float(dict_mess["norm_2"]),
                "norm_3": float(dict_mess["norm_3"]),
                "norm_4": float(dict_mess["norm_4"]),
                "norm_5": float(dict_mess["norm_5"]),
                "norm_6": float(dict_mess["norm_6"]),
                "start_time": start_time,
            },
        }
        # Start qoa timer for calculating response time
        qoa_client.timer()

        response = requests.request(
            "POST", ml_serving_url, headers=headers, data=json.dumps(json_mess)
        )
        # Response_time is already report by calling timer 2nd time
        response_time = qoa_client.timer()

        dict_response = response.json()
        if "result" in dict_response:
            predict_value = dict_response["result"]
            print(dict_response)
            if isinstance(predict_value, dict):
                if "LSTM" in predict_value:
                    pre_val = denormalize(predict_value["LSTM"])
                    inference_id = predict_value["inference_id"]
                    dict_predicted = {"LSTM": pre_val}
                    # calculate accuracy
                    accuracy = (
                        1
                        - abs(
                            (predict_value["LSTM"] - float(predict_value["norm_value"]))
                            / float(predict_value["norm_value"])
                        )
                    ) * 100
                    if accuracy < 0:
                        accuracy = 0
                    # calculate response time
                    response_time = time.time() - predict_value["start_time"]
                    # return prediction analysis
                    ml_response = {
                        "Prediction": dict_predicted,
                        "ResponseTime": response_time,
                        "Accuracy": accuracy,
                    }
                    print(ml_response)
            print(predict_value)
        else:
            print(dict_response)

        ####################### SEND THE QOA4ML REPORT #########################
        if "accuracy" in locals():
            print(accuracy)
            qoa_client.inference_report(
                value=pre_val, accuracy=accuracy, inference_id=inference_id
            )
        else:
            print("Error: ", error)
            error += 1
            qoa_client.observeMetric("service_errors", error, service_quality=True)
        qoa_report = qoa_client.get_report(submit=True)
        print("--------------\nQoA Report: \n", qoa_report, "\n--------------")
        ########################################################################
