from common_models import Metric
from datamodel_enum import (DataQualityEnum, ServiceMetricNameEnum,
                            StageNameEnum)
from ml_report import (ExecutionGraph, InferenceGraph, InferenceInstance,
                       StageReport)

service_quality = [
    StageReport(
        id="ml_inference_aggregate_id",
        name=StageNameEnum.ml_inference_aggregate,
        metric=[
            Metric(
                metric_name=ServiceMetricNameEnum.response_time,
                records=[
                    {
                        "5e4f82e8-f2ff-45a8-8809-140f98253e4d": {
                            "start_time": 1684746282.947917,
                            "response_time": 0.20208120346069336,
                        }
                    }
                ],
            ),
        ],
    ),
    StageReport(
        id="ml_inference_ensemble",
        name=StageNameEnum.ml_inference_ensemble,
        metric=[
            Metric(
                metric_name=ServiceMetricNameEnum.response_time,
                records=[
                    {
                        "78c2f055-721b-4867-85ff-f90494b5dd7b": {
                            "start_time": 1684746282.383123,
                            "response_time": 0.20420598983764648,
                        },
                        "8ae48ecc-b2f0-482f-9845-a03ab05764cb": {
                            "start_time": 1684746282.663837,
                            "response_time": 0.20443487167358398,
                        },
                    }
                ],
            ),
        ],
    ),
    StageReport(
        id="data_processing_id",
        name=StageNameEnum.data_processing,
        metric=[
            Metric(
                metric_name=ServiceMetricNameEnum.response_time,
                records=[
                    {
                        "22e0af69-3fe2-4451-9d63-b3f627e3a676": {
                            "start_time": 1684746282.105319,
                            "response_time": 0.2010021209716797,
                        }
                    }
                ],
            ),
        ],
    ),
    StageReport(
        id="gate_way_id",
        name=StageNameEnum.gate_way,
        metric=[
            Metric(
                metric_name=ServiceMetricNameEnum.response_time,
                records=[
                    {
                        "40a7fd9b-84cb-4c4f-9531-af91c05b9f77": {
                            "start_time": 1684746281.902005,
                            "response_time": 0.10008597373962402,
                        }
                    }
                ],
            ),
        ],
    ),
]

data_quality = [
    StageReport(
        id="ml_inference_aggregate_id",
        name=StageNameEnum.ml_inference_aggregate,
        metric=[
            Metric(
                metric_name=DataQualityEnum.object_size,
                records=[{"5e4f82e8-f2ff-45a8-8809-140f98253e4d": (345, 123)}],
            ),
        ],
    ),
    StageReport(
        id="ml_inference_ensemble",
        name=StageNameEnum.ml_inference_ensemble,
        metric=[
            Metric(
                metric_name=DataQualityEnum.object_size,
                records=[
                    {
                        "78c2f055-721b-4867-85ff-f90494b5dd7b": (52, 123),
                        "8ae48ecc-b2f0-482f-9845-a03ab05764cb": (123, 123),
                    }
                ],
            ),
        ],
    ),
    StageReport(
        id="data_processing_id",
        name=StageNameEnum.data_processing,
        metric=[
            Metric(
                metric_name=DataQualityEnum.image_size,
                records=[{"22e0af69-3fe2-4451-9d63-b3f627e3a676": (100, 242)}],
            ),
            Metric(
                metric_name=DataQualityEnum.object_size,
                records=[{"22e0af69-3fe2-4451-9d63-b3f627e3a676": (40, 52)}],
            ),
        ],
    ),
    StageReport(
        id="gate_way_id",
        name=StageNameEnum.gate_way,
        metric=[
            Metric(
                metric_name=DataQualityEnum.image_size,
                records=[{"40a7fd9b-84cb-4c4f-9531-af91c05b9f77": (20, 42)}],
            ),
        ],
    ),
]
