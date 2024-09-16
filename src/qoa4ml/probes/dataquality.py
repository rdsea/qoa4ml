# This library is built based on ydata_quality: https://github.com/ydataai/ydata-quality

import io

import numpy as np
import pandas as pd
from PIL import Image

from ..lang.datamodel_enum import DataQualityNameEnum, ImageQualityNameEnum
from ..utils.logger import qoa_logger


def image_quality(input_image: bytes | np.ndarray):
    quality = {}
    if isinstance(input_image, bytes):
        image = Image.open(io.BytesIO(input_image))
    elif isinstance(input_image, np.ndarray):
        image = Image.fromarray(input_image)
    quality[ImageQualityNameEnum.image_size] = image.size
    quality[ImageQualityNameEnum.color_mode] = image.mode
    quality[ImageQualityNameEnum.color_channel] = len(image.getbands())
    return quality


def eva_erronous(data, errors=None):
    """
    Return number/percentage of error data
    data: numpy array or pandas data frame
    errors: list of items considered as errors
    ratio: return percentage if set to True
    sum: sum the result if set to True, otherwise return errors following the categories in list of 'errors'
    """
    try:
        if isinstance(data, np.ndarray):
            data = pd.DataFrame(data)

        if isinstance(data, pd.DataFrame):
            if errors and isinstance(errors, list):
                error_mask = data.isin(errors)
            else:
                error_mask = data.isna()

            total_errors = error_mask.sum().sum()
            total_count = data.count().sum()

            results = {
                DataQualityNameEnum.total_errors: total_errors,
                DataQualityNameEnum.error_ratios: 100 * total_errors / total_count
                if total_count > 0
                else np.nan,
            }
            return results
        else:
            qoa_logger.warning(f"Unsupported data: {type(data)}")
            return None
    except Exception as e:
        qoa_logger.exception(f"Error {type(e)} in eva_erronous")
        return None


#
#
def eva_duplicate(data):
    """
    Return data/percentage of duplicates
    data: numpy array or pandas data frame
    ratio: return percentage if set to True
    """
    try:
        if isinstance(data, np.ndarray):
            data = pd.DataFrame(data)

        if isinstance(data, pd.DataFrame):
            duplicate_mask = data.duplicated(keep=False)
            duplicate_data = data[duplicate_mask]

            results = {
                DataQualityNameEnum.duplicate_ratio: 100
                * duplicate_data.shape[0]
                / data.shape[0],
                DataQualityNameEnum.total_duplicate: duplicate_data.shape[0],
            }
            return results
        else:
            qoa_logger.warning(f"Unsupported data: {type(data)}")
            return None
    except Exception as e:
        qoa_logger.exception(f"Error {type(e)} in eva_duplicate")
        return None


def eva_missing(data, null_count=True, correlations=False, predict=False):
    try:
        if isinstance(data, np.ndarray):
            data = pd.DataFrame(data)
        if isinstance(data, pd.DataFrame):
            results = {}
            if null_count:
                count = data.isnull().sum()
                results[DataQualityNameEnum.null_count] = count

            if correlations:
                nulls = data.loc[:, results["null_count"] > 0]
                results[DataQualityNameEnum.null_correlations] = nulls.isnull().corr()

            if predict:
                raise RuntimeWarning("Predict is enabled but not implemented yet")
                # results["missing_prediction"] = mp.predict_missings()

            return results
        else:
            qoa_logger.warning(f"Unsupported data: {type(data)}")
            return None
    except Exception as e:
        qoa_logger.exception(f"Error {type(e)} in eva_erronous")


def eva_none(data):
    try:
        if isinstance(data, pd.DataFrame):
            data = data.to_numpy()
        if isinstance(data, np.ndarray):
            valid_count = np.count_nonzero(~np.isnan(data))
            none_count = np.count_nonzero(np.isnan(data))
            results = {}
            results[DataQualityNameEnum.total_valid] = valid_count
            results[DataQualityNameEnum.total_none] = none_count
            results[DataQualityNameEnum.none_ratio] = valid_count / (
                valid_count + none_count
            )
            return results
        else:
            qoa_logger.warning(f"Unsupported data: {type(data)}")
            return None
    except Exception as e:
        qoa_logger.exception(f"Error {type(e)} in eva_none")


#
#
# class OutlierDetector:
#     def __init__(self, data):
#         self.data = None
#         self.update_data(data)
#
#     def detect_outlier(self, n_data, labels=None, random_state=0, n=10, cluster=False):
#         if labels is None:
#             labels = []
#         if is_numpyarray(n_data):
#             n_data = pd.DataFrame(n_data)
#         if is_pddataframe(n_data):
#             if self.data is not None:
#                 data = None
#                 try:
#                     data = pd.concat([self.data, n_data])
#                 except Exception as e:
#                     qoa_logger.error(
#                         f"Error {type(e)} in concatenating data: {e.__traceback__}"
#                     )
#                     traceback.print_exception(*sys.exc_info())
#                 if data is not None:
#                     results = {}
#                     for label in labels:
#                         try:
#                             if "LabelInspector" not in globals():
#                                 global LabelInspector
#                                 from ydata_quality.labelling import LabelInspector
#                             li = LabelInspector(
#                                 df=data, label=label, random_state=random_state
#                             )
#                             results[label] = li.outlier_detection(
#                                 th=n, use_clusters=cluster
#                             )
#                         except Exception as e:
#                             qoa_logger.error(
#                                 f"Error {type(e)} in LabelInspector: {e.__traceback__}"
#                             )
#                             traceback.print_exception(*sys.exc_info())
#                     return results
#                 else:
#                     return {"Error": "Cannot concatenate data"}
#             else:
#                 return {"Error": "Historical data has not been set"}
#         else:
#             return {"Error": f"Unsupported data: {type(data)}"}
#
#     def update_data(self, data):
#         if is_numpyarray(data):
#             data = pd.DataFrame(data)
#         if is_pddataframe(data):
#             self.data = data
#             return {"Response": "Success"}
#         else:
#             return {"Error": f"Unsupported data: {type(data)}"}
