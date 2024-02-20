import re
from fastapi import APIRouter, FastAPI, HTTPException, status
from pydantic import BaseModel
import json
import os
import threading
import requests
import time
from tinyflux import TinyFlux, Point
from datetime import datetime

app = FastAPI()


class ProcessReport(BaseModel):
    metadata: dict
    timestamp: int
    cpu_usage: dict
    mem_usage: dict


class SystemReport(BaseModel):
    node_name: str
    timestamp: int
    cpu_usage: dict
    gpu_usage: dict
    mem_usage: dict


class NodeExporter:
    def __init__(self, config: dict) -> None:
        self.config = config
        if "subscribed_consumer" in self.config:
            self.subscribed_consumer = self.config["subscribed_consumer"]
        else:
            self.subscribed_consumer = []
        self.db = TinyFlux("./db.csv")

        self.router = APIRouter() 
        self.router.add_api_route(
            "/metrics/process", self.metric_process, methods=["POST"]
        )
        self.router.add_api_route("/metrics/system", self.metric_system, methods=["POST"])

    def insert_metric(self, timestamp: int, tags: dict, fields: dict):
        datapoint = Point(
            time=datetime.fromtimestamp(timestamp), tags=tags, fields=fields
        )
        self.db.insert(datapoint)

    def query_all_metric(self):
        return self.db.all()

    def metric_process(self, report: ProcessReport):
        try:
            fields = {
                **report.cpu_usage, 
                **report.mem_usage
            }
            self.insert_metric(report.timestamp, report.metadata, fields)
            return "Received"
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def metric_system(self, report: SystemReport):
        try:
            fields = {
                **report.cpu_usage, 
                **report.gpu_usage, 
                **report.mem_usage
            }
            self.insert_metric(report.timestamp, {"node_name": report.node_name}, fields)
            return "Received"
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))


node_exporter = NodeExporter({})
app.include_router(node_exporter.router)
