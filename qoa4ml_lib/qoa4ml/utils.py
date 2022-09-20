from concurrent.futures import thread
from email.policy import default
import json, psutil, time, os, docker
from qoa4ml.reports import Qoa_Client
from threading import Thread

default_sys_metric = {
    "cpu_stat":{
        "cpu":{
            "class": "Gauge",
            "description": "monitor system cpu times",
            "default": -1,
            "key": "cpu time"
        }
    },
    "mem_stat":{
        "memory": {
            "class": "Gauge",
            "description": "monitor system memory used",
            "default": - 0,
            "key": "used"
        }
    }
}
default_proc_metric = {
    "proc_cpu":{
        "cpu":{
            "class": "Gauge",
            "description": "monitor system cpu times",
            "default": -1,
            "key": "cpu time"
        }
    },
    "proc_mem":{
        "memory": {
            "class": "Gauge",
            "description": "monitor system memory used",
            "default": - 0,
            "key": "used"
        }
    }
}
default_docker_metric = {
    "dock_cpu_percentage":{
        "class": "Gauge",
        "description": "monitor system cpu percentage",
        "default": -1,
        "key": "percentage"
    },
    "docker_memory_used": {
        "class": "Gauge",
        "description": "monitor system memory used",
        "default": - 0,
        "key": "used"
    }
}

def load_config(file_path:str)->dict:
    """
    file_path: file path to load config
    """
    with open(file_path, "r") as f:
        return json.load(f)

def to_json(file_path:str, conf:dict):
    """
    file_path: file path to save config
    """
    with open(file_path, "w") as f:
        json.dump(conf, f)
    
def get_cpu(key:str = None):
    if key == "cpu time":
        return psutil.cpu_times().user
    if key == "percentage":
        pass
    return psutil.cpu_percent()

def get_mem(key:str = None):
    if key == "percentage":
        return psutil.virtual_memory().percent
    if key == "free":
        return psutil.virtual_memory().free
    if key == "total":
        return psutil.virtual_memory().total
    if key == "active":
        return psutil.virtual_memory().active
    if key == "available":
        return psutil.virtual_memory().available
    if key == "used":
        pass
    return psutil.virtual_memory().used

def get_proc_cpu(pid = None):
    if (pid == None):
        pid = os.getpid()
    process = psutil.Process(pid)
    child_list = process.children()
    cpu_usage = process.cpu_times().user
    for child in child_list:
        cpu_usage += child.cpu_times().user
    return cpu_usage

def get_proc_mem(pid = None):
    if (pid == None):
        pid = os.getpid()
    process = psutil.Process(pid)
    child_list = process.children()
    mem_usage = process.memory_info().rss
    for child in child_list:
        mem_usage += child.memory_info().rss
    return mem_usage



sys_monitor_flag = False
proc_monitor_flag = False
doc_monitor_flag = False

def system_report(client:Qoa_Client, interval:int, metrics:dict = None, category=None):
    try:
        client.add_metric(metrics['cpu_stat'])
        client.add_metric(metrics['mem_stat'])
    except Exception as e:
        print("Unable to add system metric: ", e)
    metric_list = []
    while sys_monitor_flag:
        try:
            for metric_name in metrics['cpu_stat']:
                metric = client.get_metric(metric_name)
                metric.set(get_cpu(metrics['cpu_stat'][metric_name]["key"]))
                metric_list.append(metric_name)
        except Exception as e:
            print("Unable to report CPU stat: ", e)
        try:
            for metric_name in metrics['mem_stat']:
                metric = client.get_metric(metric_name)
                metric.set(get_mem(metrics['mem_stat'][metric_name]["key"]))
                metric_list.append(metric_name)
        except Exception as e:
            print("Unable to report memory stat: ", e)
        try:
            client.report(metrics=metric_list, category=category)
        except Exception as e:
            print("Unable to send system report: ", e)
        time.sleep(interval)


