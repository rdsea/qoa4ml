from ml_report import *

execution_graph_data = {
    "instances": {
        "5e4f82e8-f2ff-45a8-8809-140f98253e4d": {
            "instance_name": "Inference Jet 05",
            "method": "Max Aggregate",
            "previous_instance": [
                "78c2f055-721b-4867-85ff-f90494b5dd7b",
                "8ae48ecc-b2f0-482f-9845-a03ab05764cb",
            ],
        },
        "78c2f055-721b-4867-85ff-f90494b5dd7b": {
            "instance_name": "Inference Jet 03",
            "method": "TensorFlow",
            "previous_instance": ["22e0af69-3fe2-4451-9d63-b3f627e3a676"],
        },
        "22e0af69-3fe2-4451-9d63-b3f627e3a676": {
            "instance_name": "data processing Raps 02",
            "method": "Transformation",
            "previous_instance": ["40a7fd9b-84cb-4c4f-9531-af91c05b9f77"],
        },
        "40a7fd9b-84cb-4c4f-9531-af91c05b9f77": {
            "instance_name": "data handling01 Raps",
            "method": "REST",
            "previous_instance": [],
        },
        "8ae48ecc-b2f0-482f-9845-a03ab05764cb": {
            "instance_name": "Inference Jet 04",
            "method": "TensorFlow",
            "previous_instance": ["22e0af69-3fe2-4451-9d63-b3f627e3a676"],
        },
    },
    "last_instance": "5e4f82e8-f2ff-45a8-8809-140f98253e4d",
}


computation_graph = ComputationGraph.parse_obj(execution_graph_data)


service_quality = ServiceQuality(
    stage_reports=[
        StageReport(
            stage_name="MLInference Aggregate",
            metric_reports=[
                MetricReport(
                    metric_name="Response Time",
                    value=[
                        InstanceReport(
                            instance_id="5e4f82e8-f2ff-45a8-8809-140f98253e4d",
                            value={
                                "start_time": 1684746282.947917,
                                "response_time": 0.20208120346069336,
                            },
                        ),
                    ],
                ),
                MetricReport(
                    metric_name="metric15",
                    value=[
                        InstanceReport(
                            instance_id="5e4f82e8-f2ff-45a8-8809-140f98253e4d",
                            value=4345,
                        ),
                    ],
                ),
            ],
        ),
        StageReport(
            stage_name="MLInference Ensemble",
            metric_reports=[
                MetricReport(
                    metric_name="Response Time",
                    value=[
                        InstanceReport(
                            instance_id="78c2f055-721b-4867-85ff-f90494b5dd7b",
                            value={
                                "start_time": 1684746282.947917,
                                "response_time": 0.20208120346069336,
                            },
                        ),
                        InstanceReport(
                            instance_id="8ae48ecc-b2f0-482f-9845-a03ab05764cb",
                            value={
                                "start_time": 1684746282.663837,
                                "response_time": 0.20443487167358398,
                            },
                        ),
                    ],
                ),
                MetricReport(
                    metric_name="metric1",
                    value=[
                        InstanceReport(
                            instance_id="78c2f055-721b-4867-85ff-f90494b5dd7b",
                            value=56,
                        ),
                        InstanceReport(
                            instance_id="8ae48ecc-b2f0-482f-9845-a03ab05764cb",
                            value=342,
                        ),
                    ],
                ),
            ],
        ),
        StageReport(
            stage_name="DataProcessing",
            metric_reports=[
                MetricReport(
                    metric_name="Response Time",
                    value=[
                        InstanceReport(
                            instance_id="22e0af69-3fe2-4451-9d63-b3f627e3a676",
                            value={
                                "start_time": 1684746282.105319,
                                "response_time": 0.2010021209716797,
                            },
                        ),
                    ],
                ),
                MetricReport(
                    metric_name="metric1",
                    value=[
                        InstanceReport(
                            instance_id="22e0af69-3fe2-4451-9d63-b3f627e3a676",
                            value=56,
                        ),
                    ],
                ),
                MetricReport(
                    metric_name="metric2",
                    value=[
                        InstanceReport(
                            instance_id="22e0af69-3fe2-4451-9d63-b3f627e3a676",
                            value=34,
                        ),
                    ],
                ),
            ],
        ),
        StageReport(
            stage_name="Gateway",
            metric_reports=[
                MetricReport(
                    metric_name="Response Time",
                    value=[
                        InstanceReport(
                            instance_id="40a7fd9b-84cb-4c4f-9531-af91c05b9f77",
                            value={
                                "start_time": 1684746281.902005,
                                "response_time": 0.10008597373962402,
                            },
                        ),
                    ],
                ),
                MetricReport(
                    metric_name="metric1",
                    value=[
                        InstanceReport(
                            instance_id="40a7fd9b-84cb-4c4f-9531-af91c05b9f77",
                            value=10,
                        ),
                    ],
                ),
            ],
        ),
    ]
)

