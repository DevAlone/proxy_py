import os
import importlib.util

from models import session, CollectorState


collectors = {}


for root, dirs, files in os.walk("collectors"):
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)
            module_name = os.path.splitext(file_path)[0].replace('/', '.')
            spec = importlib.util.spec_from_file_location(module_name, file_path)

            collector_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(collector_module)

            if hasattr(collector_module, "Collector"):
                if hasattr(collector_module.Collector, "__collector__") and collector_module.Collector.__collector__:
                    collectors[module_name] = collector_module.Collector()


# init db
for module_name, CollectorType in collectors.items():
    collectorState = session.query(CollectorState).filter(CollectorState.identifier == module_name).first()

    if not collectorState:
        session.add(CollectorState(
            identifier=module_name,
            processing_period=CollectorType.processing_period,
            last_processing_time=0,
        ))
        session.commit()


# def get_collector_state(module_name : str):
#     collectorState = session.query(CollectorState).filter(CollectorState.identifier == module_name).first()
#     if not collectorState:
#         raise CollectorNotFoundException()
#
#     return collectorState


def get_collector_of_module_name(module_name : str):
    if module_name not in collectors:
        raise CollectorNotFoundException()

    return collectors[module_name]


async def load_collector(state : CollectorState):
    collector = get_collector_of_module_name(state.identifier)
    await collector.load_state(state)
    return collector


class CollectorNotFoundException(BaseException):
    pass