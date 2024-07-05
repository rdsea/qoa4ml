# NOTE: Mark lazy module globally, only load when used
import lazy_import

lazy_import.lazy_module("requests")
# NOTE: package in extra, will cause error if not installed
try:
    lazy_import.lazy_module("tensorflow")
    lazy_import.lazy_module("docker")
    lazy_import.lazy_module("numpy")
    lazy_import.lazy_module("pandas")
except Exception:
    pass

lazy_import.lazy_module("fastapi")
lazy_import.lazy_module("tinyflux")
lazy_import.lazy_module("psutil")
