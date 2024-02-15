from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn, requests

app = FastAPI()

obsServiceSubscribed = False
obsServiceUrl = None


class ProbeReport(BaseModel):
    node_name: str
    cpu: dict
    gpu: dict
    mem: dict


class ServiceUrl(BaseModel):
    url: str


@app.post("/report")
async def report(probeReport: ProbeReport):
    global obsServiceUrl
    global obsServiceSubscribed
    try:
        if obsServiceSubscribed and obsServiceUrl:
            response = requests.post(obsServiceUrl, json=dict(probeReport))
        else:
            print("Nothing subscribed yet")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/subscribe")
async def subscribe(serviceUrl: ServiceUrl):
    global obsServiceUrl
    global obsServiceSubscribed
    try:
        obsServiceSubscribed = True
        obsServiceUrl = serviceUrl.url
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


if __name__ == "__main__":
    # start_subscription()

    uvicorn.run(app, host="localhost", port=8001) 
    uvicorn.run("CSC_monitoring_service:app", host="localhost", port=8001, reload=True)
