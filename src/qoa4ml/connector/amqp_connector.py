import uuid
from typing import Optional

import pika

from ..config.configs import AMQPConnectorConfig
from .base_connector import BaseConnector


class AmqpConnector(BaseConnector):
    """
    AmqpConnector handles the connection to an AMQP server for sending messages.

    Parameters
    ----------
    config : AMQPConnectorConfig
        Configuration settings for the AMQP connector.
    log : bool, optional
        A flag to enable logging of messages, default is False.

    Attributes
    ----------
    conf : AMQPConnectorConfig
        The AMQP connector configuration.
    exchange_name : str
        The name of the exchange to connect to.
    exchange_type : str
        The type of the exchange (e.g., 'direct', 'topic').
    out_routing_key : str
        The routing key for outgoing messages.
    log_flag : bool
        Flag indicating whether to log messages.
    out_connection : pika.BlockingConnection
        The connection to the RabbitMQ server.
    out_channel : pika.channel.Channel
        The channel for communication with RabbitMQ.

    Methods
    -------
    send_report(body_message: str, corr_id: Optional[str] = None, routing_key: Optional[str] = None, expiration: int = 1000)
        Send data to the desired destination.
    get() -> AMQPConnectorConfig
        Get the current configuration of the connector.
    """

    def __init__(self, config: AMQPConnectorConfig, log: bool = False):
        """
        Initialize an instance of AmqpConnector.

        Parameters
        ----------
        config : AMQPConnectorConfig
            Configuration settings for the AMQP connector.
        log : bool, optional
            A flag to enable logging of messages, default is False.
        """
        self.conf = config
        self.exchange_name = config.exchange_name
        self.exchange_type = config.exchange_type
        self.out_routing_key = config.out_routing_key
        self.log_flag = log

        # Connect to RabbitMQ host
        if "amqps://" in config.end_point:
            self.out_connection = pika.BlockingConnection(
                pika.URLParameters(config.end_point)
            )
        else:
            self.out_connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=config.end_point)
            )

        # Create a channel
        self.out_channel = self.out_connection.channel()

        # Initialize an Exchange
        self.out_channel.exchange_declare(
            exchange=self.exchange_name, exchange_type=self.exchange_type
        )

    def send_report(
        self,
        body_message: str,
        corr_id: Optional[str] = None,
        routing_key: Optional[str] = None,
        expiration: int = 1000,
    ) -> None:
        """
        Send data to the desired destination.

        Parameters
        ----------
        body_message : str
            The message body to be sent.
        corr_id : str, optional
            The correlation ID for the message, default is None.
        routing_key : str, optional
            The routing key for the message, default is None.
        expiration : int, optional
            Message expiration time in milliseconds, default is 1000.

        Notes
        -----
        - If `corr_id` is not provided, a new UUID will be generated.
        - If `routing_key` is not provided, the default `out_routing_key` will be used.
        """
        if corr_id is None:
            corr_id = str(uuid.uuid4())
        if routing_key is None:
            routing_key = self.out_routing_key
        self.sub_properties = pika.BasicProperties(
            correlation_id=corr_id, expiration=str(expiration)
        )
        self.out_channel.basic_publish(
            exchange=self.exchange_name,
            routing_key=routing_key,
            properties=self.sub_properties,
            body=body_message,
        )

    def get(self) -> AMQPConnectorConfig:
        """
        Get the current configuration of the connector.

        Returns
        -------
        AMQPConnectorConfig
            The AMQP connector configuration.
        """
        return self.conf
