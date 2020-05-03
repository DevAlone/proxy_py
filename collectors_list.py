import inspect
import os
import importlib.util

import storage
from storage.models import db
import settings


collectors = {}


async def init():
    global collectors

    # TODO: use storage!
    postgres_storage = storage.PostgresStorage()
    await postgres_storage.init()

    _collectors_dirs = settings.collectors_handler.collectors_dirs
    if type(_collectors_dirs) is not list:
        _collectors_dirs = [_collectors_dirs]

    for collectors_dir in _collectors_dirs:
        if collectors_dir.startswith('/'):
            raise Exception("Collector's dir cannot be absolute")
        if collectors_dir.startswith('..'):
            raise Exception("Collector's dir cannot be in parent directory")

        for root, dirs, files in os.walk(collectors_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    if file_path.startswith('./'):
                        file_path = file_path[2:]
                    module_name = os.path.splitext(file_path)[0].replace('/', '.')
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    collector_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(collector_module)

                    # TODO: iterate through all classes independent of their names
                    for name, member in inspect.getmembers(collector_module, inspect.isclass):
                        # if inspect.isclass(member):
                        if member.__module__ == collector_module.__name__ \
                                and hasattr(member, '__collector__') \
                                and member.__collector__:
                            collectors[module_name + '.' + member.__name__] = member()

    # init db

    for module_name, Collector in collectors.items():
        try:
            await db.get(
                storage.CollectorState.select().where(
                    storage.CollectorState.identifier == module_name
                )
            )
        except storage.CollectorState.DoesNotExist:
            await db.create(
                storage.CollectorState,
                identifier=module_name,
                processing_period=Collector.processing_period,
                last_processing_time=0,
            )


def get_collector_of_module_name(module_name: str):
    if module_name not in collectors:
        raise CollectorNotFoundException(
            "Probably some collector exists in database but not in filesystem. "
            "module_name = {}".format(module_name)
        )

    return collectors[module_name]


async def load_collector(state: storage.CollectorState):
    collector = get_collector_of_module_name(state.identifier)
    await collector.load_state(state)
    return collector


async def save_collector(state: storage.CollectorState):
    collector = get_collector_of_module_name(state.identifier)
    await collector.save_state(state)
    await db.update(state)


class CollectorNotFoundException(BaseException):
    pass
