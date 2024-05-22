import time

from PIL import Image

from qoa4ml.datamodels.datamodel_enum import MetricNameEnum
from qoa4ml.qoa_client import QoaClient

qoa_client1 = QoaClient(config_path="./data/data_processing_client_config.json")
image = Image.open("./data/test_image.jpg")
while True:
    qoa_client1.timer()
    qoa_client1.report(submit=True)
    time.sleep(1)
