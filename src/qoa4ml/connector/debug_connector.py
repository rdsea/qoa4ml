import json

from devtools import debug

from ..config.configs import DebugConnectorConfig
from .base_connector import BaseConnector


class DebugConnector(BaseConnector):
    """
    DebugConnector provides a connector for debugging purposes, enabling the logging of messages.

    Parameters
    ----------
    config : DebugConnectorConfig
        Configuration settings for the debug connector.

    Attributes
    ----------
    silence : bool
        Flag to suppress debugging output if set to True.

    Methods
    -------
    send_report(body_message: str) -> None
        Send and debug the message.
    """

    def __init__(self, config: DebugConnectorConfig):
        """
        Initialize an instance of DebugConnector.

        Parameters
        ----------
        config : DebugConnectorConfig
            Configuration settings for the debug connector.
        """
        self.silence = config.silence

    def send_report(self, body_message: str) -> None:
        """
        Send and debug the message.

        Parameters
        ----------
        body_message : str
            The message body to be sent and debugged.

        Notes
        -----
        If `silence` is set to False, the message will be logged for debugging purposes.
        """
        if not self.silence:
            debug(json.loads(body_message))

    def check_connection(self) -> bool:
        return True
