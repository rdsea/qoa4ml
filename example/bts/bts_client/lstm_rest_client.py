import random
import time
import argparse

import pandas as pd
import json

import requests


headers = {
    'Content-Type': 'application/json'
}

data_normalize={
        "max": 12.95969626,
        "mean": 12.04030374
}
def denormalize(value):
    return value*data_normalize["max"]+data_normalize["mean"]
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="simple bts rest client")
    parser.add_argument('--file', default="../data/1161114002_122_norm.csv")
    parser.add_argument('--url', default="http://127.0.0.1:5000")
    args = parser.parse_args()
    file =args.file
    ml_serving_url=args.url+"/predict"
    raw_dataset = pd.read_csv(file)
    raw_dataset = raw_dataset.astype({'norm_value':'float','norm_1':'float', 'norm_2':'float', 'norm_3':'float', 'norm_4':'float', 'norm_5':'float', 'norm_6':'float'})
    print("Sending request...")
    for index, line in raw_dataset.iterrows():
        time.sleep(random.uniform(0.2, 1))
        # Parse data
        dict_mess = {
            "norm_value" : float(line["norm_value"]),
            "norm_1" : float(line["norm_1"]),
            "norm_2" : float(line["norm_2"]),
            "norm_3" : float(line["norm_3"]),
            "norm_4" : float(line["norm_4"]),
            "norm_5" : float(line["norm_5"]),
            "norm_6" : float(line["norm_6"])
        }
        # print("Sending request: {}".format(line))
        # Publish data to a specific topi
        start_time = time.time()
        json_mess = {
            "norm_value": float(dict_mess["norm_value"]), 
            "norm_1": float(dict_mess["norm_1"]), 
            "norm_2": float(dict_mess["norm_2"]), 
            "norm_3": float(dict_mess["norm_3"]), 
            "norm_4": float(dict_mess["norm_4"]),
            "norm_5": float(dict_mess["norm_5"]),
            "norm_6": float(dict_mess["norm_6"]),
            "start_time": start_time
        }
        response = requests.request("POST", ml_serving_url, headers=headers, data=json.dumps(json_mess))
        predict_value = response.json()
        print(predict_value)
        
        pre_val = denormalize(predict_value["LSTM"])
        dict_predicted = {
            "LSTM": pre_val
        }
        # calculate accuracy
        accuracy =  (1 - abs((predict_value["LSTM"] - float(predict_value["norm_value"]))/float(predict_value["norm_value"])))*100
        if accuracy < 0:
            accuracy = 0
        # calculate response time
        response_time = time.time() - predict_value["start_time"]
        # return prediction analysis
        ml_response = {"Prediction": dict_predicted, "ResponseTime": response_time, "Accuracy": accuracy}
        print(ml_response)