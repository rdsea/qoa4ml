import json, psutil, time, os, yaml, logging
from threading import Thread
import traceback,sys, pathlib

import logging

logging.basicConfig(format='%(asctime)s:%(levelname)s -- %(message)s', level=logging.INFO)

qoaLogger = logging.getLogger()

def set_logger_level(logging_level):
    if logging_level == 0:
        log_level = logging.NOTSET
    elif logging_level == 1:
        log_level = logging.DEBUG
    elif logging_level == 2:
        log_level = logging.INFO
    elif logging_level == 3:
        log_level = logging.WARNING
    elif logging_level == 4:
        log_level = logging.ERROR
    elif logging_level == 5:
        log_level = logging.CRITICAL
    qoaLogger.setLevel(log_level)

###################### DEFAULT METRIC ######################
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


###################### COMMON USED FUNCTION ######################
def load_config(file_path:str, format=0)->dict:
    """
    file_path: file path to load config
    format:
        0 - json
        1 - yaml
        other - To Do
    """
    try:
        if format == 0:
            with open(file_path, "r") as f:
                return json.load(f)
        elif format == 1:
            with open('file_path', 'r') as f:
                return yaml.safe_load(f)
        else:
            qoaLogger.warning("Unsupported format")
            return None
    except Exception as e:
        qoaLogger.error("Unable to load configuration")

def to_json(file_path:str, conf:dict):
    """
    file_path: file path to save config
    """
    with open(file_path, "w") as f:
        json.dump(conf, f)

def to_yaml(file_path:str, conf:dict):
    """
    file_path: file path to save config
    """
    with open(file_path, "w") as f:
        yaml.dump(conf, f)
    
def get_sys_cpu():
    stats = psutil.cpu_stats()
    cpu_time = psutil.cpu_times()
    info = {}
    for key in stats._fields:
        info[key] = getattr(stats,key)
    for key in cpu_time._fields:
        info[key] = getattr(cpu_time,key)
    return info

def get_sys_mem():
    stats = psutil.virtual_memory()
    info = {}
    for key in stats._fields:
        info[key] = getattr(stats,key)
    return info

def get_sys_net():
    info = {}
    net = psutil.net_io_counters()
    for key in net._fields:
        info[key] = getattr(net,key)
    return info

def report_proc_cpu(process):
    report = {}
    cpu_time = process.cpu_times()
    contex = process.num_ctx_switches()
    for key in cpu_time._fields:
        report[key] = getattr(cpu_time,key)
    for key in contex._fields:
        report[key] = getattr(contex,key)
    report['num_thread'] = process.num_threads()

    return report
    
def get_proc_cpu(pid = None):
    if (pid == None):
        pid = os.getpid()
    process = psutil.Process(pid)
    child_list = process.children()
    info = {}
    info[pid] = report_proc_cpu(process)
    
    for child in child_list:
        info[child.pid + "c"] = report_proc_cpu(child)
    return info

def report_proc_mem(process):
    report = {}
    mem_info = process.memory_info()
    for key in mem_info._fields:
        report[key] = getattr(mem_info,key)
    return report
    
def get_proc_mem(pid = None):
    if (pid == None):
        pid = os.getpid()
    process = psutil.Process(pid)
    child_list = process.children()
    info = {}
    info[pid] = report_proc_mem(process)
    
    for child in child_list:
        info[child.pid + "c"] = report_proc_mem(child)
    return info

def convert_to_gbyte(value):
    return value/1024./1024./1024.

def convert_to_mbyte(value):
    return value/1024./1024.

def convert_to_kbyte(value):
    return value/1024.

###################### SYSTEM REPORT ######################

sys_monitor_flag = False
procMonitorFlag = False
doc_monitor_flag = False


def system_report(client, interval:int, to_mb=True, to_gb=False, to_kb=False):
    report = {}
    last_net_value = {"sent":0, "receive":0}  
    while sys_monitor_flag:
        try:
            report["sys_cpu_stats"] = get_sys_mem()
        except Exception as e:
            qoaLogger.error("Error {} in report CPU stat: {}".format(type(e),e.__traceback__))
            traceback.print_exception(*sys.exc_info())
        try:
            report["sys_mem_stats"] = get_sys_mem()
        except Exception as e:
            qoaLogger.error("Error {} in report memory stat: {}".format(type(e),e.__traceback__))
            traceback.print_exception(*sys.exc_info())
        try:
            report["sys_net_stats"] = get_sys_net()
            sent = 0
            if to_mb:
                sent = convert_to_mbyte(psutil.net_io_counters().bytes_sent)
                receive = convert_to_mbyte(psutil.net_io_counters().bytes_recv)
            elif to_gb:
                sent = convert_to_gbyte(psutil.net_io_counters().bytes_sent)
                receive = convert_to_gbyte(psutil.net_io_counters().bytes_recv)
            elif to_kb:
                sent = convert_to_kbyte(psutil.net_io_counters().bytes_sent)
                receive = convert_to_kbyte(psutil.net_io_counters().bytes_recv)
            else:
                sent = psutil.net_io_counters().bytes_sent
                receive = psutil.net_io_counters().bytes_recv
            curr_net_value = {"sent": sent, "receive": receive}  
            report["sys_net_send"]  = curr_net_value["sent"] - last_net_value["sent"]
            report["sys_net_receive"]  = curr_net_value["receive"] - last_net_value["receive"]
            last_net_value = curr_net_value.copy()
        except Exception as e:
            qoaLogger.error("Error {} in report network stat: {}".format(type(e),e.__traceback__))
            traceback.print_exception(*sys.exc_info())
        try:
            client.report(report=report)
        except Exception as e:
            qoaLogger.error("Error {} in sent system report: {}".format(type(e),e.__traceback__))
            traceback.print_exception(*sys.exc_info())
        time.sleep(interval)


