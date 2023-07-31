# This library is built based on ydata_quality: https://github.com/ydataai/ydata-quality
import pandas as pd 
import numpy as np
import traceback, sys
from ydata_quality.erroneous_data import ErroneousDataIdentifier
from ydata_quality.missings import MissingsProfiler
from ydata_quality.labelling import LabelInspector
from ydata_quality.duplicates import DuplicateChecker
from PIL import Image
import PIL, io
import utils

# Define metric names, return formats: dictionary {metric name} {sub-element}
# Return error/debugging
################################################ DATA QUALITY ########################################################




def eva_erronous(data, errors=None, ratio=False, sum=True):
    """
    Return number/percentage of error data
    data: numpy array or pandas data frame
    errors: list of item considered as error
    ratio: return percentage if set to True
    sum: sumarize the result if set to True, otherwise return errors following the categories in list of 'errors'
    """
    try:
        if utils.is_numpyarray(data):
            data = pd.DataFrame(data)
        if utils.is_pddataframe(data):
            if errors and isinstance(errors, list):
                eva_err =  ErroneousDataIdentifier(df=data,ed_extensions=errors) 
            else:
                eva_err = ErroneousDataIdentifier(df=data) 
            error_df = eva_err.predefined_erroneous_data()
            if ratio:
                total_count = data.count().to_numpy().flatten().sum()
                error_df.to_numpy().flatten().sum()
                error_df = 100*error_df/total_count
            if sum:
                error_df = error_df.to_numpy().flatten().sum()
            return error_df
        else:
            return {"Error": "Unsupported data: {}".format(type(data))}
    except Exception as e:
        print("[ERROR] - Error {} in eva_erronous: {}".format(type(e),e.__traceback__))
        traceback.print_exception(*sys.exc_info())

def eva_duplicate(data, ratio=False):
    """
    Return data/percentage of duplicate
    data: numpy array or pandas data frame
    ratio: return percentage if set to True
    """
    try:
        if utils.is_numpyarray(data):
            data = pd.DataFrame(data)
        if utils.is_pddataframe(data):
            dc = DuplicateChecker(df=data)
            result = dc.exact_duplicates()
            if ratio:
                result = {"duplicate": 100*len(result.index)/len(data.index)}
            return result
        else:
            return {"Error": "Unsupported data: {}".format(type(data))}
    except Exception as e:
        print("[ERROR] - Error {} in eva_duplicate: {}".format(type(e),e.__traceback__))
        traceback.print_exception(*sys.exc_info())

def eva_missing(data, null_count=True, correlations=False, predict=False, random_state=0):
    try:
        if utils.is_numpyarray(data):
            data = pd.DataFrame(data)
        if utils.is_pddataframe(data):
            mp = MissingsProfiler(df=data, random_state=random_state)
            results ={}
            if null_count:
                results["null_count"] = mp.null_count()
            if correlations:
                results["correlations"] = mp.missing_correlations()
            if predict:
                results["missing_prediction"]= mp.predict_missings()
            return results
        else:
            return {"Error":  "Unsupported data: {}".format(type(data))}
    except Exception as e:
        print("[ERROR] - Error {} in eva_erronous: {}".format(type(e),e.__traceback__))
        traceback.print_exception(*sys.exc_info())

class Outlier_Detector(object):
    def __init__(self, data):
        self.data = None
        self.update_data(data)
    
    def detect_outlier(self, n_data, labels=[], random_state=0, n=10, cluster=False):
        if utils.is_numpyarray(n_data):
            n_data = pd.DataFrame(n_data)
        if utils.is_pddataframe(n_data):
            if self.data is not None:
                data = None
                try:
                    data = pd.concat([self.data,n_data])
                except Exception as e:
                    print("[ERROR] - Error {} in concatenating data: {}".format(type(e),e.__traceback__))
                    traceback.print_exception(*sys.exc_info())
                if data is not None:
                    results = {}
                    for label in labels:
                        try:
                            li = LabelInspector(df=data, label=label, random_state=random_state)
                            results[label] = li.outlier_detection(th=n,use_clusters=cluster)
                        except Exception as e:
                            print("[ERROR] - Error {} in LabelInspector: {}".format(type(e),e.__traceback__))
                            traceback.print_exception(*sys.exc_info())
                    return results
                else: 
                    return {"Error": "Cannot concatenate data"}
            else:
                return {"Error": "Historical data has not been set"}
        else:
            return {"Error":  "Unsupported data: {}".format(type(data))}
    
    def update_data(self, data):
        if utils.is_numpyarray(data):
            data = pd.DataFrame(data)
        if utils.is_pddataframe(data):
            self.data = data
            return {"Response":  "Success"}
        else:
            return {"Error":  "Unsupported data: {}".format(type(data))}


def image_quality(image):
    quality = {}
    if isinstance(image,bytes):
        image = Image.open(io.BytesIO(image))
    if isinstance(image,np.ndarray):
        image = Image.fromarray(image)
    if isinstance(image,PIL.JpegImagePlugin.JpegImageFile) or isinstance(image,PIL.Image.Image):
        # print(dir(image))
        quality["image_quality"] = {}
        quality["image_quality"]["width"] = image.width
        quality["image_quality"]["height"] = image.height
        quality["image_quality"]["size"] = image.size
        quality["image_quality"]["mode"] = image.mode
        quality["image_quality"]["channel"] = len(image.getbands())
    return quality

def eva_none(data):
    try:
        if utils.is_pddataframe(data):
            data = data.to_numpy()
        if utils.is_numpyarray(data):
            valid_count = np.count_nonzero(~np.isnan(data))
            none_count = np.count_nonzero(np.isnan(data))
            return valid_count/(valid_count+none_count)
        else:
            return {"Error":  "Unsupported data: {}".format(type(data))}
    except Exception as e:
        print("[ERROR] - Error {} in eva_none: {}".format(type(e),e.__traceback__))
        traceback.print_exception(*sys.exc_info())
