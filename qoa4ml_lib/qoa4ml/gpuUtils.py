from .pynvml_forked import nvmlDeviceGetCount, nvmlDeviceGetHandleByIndex, nvmlInit, \
    nvmlDeviceGetUtilizationRates, nvmlDeviceGetMemoryInfo, nvmlDeviceGetNumGpuCores, nvmlDeviceGetMaxClockInfo

HAS_NVIDIA_GPU = True
try: 
    nvmlInit()
except: 
    HAS_NVIDIA_GPU = False

def get_sys_gpu_usage():
    usage = {} 
    if not HAS_NVIDIA_GPU: 
        return {}
    deviceCount = nvmlDeviceGetCount()
    
    for i in range(deviceCount):
        handle = nvmlDeviceGetHandleByIndex(i)
        util = nvmlDeviceGetUtilizationRates(handle)
        mem = nvmlDeviceGetMemoryInfo(handle) 
        usage[f"device_{i+1}_core"] = util.gpu
        usage[f"device_{i+1}_mem"] = mem.used/1024./1024
    return usage

def get_sys_gpu_metadata():
    metadata = {}
    if not HAS_NVIDIA_GPU: 
        return {}
    deviceCount = nvmlDeviceGetCount()

    for i in range(deviceCount):
        handle = nvmlDeviceGetHandleByIndex(i)
        cores = nvmlDeviceGetNumGpuCores(handle)
        clock = nvmlDeviceGetMaxClockInfo(handle, 0)
        mem = nvmlDeviceGetMemoryInfo(handle)
        metadata[f"device_{i+1}"] = {
            "frequency": {
                "value": clock,
                "unit": "MHz"
            },
            "core": cores,
            "mem": {
                "capacity": mem.total/1024./1024,
                "unit": "Gb"
            }
        }
    return metadata
