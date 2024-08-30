# NOTE: Mark lazy module globally, only load when used
from __future__ import annotations

import lazy_import

lazy_import.lazy_module("requests")
lazy_import.lazy_module("fastapi")
lazy_import.lazy_module("tinyflux")
lazy_import.lazy_module("psutil")