def sys_monitor(client:Qoa_Client, interval:int, metrics: dict = None, category=None):
    if (metrics == None):
        metrics = default_sys_metric
    sub_thread = Thread(target=system_report, args=(client, interval, metrics, category))
    sub_thread.start()

def process_report(client:Qoa_Client, interval:int, pid:int = None, metrics: dict = None, category=None):
    if category == None:
        category = 'resource_monitor'
    try:
        client.add_metric(metrics['proc_cpu'],category=category)
        client.add_metric(metrics['proc_mem'],category=category)
    except Exception as e:
        print("Unable to add process metric: ", e)
    metric_list = []
    while proc_monitor_flag:
        try:
            for metric_name in metrics['proc_cpu']:
                metric = client.get_metric(metric_name,category=category)
                metric.set(get_proc_cpu(pid=pid))
                metric_list.append(metric_name)
        except Exception as e:
            print("Unable to report process CPU stat: ", e)
        try:
            for metric_name in metrics['proc_mem']:
                metric = client.get_metric(metric_name,category=category)
                metric.set(get_proc_mem(pid=pid))
                metric_list.append(metric_name)
        except Exception as e:
            print("Unable to report process memory stat: ", e)
        try:
            client.report(category=category)
            # client.report(metrics=metric_list, category=category)
        except Exception as e:
            print("Unable to send process report: ", e)
        time.sleep(interval)


def process_monitor(client:Qoa_Client, interval:int, pid:int = None, metrics: dict = None, category=None):
    if (metrics == None):
        metrics = default_proc_metric
    if (pid == None):
        pid = os.getpid()
    sub_thread = Thread(target=process_report, args=(client, interval, pid, metrics, category))
    sub_thread.start()

def get_cpu_stat(stats,key):
    if key == 'percentage':
        UsageDelta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']

        SystemDelta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']

        len_cpu = stats['cpu_stats']['online_cpus']

        percentage = (UsageDelta / SystemDelta) * len_cpu * 100
        return round(percentage, 2)
    else:
        return -1
def get_mem_stat(stats,key):
    if key == "used":
        return stats["memory_stats"]["usage"]
    else:
        return -1

def get_docker_stats(client):
    stats = {}
    try:
        for container in client.containers.list():
            stats[container.name] = {}
            stats[container.name]["cpu"] = {}
            stats[container.name]["mem"]= {}

            stat = container.stats(decode=None, stream = False) 
            stats[container.name]["cpu"]["percentage"] = get_cpu_stat(stat,"percentage")
            stats[container.name]["mem"]["used"] = get_mem_stat(stat,"used")
    except Exception as e:
        print("Unable to query docker stat: ", e)
    return stats

def docker_report(client:Qoa_Client, interval:int, metrics:dict = None, detail = False):
    try:
        client.add_metric(metrics)
    except Exception as e:
        print("Unable to add docker metric: ", e)
    metric_list = list(metrics.keys())
    doc_client = docker.from_env()
    
    while doc_monitor_flag:
        sum_cpu = 0
        sum_memory = 0
        try:
            stats = get_docker_stats(doc_client)
            for container_name in stats:
                sum_cpu += stats[container_name]["cpu"][metrics['dock_cpu_percentage']['key']]
                sum_memory += stats[container_name]["mem"][metrics['docker_memory_used']['key']]
                
            cpu_metric = client.get_metric('dock_cpu_percentage')
            cpu_metric.set(sum_cpu)
            mem_metric = client.get_metric('docker_memory_used')
            mem_metric.set(sum_memory)
        except Exception as e:
            print("Unable to report docker stat: ", e)

        try:
            if detail:
                client.report(report=stats)
            else:
                client.report(metrics=metric_list)
        except Exception as e:
            print("Unable to send system report: ", e)
        time.sleep(interval)

def docker_monitor(client:Qoa_Client, interval:int, metrics: dict = None, detail=False):
    if (metrics == None):
        metrics = default_docker_metric
    sub_thread = Thread(target=docker_report, args=(client, interval, metrics,detail))
    sub_thread.start()
