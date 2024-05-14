import os

try:
    ODOP_PATH = os.environ["ODOP_PATH"]
except KeyError:
    raise RuntimeError("ODOP_PATH is not defined, please defined it ")
