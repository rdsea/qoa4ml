import os
import logging
from pydantic import BaseModel

ODOP_PATH = os.getenv("ODOP_PATH")
if not ODOP_PATH:
    logging.error("No ODOP_PATH environment variable")


class ProcessReport(BaseModel):
    metadata: dict
    timestamp: float
    usage: dict


class SystemReport(BaseModel):
    node_name: str
    timestamp: float
    cpu: dict
    gpu: dict
    mem: dict
