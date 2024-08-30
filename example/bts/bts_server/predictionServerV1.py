import argparse
import time

import numpy as np
from flask import Flask, request
from predictionService.powerGrid.ML_Loader import ML_Loader


class LSTM_Prediction_PlainServer:
    def __init__(self, configuration):
        # Init the queue for ML request and load the ML model
        self.model_info = configuration["model"]
        self.normalize = configuration["data_normalize"]
        self.model = ML_Loader(self.model_info)

    def predict(self, payload):
        # start calculate response time
        start_time = time.time()
        # load json message
        predict_value = payload
        norm_1 = float(predict_value["norm_1"])
        norm_2 = float(predict_value["norm_2"])
        norm_3 = float(predict_value["norm_3"])
        norm_4 = float(predict_value["norm_4"])
        norm_5 = float(predict_value["norm_5"])
        norm_6 = float(predict_value["norm_6"])
        pas_series = np.array(
            [[norm_1], [norm_2], [norm_3], [norm_4], [norm_5], [norm_6]]
        )
        pas_series = np.array(pas_series)[np.newaxis, :, :]
        # Making prediciton using loader
        result = self.model.prediction(pas_series)
        result = result.reshape(result.shape[1], result.shape[2])
        # Load the result into json format
        response = {"LSTM": float(result[0])}
        self.print_result(response)
        predict_value["LSTM"] = response["LSTM"]
        return predict_value

    def print_result(self, data):
        prediction = ""
        for key in data:
            prediction += f"\n# {key} : {data[key]} "

        prediction_to_str = f"""{'='*40}
        # Prediction Server:{prediction}
        {'='*40}"""
        print(prediction_to_str.replace("  ", ""))


app = Flask(__name__)
# for storing service
service_dict = {}


@app.route("/")
def hello():
    return {"msg": "This is BTS Plain Server that you can use to test "}


@app.route("/create_service", methods=["POST"])
def create_service():
    req_data = request.get_json()
    if req_data["model"] != None:
        model = req_data["model"]
        if model["name"] == "LSTM":
            new_service = LSTM_Prediction_PlainServer(req_data)
            service_dict["LSTM"] = new_service
            new_service.start()
        pass
    return f"the data is {req_data}"


@app.route("/command", methods=["POST"])
def execute_command():
    req_data = request.get_json()
    if req_data["command"] != None:
        command = req_data["command"]
        if command == "START":
            if req_data["model"] != None:
                model_name = req_data["model"]["name"]
                if model_name not in service_dict.keys():
                    if req_data["model"]["name"] == "LSTM":
                        req_service = LSTM_Prediction_PlainServer(req_data)
                        service_dict["LSTM"] = req_service
                        status = f"{model_name} was  started"
                    else:
                        status = f"{model_name} was not found"
                else:
                    status = f"{model_name} has been already  started"
            else:
                status = f"{model_name} was not found"
        elif command == "STOP":
            model_name = req_data["model"]["name"]
            if model_name in service_dict.keys():
                service_dict.pop(model_name)
                status = f"{model_name} was stopped"
            else:
                status = f"{model_name} was not found"
        else:
            status = f"{command} is not supported"
    else:
        status = "command is empty"
    resp_info = {"status": status, "msg": f"the data is {req_data}"}
    return resp_info


@app.route("/predict", methods=["POST"])
def predict():
    req_data = request.get_json()
    service = service_dict["LSTM"]
    result = service.predict(req_data)
    return result


if __name__ == "__main__":
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", help="Port of the service")

    args = parser.parse_args()
    port = int(args.port)
    app.run(debug=True, port=port)
