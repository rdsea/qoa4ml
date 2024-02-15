from qoa4ml import qoaUtils
import psutil
import requests, json, time


class SysMonitoringProbe:
    def __init__(self, **kwargs) -> None:
        self.conf = kwargs
        # TODO: find somehow to get node name
        self.node_name = "aaltosea_test"
        self.obsServiceUrl = "http://localhost:8000/register"
        self.isRegisted = False

    def getCpuMetadata(self):
        cpu_freq = psutil.cpu_freq()
        frequency = {"value": cpu_freq.max / 1000, "unit": "GHz"}
        cpu_threads = psutil.cpu_count(logical=True)

        return {"frequency": frequency, "thread": cpu_threads}

    def getCpuUsage(self):
        report = qoaUtils.get_sys_cpu_util()

        return {"usage": report, "unit": "percentage"}

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
        return {
            "usage": {"value": qoaUtils.convert_to_mbyte(mem["used"]), "unit": "Mb"}
        }

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

    def report(self):
        cpuUsage = self.getCpuUsage()
        gpuUsage = self.getGpuUsage()
        memUsage = self.getMemUsage()
        report = {
            "node_name": self.node_name,
            "cpu": cpuUsage,
            "gpu": {"usage": gpuUsage},
            "mem": memUsage,
        }
        response = requests.post(self.monitoringServiceUrl, json=report)


if __name__ == "__main__":
    sysMonitoringProbe = SysMonitoringProbe()
    sysMonitoringProbe.register()
    i = 0
    while True:
        sysMonitoringProbe.report()
        time.sleep(1 / sysMonitoringProbe.frequency)
        i = i + 1
