from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
import threading
import requests
import time

app = FastAPI()


class ODOPObsService:
    def __init__(
        self, system_monitoring_probe_conf: dict, process_monitoring_probe_conf: dict
    ) -> None:
        self.router = APIRouter()
        sef


odopObsService = ODOPObsService()
app.include_router(odopObsService.router)
