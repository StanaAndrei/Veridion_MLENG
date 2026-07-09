import importlib, pkgutil

modules = []

# Automatically find and import every file in this folder
for _, module_name, _ in pkgutil.iter_modules(__path__):
    full_module_name = f"{__name__}.{module_name}"
    modules.append(importlib.import_module(full_module_name))