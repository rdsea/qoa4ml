import json

from devtools import debug

from ..config.configs import DebugConnectorConfig
from .base_connector import BaseConnector


class DebugConnector(BaseConnector):
    def __init__(self, config: DebugConnectorConfig):
        self.silence = config.silence

    def send_report(self, body_message: str):
        if not self.silence:
            debug(json.loads(body_message))
