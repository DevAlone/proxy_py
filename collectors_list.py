import os
import importlib.util


collector_types = []


for root, dirs, files in os.walk("collectors"):
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)
            spec = importlib.util.spec_from_file_location(
                os.path.splitext(file_path)[0].replace('/', '.'), file_path)

            collector_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(collector_module)

            if hasattr(collector_module, "Collector"):
                if hasattr(collector_module.Collector, "__collector__") and collector_module.Collector.__collector__:
                    collector_types.append(collector_module.Collector)