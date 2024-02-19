from fastapi import APIRouter, FastAPI, HTTPException, status
from pydantic import BaseModel
import json
import os
import threading
import requests
import time

app = FastAPI()

class ProcessReport(BaseModel):
    metadata: dict 
    timestamp: int
    usage: dict 

class NodeReport(BaseModel): 
    node_name: str
    timestamp: int 
    cpu: dict 
    gpu: dict 
    mem: dict

@app.post("/metrics/process", status_code=status.HTTP_200_OK)
async def metric_process(report: ProcessReport):
    try:
        print(report)
        return "Received"
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/metrics/node", status_code=status.HTTP_200_OK)
async def metric_node(report: NodeReport):
    try:
        print(report)
        return "Received"
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
