from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
import threading
import requests
import time
import uvicorn

app = FastAPI()

filePath = "./monitoring_service.json"
ObsServiceUrl = "http://localhost:8000/metric"


class Metadata(BaseModel):
    cpu: dict
    gpu: dict
    mem: dict


class Item(BaseModel):
    node_name: str
    metadata: Metadata


class ResourceUsage(BaseModel):
    node_name: str
    cpu: dict
    gpu: dict
    mem: dict


def saveProbeMetaData(metadata: Metadata):
    # TODO: save probe metadata to database
    pass


def subscribeToMonitoringService(url: str):
    response = requests.post(url, json={"url": ObsServiceUrl})
    if response.status_code == 200:
        print("Ok")
        return True
    return False


@app.post("/register")
async def register(item: Item):
    try:
        saveProbeMetaData(item.metadata)
        return monitoringServiceConfig
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/metric")
async def metric(resourceUsage: ResourceUsage):
    try:
        print(resourceUsage)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    if os.path.exists(filePath):
        file = open(filePath)
        monitoringServiceConfig = json.load(file)
        subscribeToMonitoringService(
            monitoringServiceConfig["monitoring_service"]["subscribeUrl"]
        )
    else:
        raise Exception("No Monitoring Service Config")

    # start_subscription()

    uvicorn.run(app, host="localhost", port=8000)
