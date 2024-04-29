import importlib.util
import sys


def lazy_import(name):
    spec = importlib.util.find_spec(name)
    if not spec or not spec.loader:
        raise RuntimeError(f"Can't find spec with name {name}")
    loader = importlib.util.LazyLoader(spec.loader)
    spec.loader = loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    loader.exec_module(module)
    return module