def sys_monitor(client, interval:int):
    sub_thread = Thread(target=system_report, args=(client, interval))
    sub_thread.start()


###################### PROCESS REPORT ######################   

# def process_report(client, interval:int, pid:int = None):
#     report = {}
#     while procMonitorFlag:
#         try:
#             report["proc_cpu_stats"] = get_proc_cpu()
#         except Exception as e:
#             qoaLogger.error("Error {} in report process cpu stat: {}".format(type(e),e.__traceback__))
#             traceback.print_exception(*sys.exc_info())
#         try:
#             report["proc_mem_stats"] = get_proc_mem()
#         except Exception as e:
#             qoaLogger.error("Error {} in report process memory stat: {}".format(type(e),e.__traceback__))
#             traceback.print_exception(*sys.exc_info())
#         try:
#             client.report(report=report)
#         except Exception as e:
#             qoaLogger.error("Error {} in sent process report: {}".format(type(e),e.__traceback__))
#             traceback.print_exception(*sys.exc_info())
#         time.sleep(interval)


# def process_monitor(client, interval:int, pid:int = None):
#     if (pid == None):
#         pid = os.getpid()
#     sub_thread = Thread(target=process_report, args=(client, interval, pid))
#     sub_thread.start()


###################### DOCKER REPORT ######################

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
        qoaLogger.error("Error {} in query docker stat: {}".format(type(e),e.__traceback__))
        traceback.print_exception(*sys.exc_info())
    return stats

def docker_report(client, interval:int, metrics:dict = None, detail = False):
    try:
        client.addMetric(metrics)
    except Exception as e:
        qoaLogger.error("Error {} in add docker metric: {}".format(type(e),e.__traceback__))
        traceback.print_exception(*sys.exc_info())
    metric_list = list(metrics.keys())

    if 'docker' not in globals():
        global docker
        import docker
    doc_client = docker.from_env()
    
    while doc_monitor_flag:
        sum_cpu = 0
        sum_memory = 0
        try:
            stats = get_docker_stats(doc_client)
            for container_name in stats:
                sum_cpu += stats[container_name]["cpu"][metrics['dock_cpu_percentage']['key']]
                sum_memory += stats[container_name]["mem"][metrics['docker_memory_used']['key']]
                
            cpu_metric = client.getMetric('dock_cpu_percentage')
            cpu_metric.set(sum_cpu)
            mem_metric = client.getMetric('docker_memory_used')
            mem_metric.set(sum_memory)
        except Exception as e:
            qoaLogger.error("Error {} in report docker stat: {}".format(type(e),e.__traceback__))
            traceback.print_exception(*sys.exc_info())

        try:
            if detail:
                client.report(report=stats)
            else:
                client.report(metrics=metric_list)
        except Exception as e:
            qoaLogger.error("Error {} in send docker report: {}".format(type(e),e.__traceback__))
            traceback.print_exception(*sys.exc_info())
        time.sleep(interval)

def docker_monitor(client, interval:int, metrics: dict = None, detail=False):
    if (metrics == None):
        metrics = default_docker_metric
    sub_thread = Thread(target=docker_report, args=(client, interval, metrics,detail))
    sub_thread.start()


def mergeReport(f_report, i_report, prio=True):
    try:
        if isinstance(f_report, dict) and isinstance(i_report, dict):
            key_list = tuple(f_report.keys())
            for key in key_list:
                if key in i_report:
                    f_report[key] = mergeReport(f_report[key],i_report[key],prio)
                    i_report.pop(key)
            f_report.update(i_report)
        else:
            if f_report != i_report:
                if prio == True:
                    return f_report
                else:
                    return i_report
    except Exception as e:
        qoaLogger.error("Error {} in mergeReport: {}".format(type(e),e.__traceback__))
        traceback.print_exception(*sys.exc_info())
    return f_report

def get_dict_at(dict, i=0):
    try:
        keys = list(dict.keys())
        return  keys[i], dict[keys[i]]
    except Exception as e:
        qoaLogger.error("Error {} in get_dict_at: {}".format(type(e),e.__traceback__))
        traceback.print_exception(*sys.exc_info())

def get_file_dir(file, to_string=True):
    current_dir = pathlib.Path(file).parent.absolute()
    if to_string:
        return str(current_dir)
    else:
        return current_dir

def get_parent_dir(file, parent_level=1, to_string=True):
    current_dir = get_file_dir(file=file, to_string=False)
    for i in range(parent_level):
        current_dir = current_dir.parent.absolute()
    if to_string:
        return str(current_dir)
    else:
        return current_dir



def is_numpyarray(obj):
    if 'np' not in globals():
        global np
        import numpy as np
    return type(obj) == np.ndarray

def is_pddataframe(obj):
    if 'pd' not in globals():
        global pd 
        import pandas as pd
    return type(obj) == pd.DataFrame