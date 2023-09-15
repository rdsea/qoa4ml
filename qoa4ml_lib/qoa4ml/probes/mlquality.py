# This library is built based on ydata_quality: https://github.com/ydataai/ydata-quality
import pandas as pd 
import numpy as np
import traceback, sys, pathlib
p_dir = pathlib.Path(__file__).parent.parent.absolute()
sys.path.append(str(p_dir))
from from qoaUtils import is_numpyarray, qoaLogger

try:
    import tensorflow as tf
except Exception as e:
    qoaLogger.error("Error {} when importing TensorFlow: {}".format(type(e),e.__traceback__))
    traceback.print_exception(*sys.exc_info())


################################################ ML QUALITY ########################################################

def timeseries_metric(model):
    metrics = {}
    try:
        if isinstance(model, tf.keras.Sequential):
            for metric in model.metrics:
                metrics[metric.name] = metric.result().numpy()
        return metrics
    except Exception as e:
        qoaLogger.error("Error {} when querying timeseries model metrics: {}".format(type(e),e.__traceback__))
        traceback.print_exception(*sys.exc_info())
        return {"Error": "Unable to get metrics"}

def ts_inference_metric(model,name):
    try:
        metrics = timeseries_metric(model)
        results = {}
        if name in metrics:
            results[name] = metrics[name]
        if "Error" in metrics:
            results["Error"] = metrics["Error"]
        return results
    except Exception as e:
        qoaLogger.error("Error {} when querying timeseries {}: {}".format(type(e),name,e.__traceback__))
        traceback.print_exception(*sys.exc_info())
        return {"Error": "Unable to get model {}".format(name)}
    
def ts_inference_MAE(model):
    try:
        metrics = ts_inference_metric(model, "mean_absolute_error")
        return {"MAE":metrics}
    except Exception as e:
        qoaLogger.error("Error {} when querying timeseries mean absolute error: {}".format(type(e),e.__traceback__))
        traceback.print_exception(*sys.exc_info())
        return {"Error": "Unable to get model mean absolute error"}
    
def ts_inference_loss(model):
    try:
        metrics = ts_inference_metric(model, "loss")
        return {"Loss":metrics}
    except Exception as e:
        qoaLogger.error("Error {} when querying timeseries mean absolute error: {}".format(type(e),e.__traceback__))
        traceback.print_exception(*sys.exc_info())
        return {"Error": "Unable to get model mean absolute error"}
    

def training_metric(model):
    try:
        if isinstance(model, tf.keras.Sequential):
            return model.history.history
        else:
            return None
    except Exception as e:
        qoaLogger.error("Error {} when querying training metrics: {}".format(type(e),e.__traceback__))
        traceback.print_exception(*sys.exc_info())
        return {"Error": "Unable to get training metrics"}
    
def training_loss(model):
    try:
        if isinstance(model, tf.keras.Sequential):
            return {"Training Loss":model.history.history["loss"]}
        else:
            return None
    except Exception as e:
        qoaLogger.error("Error {} when querying training loss: {}".format(type(e),e.__traceback__))
        traceback.print_exception(*sys.exc_info())
        return {"Error": "Unable to get training loss"}
    
def training_val_accuracy(model):
    try:
        if isinstance(model, tf.keras.Sequential):
            return {"Evaluate Accuracy":model.history.history["val_accuracy"]}
        else:
            return None
    except Exception as e:
        qoaLogger.error("Error {} when querying training validation accuracy: {}".format(type(e),e.__traceback__))
        traceback.print_exception(*sys.exc_info())
        return {"Error": "Unable to get validation accuracy"}

def training_accuracy(model):
    try:
        if isinstance(model, tf.keras.Sequential):
            return {"Train Accuracy": model.history.history["accuracy"]}
        else:
            return None
    except Exception as e:
        qoaLogger.error("Error {} when querying training accuracy: {}".format(type(e),e.__traceback__))
        traceback.print_exception(*sys.exc_info())
        return {"Error": "Unable to get accuracy"}
    
def training_val_loss(model):
    try:
        if isinstance(model, tf.keras.Sequential):
            return {"Evaluate Loss":model.history.history["val_loss"]}
        else:
            return None
    except Exception as e:
        qoaLogger.error("Error {} when querying training validation loss: {}".format(type(e),e.__traceback__))
        traceback.print_exception(*sys.exc_info())
        return {"Error": "Unable to get validation loss"}

def classification_confidence(data, score=True):
    try:
        if score:
            return {"Confidence": 100 * np.max(data)}
        else:
            if is_numpyarray(data):
                scores = tf.nn.softmax(data[0])
                return {"Confidence":100 * np.max(scores)}
            else:
                return {"Error": "Unsupported data: {}".format(type(data))}
    except Exception as e:
        qoaLogger.error("Error {} in extracting classification confidence: {}".format(type(e),e.__traceback__))
        traceback.print_exception(*sys.exc_info())
        return {"Error": "Unable to get classification confidence"}





