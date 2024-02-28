import subprocess, multiprocessing, time, atexit, os, signal

import yaml

from odop_obs import OdopObs


def run_server():
    subprocess.run(["uvicorn", "exporter:app", "--port", "8000"])


if __name__ == "__main__":
    config = yaml.safe_load(open("./odop_obs_conf.yaml"))
    odop_obs = OdopObs(config)
    odop_obs.start()
    while True:
        print("working")
        time.sleep(1)
