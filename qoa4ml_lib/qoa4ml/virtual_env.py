import os
import subprocess
import shlex
import re


def get_cgroup_version() -> str:
    proc1 = subprocess.Popen(shlex.split("mount"), stdout=subprocess.PIPE)
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


def get_process_allowed_cpus():
    with open("/proc/self/status") as file:
        for line in file:
            if "Cpus_allowed_list" in line:
                ranges = line.split(":")[1].strip().split(",")
                result = []
                for range_str in ranges:
                    if "-" not in range_str:
                        result.append(int(range_str))
                    start, end = map(int, range_str.split("-"))
                    result.extend(list(range(start, end + 1)))
                return result


def get_process_allowed_memory(cgroup_version: str):
    if cgroup_version == "v1":
        with open("/proc/self/cgroup") as file:
            for line in file:
                parts = line.strip().split(":")
                if len(parts) == 3 and parts[1] == "memory":
                    cgroup_path = parts[2]
                    memory_limit_file = re.sub(r"/task_\d+", "", cgroup_path)
                    os.listdir(
                        f"/sys/fs/cgroup/memory{memory_limit_file}/memory.limit_in_bytes"
                    )
                    with open(
                        f"/sys/fs/cgroup/memory{memory_limit_file}/memory.limit_in_bytes"
                    ) as limit_file:
                        memory_limit = limit_file.read().strip()
                        return memory_limit

    else:
        with open("/proc/self/cgroup") as file:
            for line in file:
                parts = line.strip().split(":")
                cgroup_path = parts[2]
                with open(f"/sys/fs/cgroup{cgroup_path}/memory.max") as file:
                    memory_limit = file.read().strip()
                    return memory_limit


cgroup_version = get_cgroup_version()
print(get_process_allowed_memory(cgroup_version))
