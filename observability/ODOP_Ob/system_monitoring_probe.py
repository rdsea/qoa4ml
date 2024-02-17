from qoa4ml.qoaUtils import (
    get_sys_cpu_util,
    get_sys_mem,
    convert_to_gbyte,
    get_sys_mem,
    convert_to_mbyte,
    get_sys_cpu_metadata,
)

from qoa4ml.gpuUtils import (
    get_sys_gpu_metadata,
    get_sys_gpu_usage,
)

import json, time

from threading import Thread



class SysMonitoringProbe:
    def __init__(self, conf: dict) -> None:
        self.conf = conf
        # TODO: find somehow to get node name
        self.node_name = "aaltosea_test"
        self.frequency = self.conf["frequency"]
        if self.conf["requireRegister"]:
            self.obsServiceUrl = self.conf["obsServiceUrl"]
        self.cpuMetadata = self.getCpuMetadata()
        self.gpuMetadata = self.getGpuMetadata()
        self.memMetadata = self.getMemMetadata()
        self.currentReport = None
        self.started = False

    def getCpuMetadata(self):
        return get_sys_cpu_metadata()

    def getCpuUsage(self):
        report = get_sys_cpu_util()
        return {"value": report, "unit": "percentage"}

    def getGpuMetadata(self):
        report = get_sys_gpu_metadata()
        return report

    def getGpuUsage(self):
        report = get_sys_gpu_usage()
        return report

    def getMemMetadata(self):
        mem = get_sys_mem()
        return {"mem": {"capacity": convert_to_gbyte(mem["total"]), "unit": "Gb"}}

    def getMemUsage(self):
        mem = get_sys_mem()
        return {"value": convert_to_mbyte(mem["used"]), "unit": "Mb"}

    def register(self):
        import requests

        cpuMetadata = self.getCpuMetadata()
        gpuMetadata = self.getGpuMetadata()
        memMetadata = self.getMemMetadata()
        data = {
            "node_name": self.node_name,
            "metadata": {"cpu": cpuMetadata, "gpu": gpuMetadata, "mem": memMetadata},
        }
        response = requests.post(self.obsServiceUrl, json=data)
        if response.status_code == 200:
            registerInfo = json.loads(response.text)
            self.monitoringServiceUrl = registerInfo["reportUrl"]
            self.metrics = registerInfo["metrics"]
            self.frequency = registerInfo["frequency"]
        else:
            raise Exception(f"Can't register probe {self.node_name}")

    def createReport(self):
        timestamp = time.time()
        cpuUsage = self.getCpuUsage()
        gpuUsage = self.getGpuUsage()
        memUsage = self.getMemUsage()
        report = {
            "node_name": self.node_name,
            "timestamp": int(timestamp),
            "cpu": {"metadata": self.cpuMetadata, "usage": cpuUsage},
            "gpu": {"metadata": self.gpuMetadata, "usage": gpuUsage},
            "mem": {"metadata": self.memMetadata, "usage": memUsage},
        }
        self.currentReport = report
        print(f"Latency {(time.time() - timestamp)*1000}ms")

    def reporting(self):
        while self.started:
            self.createReport()
            time.sleep(1)

    def startReporting(self):
        self.started = True
        self.reportThread = Thread(target=self.reporting)
        self.reportThread.daemon = True
        self.reportThread.start()

    def stopReporting(self):
        self.started = False
        self.reportThread.join()


if __name__ == "__main__":
    conf = json.load(open("./probe_conf.json"))

    sysMonitoringProbe = SysMonitoringProbe(conf)
    while True:
        sysMonitoringProbe.createReport()
        time.sleep(1)
