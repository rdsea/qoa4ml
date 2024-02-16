from qoa4ml import qoaUtils
from tinydb import TinyDB
import psutil
import requests, json, time
#import shelve
import threading


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
        #self.db = shelve.open("./logs/test_shelf.db")

    def getCpuMetadata(self):
        cpu_freq = psutil.cpu_freq()
        frequency = {"value": cpu_freq.max / 1000, "unit": "GHz"}
        cpu_threads = psutil.cpu_count(logical=True)

        return {"frequency": frequency, "thread": cpu_threads}

    def getCpuUsage(self):
        report = qoaUtils.get_sys_cpu_util()
        return {"value": report, "unit": "percentage"}

    def getGpuMetadata(self):
        report = qoaUtils.get_sys_gpu_metadata()
        return report

    def getGpuUsage(self):
        report = qoaUtils.get_sys_gpu_usage()
        return report

    def getMemMetadata(self):
        mem = qoaUtils.get_sys_mem()
        return {
            "mem": {"capacity": qoaUtils.convert_to_gbyte(mem["total"]), "unit": "Gb"}
        }

    def getMemUsage(self):
        mem = qoaUtils.get_sys_mem()
        return {"value": qoaUtils.convert_to_mbyte(mem["used"]), "unit": "Mb"}

    def register(self):
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
    
    def writeToDb(self, report: dict, timestamp: int): 
    #self.db[str(timestamp)] = report
        pass

    def createReport(self):
        timestamp = time.time()
        cpuUsage = self.getCpuUsage()
        gpuUsage = self.getGpuUsage()
        memUsage = self.getMemUsage()
        report = {
            "node_name": self.node_name,
            "cpu": {"metadata": self.cpuMetadata, "usage": cpuUsage},
            "gpu": {"metadata": self.gpuMetadata, "usage": gpuUsage},
            "mem": {"metadata": self.memMetadata, "usage": memUsage},
        }
        self.writeToDb(report, int(timestamp))
        print(f"Latency {(time.time() - timestamp)*1000}")

    def reporting(self):
        while True:
            self.createReport()
            time.sleep(1)

    def startReporting(self):
        self.reportThread = threading.Thread(target=self.reporting)
        self.reportThread.start()

    def stopReporting(self):
        pass

    def truncateDb(self, timestampRange: range):
        #for timestamp in timestampRange:
        #    del self.db[str(timestamp)]
        pass

if __name__ == "__main__":
    conf = json.load(open("./probe_conf.json"))
    sysMonitoringProbe = SysMonitoringProbe(conf)
    sysMonitoringProbe.startReporting()