data_quality = DataQuality(
    stage_reports=[
        StageReport(
            stage_name="MLInference Aggregate",
            metric_reports=[
                MetricReport(
                    metric_name="object_height2",
                    value=[
                        InstanceReport(
                            instance_id="5e4f82e8-f2ff-45a8-8809-140f98253e4d",
                            value=345,
                        ),
                    ],
                ),
            ],
        ),
        StageReport(
            stage_name="MLInference Ensemble",
            metric_reports=[
                MetricReport(
                    metric_name="object_height",
                    value=[
                        InstanceReport(
                            instance_id="78c2f055-721b-4867-85ff-f90494b5dd7b",
                            value=52,
                        ),
                    ],
                ),
                MetricReport(
                    metric_name="object_height3",
                    value=[
                        InstanceReport(
                            instance_id="8ae48ecc-b2f0-482f-9845-a03ab05764cb",
                            value=654,
                        ),
                    ],
                ),
            ],
        ),
        StageReport(
            stage_name="DataProcessing",
            metric_reports=[
                MetricReport(
                    metric_name="image_width",
                    value=[
                        InstanceReport(
                            instance_id="22e0af69-3fe2-4451-9d63-b3f627e3a676",
                            value=100,
                        ),
                    ],
                ),
                MetricReport(
                    metric_name="image_height",
                    value=[
                        InstanceReport(
                            instance_id="22e0af69-3fe2-4451-9d63-b3f627e3a676",
                            value=242,
                        ),
                    ],
                ),
                MetricReport(
                    metric_name="object_width",
                    value=[
                        InstanceReport(
                            instance_id="22e0af69-3fe2-4451-9d63-b3f627e3a676",
                            value=40,
                        ),
                    ],
                ),
                MetricReport(
                    metric_name="object_height",
                    value=[
                        InstanceReport(
                            instance_id="22e0af69-3fe2-4451-9d63-b3f627e3a676",
                            value=52,
                        ),
                    ],
                ),
            ],
        ),
        StageReport(
            stage_name="Gateway",
            metric_reports=[
                MetricReport(
                    metric_name="image_width",
                    value=[
                        InstanceReport(
                            instance_id="40a7fd9b-84cb-4c4f-9531-af91c05b9f77",
                            value=20,
                        ),
                    ],
                ),
                MetricReport(
                    metric_name="image_height",
                    value=[
                        InstanceReport(
                            instance_id="40a7fd9b-84cb-4c4f-9531-af91c05b9f77",
                            value=42,
                        ),
                    ],
                ),
            ],
        ),
    ]
)

inference_quality = MlSpecificQuality(
    inference_reports=[
        InferenceReport(
            inference_id="5595ed89-41c5-4a0c-b18e-85a0aab912fa", value={"cat": 345}
        )
    ]
)
# with open("data_quality.json", "w") as file:
#    json.dump(data_quality.model_dump(), file)
