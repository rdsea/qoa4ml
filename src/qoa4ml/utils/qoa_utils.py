import glob
import json
import logging
import os
import pathlib
import re
import shlex
import subprocess
import sys
import time
import traceback
from threading import Thread

import numpy as np
import psutil
import yaml

from .logger import qoa_logger


def make_folder(temp_path):
    try:
        if os.path.exists(temp_path):
            pass
        else:
            os.makedirs(temp_path)
        return True
    except Exception:
        return False


def get_cgroup_version() -> str:
    proc1 = subprocess.Popen("mount", stdout=subprocess.PIPE)
    proc2 = subprocess.Popen(
        shlex.split("grep cgroup"),
        stdin=proc1.stdout,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if proc1.stdout:
        proc1.stdout.close()
    out, _ = proc2.communicate()
    if "cgroup2" in out.decode():
        return "v2"
    return "v1"


if get_cgroup_version() == "v2":
    CGROUP_VERSION = "v2"
else:
    CGROUP_VERSION = "v1"


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
    else:
        raise ValueError(f"Error logging level {logging_level}")
    qoa_logger.setLevel(log_level)


def load_config(file_path: str) -> dict:
    """
    file_path: file path to load config

    """
    try:
        if "json" in file_path:
            with open(file_path) as f:
                return json.load(f)
        if ("yaml" in file_path) or ("yml" in file_path):
            with open(file_path) as f:
                return yaml.safe_load(f)
        else:
            qoa_logger.warning("Unsupported format")
            return None
    except Exception:
        qoa_logger.error("Unable to load configuration")

    return None


def to_json(file_path: str, conf: dict):
    """
    file_path: file path to save config
    """
    with open(file_path, "w") as f:
        json.dump(conf, f)


def to_yaml(file_path: str, conf: dict):
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
        info[key] = getattr(stats, key)
    for key in cpu_time._fields:
        info[key] = getattr(cpu_time, key)
    return info


def get_sys_cpu_util():
    info = {}
    core_utils = psutil.cpu_percent(percpu=True)
    for core_num, core_util in enumerate(core_utils):
        info[f"core_{core_num}"] = core_util
    return info


def get_sys_cpu_metadata():
    cpu_freq = psutil.cpu_freq()
    frequency = {"value": cpu_freq.max / 1000, "unit": "GHz"}
    cpu_threads = psutil.cpu_count(logical=True)
    return {"frequency": frequency, "thread": cpu_threads}


def get_sys_mem():
    stats = psutil.virtual_memory()
    info = {}
    for key in stats._fields:
        info[key] = getattr(stats, key)
    return info


def get_sys_net():
    info = {}
    net = psutil.net_io_counters()
    for key in net._fields:
        info[key] = getattr(net, key)
    return info


def report_proc_cpu(process):
    report = {}
    cpu_time = process.cpu_times()
    context = process.num_ctx_switches()
    for key in cpu_time._fields:
        report[key] = getattr(cpu_time, key)
    for key in context._fields:
        report[key] = getattr(context, key)
    report["num_thread"] = process.num_threads()

    return report


def report_proc_child_cpu(process: psutil.Process):
    # WARNING: this children function takes a lot of time
    child_processes = process.children(recursive=True)
    child_processes_count = len(child_processes)
    child_processes_cpu = {}
    process_cpu_time = process.cpu_times()
    for id, child_proc in enumerate(child_processes):
        cpu_time = child_proc.cpu_times()
        child_processes_cpu[f"child_{id}"] = float(cpu_time.user + cpu_time.system)

    total_cpu_usage = sum(child_processes_cpu.values())
    total_cpu_usage += float(
        process_cpu_time.user
        + process_cpu_time.system
        + process_cpu_time.children_user
        + process_cpu_time.children_system
    )

    return {
        "child_process": child_processes_count,
        "value": child_processes_cpu,
        "total": total_cpu_usage,
        "unit": "cputime",
    }


def get_proc_cpu(pid=None):
    if pid is None:
        pid = os.getpid()
    process = psutil.Process(pid)
    child_list = process.children()
    info = {}
    info[pid] = report_proc_cpu(process)

    for child in child_list:
        info[child.pid + "c"] = report_proc_cpu(child)
    return info


def report_proc_mem(process: psutil.Process):
    report = {}
    mem_info = process.memory_info()
    for key in mem_info._fields:
        report[key] = getattr(mem_info, key)
    return report


def get_proc_mem(pid=None):
    if pid is None:
        pid = os.getpid()
    process = psutil.Process(pid)
    child_list = process.children()
    info = {}
    info[pid] = report_proc_mem(process)

    for child in child_list:
        info[child.pid + "c"] = report_proc_mem(child)
    return info


def convert_to_gbyte(value):
    return value / 1024.0 / 1024.0 / 1024.0


def convert_to_mbyte(value):
    return value / 1024.0 / 1024.0


def convert_to_kbyte(value):
    return value / 1024.0


###################### SYSTEM REPORT ######################

sys_monitor_flag = False
process_monitor_flag = False
doc_monitor_flag = False


def system_report(client, interval: int, to_mb=True, to_gb=False, to_kb=False):
    report = {}
    last_net_value = {"sent": 0, "receive": 0}
    while sys_monitor_flag:
        try:
            report["sys_cpu_stats"] = get_sys_mem()
        except Exception as e:
            qoa_logger.error(f"Error {type(e)} in report CPU stat: {e.__traceback__}")
            traceback.print_exception(*sys.exc_info())
        try:
            report["sys_mem_stats"] = get_sys_mem()
        except Exception as e:
            qoa_logger.error(
                f"Error {type(e)} in report memory stat: {e.__traceback__}"
            )
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
            report["sys_net_send"] = curr_net_value["sent"] - last_net_value["sent"]
            report["sys_net_receive"] = (
                curr_net_value["receive"] - last_net_value["receive"]
            )
            last_net_value = curr_net_value.copy()
        except Exception as e:
            qoa_logger.error(
                f"Error {type(e)} in report network stat: {e.__traceback__}"
            )
            traceback.print_exception(*sys.exc_info())
        try:
            client.report(report=report)
        except Exception as e:
            qoa_logger.error(
                f"Error {type(e)} in sent system report: {e.__traceback__}"
            )
            traceback.print_exception(*sys.exc_info())
        time.sleep(interval)


def sys_monitor(client, interval: int):
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


def get_cpu_stat(stats, key):
    if key == "percentage":
        usage_delta = (
            stats["cpu_stats"]["cpu_usage"]["total_usage"]
            - stats["precpu_stats"]["cpu_usage"]["total_usage"]
        )

        system_delta = (
            stats["cpu_stats"]["system_cpu_usage"]
            - stats["precpu_stats"]["system_cpu_usage"]
        )

        len_cpu = stats["cpu_stats"]["online_cpus"]

        percentage = (usage_delta / system_delta) * len_cpu * 100
        return round(percentage, 2)
    else:
        return -1


def get_mem_stat(stats, key):
    if key == "used":
        return stats["memory_stats"]["usage"]
    else:
        return -1


def merge_report(f_report, i_report, prio=True):
    try:
        if isinstance(f_report, dict) and isinstance(i_report, dict):
            key_list = tuple(f_report.keys())
            for key in key_list:
                if key in i_report:
                    f_report[key] = merge_report(f_report[key], i_report[key], prio)
                    i_report.pop(key)
            f_report.update(i_report)
        elif f_report != i_report:
            if prio is True:
                return f_report
            else:
                return i_report
    except Exception as e:
        qoa_logger.error(f"Error {type(e)} in mergeReport: {e.__traceback__}")
        traceback.print_exception(*sys.exc_info())
    return f_report


def get_dict_at(dict, i=0):
    try:
        keys = list(dict.keys())
        return keys[i], dict[keys[i]]
    except Exception as e:
        qoa_logger.error(f"Error {type(e)} in get_dict_at: {e.__traceback__}")
        traceback.print_exception(*sys.exc_info())


def get_file_dir(file, to_string=True):
    current_dir = pathlib.Path(file).parent.absolute()
    if to_string:
        return str(current_dir)
    else:
        return current_dir


def get_parent_dir(file, parent_level=1, to_string=True):
    current_dir = get_file_dir(file=file, to_string=False)
    for _ in range(parent_level):
        current_dir = current_dir.parent.absolute()
    if to_string:
        return str(current_dir)
    else:
        return current_dir


def is_numpyarray(obj):
    return isinstance(obj, np.ndarray)


def get_process_allowed_cpus():
    # NOTE: 0 as PID represents the calling process
    pid = 0
    affinity = os.sched_getaffinity(pid)
    return list(affinity)


def get_process_allowed_memory():
    if CGROUP_VERSION == "v1":
        with open("/proc/self/cgroup") as file:
            for line in file:
                parts = line.strip().split(":")
                if len(parts) == 3 and parts[1] == "memory":
                    cgroup_path = parts[2]
                    memory_limit_file = re.sub(r"/task_\d+", "", cgroup_path)

                    number_of_task = len(
                        glob.glob(f"/sys/fs/cgroup/memory{memory_limit_file}/task_*")
                    )

                    with open(
                        f"/sys/fs/cgroup/memory{memory_limit_file}/memory.limit_in_bytes"
                    ) as limit_file:
                        memory_limit_str = limit_file.read().strip()
                        try:
                            memory_limit_int = int(memory_limit_str)
                            return memory_limit_int / number_of_task
                        except ValueError:
                            return memory_limit_str
            return None

    else:
        with open("/proc/self/cgroup") as file:
            for line in file:
                parts = line.strip().split(":")
                cgroup_path = parts[2]
                pattern = r"/task_\d+"
                cgroup_path = re.sub(pattern, "", cgroup_path)
                with open(f"/sys/fs/cgroup{cgroup_path}/memory.max") as limit_file:
                    number_of_task = len(
                        glob.glob(f"/sys/fs/cgroup{cgroup_path}/task_*")
                    )
                    memory_limit_str = limit_file.read().strip()
                    try:
                        memory_limit_int = int(memory_limit_str)
                        return memory_limit_int / number_of_task
                    except ValueError:
                        return memory_limit_str
            return None
