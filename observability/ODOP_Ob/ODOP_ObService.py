from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel
import json
import os
import threading
import requests
import time
import uvicorn
import pymongo
app = FastAPI()


class Metadata(BaseModel):
    cpu: dict
    gpu: dict
    mem: dict


class ProbeMetaData(BaseModel):
    node_name: str
    metadata: Metadata


class ResourceUsage(BaseModel):
    node_name: str
    cpu: dict
    gpu: dict
    mem: dict




class ODOPObsService:
    def __init__(self, filePath: str = "./Obs_Service_conf.json") -> None:
        self.filePath = filePath
        self.router = APIRouter()

        if os.path.exists(self.filePath):
            file = open(self.filePath)
            self.obsServiceConf = json.load(file)
            self.obsServiceUrl = self.obsServiceConf["ObsServiceUrl"]
            self.subscribeToMonitoringService(
                self.obsServiceConf["monitoring_service"]["subscribeUrl"]
            )
            self.db_config = self.obsServiceConf["database"]
            self.mongo_client = pymongo.MongoClient(self.db_config["url"], tls=True, tlsCertificateKeyFile=self.db_config["certificatePath"])
            self.db = self.mongo_client[self.db_config["db_name"]]
            self.collection = self.db[self.db_config["collection"]]
        else:
            raise Exception("No Monitoring Service Config")
        self.router.add_api_route("/register", self.register, methods=["POST"])

        self.collection.drop()

    def subscribeToMonitoringService(self, url: str):
        response = requests.post(url, json={"url": self.obsServiceUrl})
        if response.status_code == 200:
            print("Ok")
            return True
        return False

    def saveProbeMetaData(self, metadata: ProbeMetaData):
        try:
            self.collection.insert_one(metadata.dict())
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def register(self, probeMetaData: ProbeMetaData):
        try:
            self.saveProbeMetaData(probeMetaData)
            return self.obsServiceConf["monitoring_service"]
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    def reset_db(self):
        self.collection.drop()


@app.post("/metric")
async def metric(resourceUsage: ResourceUsage):
    try:
        print(resourceUsage)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    odopObsService = ODOPObsService()
    app.include_router(odopObsService.router)
    uvicorn.run(app, host="localhost", port=8000)
