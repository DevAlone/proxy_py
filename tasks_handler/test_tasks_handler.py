import asyncio
import types

import pytest
import zmq.asyncio

from .tasks_handler import TasksHandler


def create_range_tasks_producer(n: int):
    async def producer():
        for i in range(n):
            yield i

    return producer


# TODO: create sockets which would count number of got messages
class NoopSocket(zmq.asyncio.Socket):
    def __init__(self):
        pass

    async def send_string(self, *args, **kwargs):
        pass

    async def recv_string(self, *args, **kwargs):
        pass


# TODO: rewrite so that it timeouts not only for async functions
def should_timeout(timeout: float):
    def decorator(function):
        async def wrapper(*args, **kwargs):
            try:
                await asyncio.wait_for(function(*args, **kwargs), timeout=timeout)
                raise AssertionError(f"function was expected to timeout in {timeout} seconds")
            except asyncio.TimeoutError:
                pass

        return wrapper

    return decorator


@pytest.mark.asyncio
@should_timeout(timeout=5)
async def test_produce_tasks_timeout():
    tasks_handler = TasksHandler(
        NoopSocket(),
        NoopSocket(),
        NoopSocket(),
        tasks_producer=create_range_tasks_producer(10),
    )
    await tasks_handler.produce_tasks()


# @pytest.mark.asyncio
# @pytest.mark.timeout(5)
# async def test_tasks_handler_ok():
#     tasks_handler = TasksHandler(
#         NoopSocket(),
#         NoopSocket(),
#         NoopSocket(),
#         tasks_producer=create_range_tasks_producer(10),
#     )
#     tasks_handler.check_results_socket.close()
#     tasks_handler.results_to_handle_socket.close()
#     await tasks_handler.run()
