# NOTE: Mark lazy module globally, only load when used
import lazy_import

lazy_import.lazy_module("requests")
lazy_import.lazy_module("tensorflow")
lazy_import.lazy_module("numpy")
lazy_import.lazy_module("pandas")
lazy_import.lazy_module("fastapi")
lazy_import.lazy_module("tinyflux")
lazy_import.lazy_module("psutil")
