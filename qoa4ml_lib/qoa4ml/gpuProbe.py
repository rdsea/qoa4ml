from pynvml import nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex, nvmlInit, \
nvmlShutdown, nvmlDeviceGetUtilizationRates, nvmlDeviceGetMemoryInfo, nvmlDeviceGetNumGpuCores, nvmlDeviceGetMaxClockInfo
from qoa4ml.qoaUtils import convert_to_mbyte, convert_to_gbyte

def get_sys_gpu():
    metadata = {}
    usage = {}
    
    nvmlInit()
    deviceCount = nvmlDeviceGetCount()
    
    for i in range(deviceCount):
        handle = nvmlDeviceGetHandleByIndex(i)
        util = nvmlDeviceGetUtilizationRates(handle)
        mem = nvmlDeviceGetMemoryInfo(handle)
        cores = nvmlDeviceGetNumGpuCores(handle)
        clock = nvmlDeviceGetMaxClockInfo(handle, 0)
        
        metadata[f"device_{i+1}"] = {
            "frequency": {
                "value": clock,
                "unit": "MHz"
            },
            "core": cores,
            "mem": {
                "capacity": convert_to_gbyte(mem.total),
                "unit": "Gb"
            }
        }
        
        usage[f"device_{i+1}"] = {
            "core": {
                "value": util.gpu,
                "unit": "percentage"
            },
            "mem": {
                "value": convert_to_mbyte(mem.used),
                "unit": "Mb"
            }
        }
    
    nvmlShutdown()
    
    return {"metadata": metadata, "usage": usage}

print(get_sys_gpu())
