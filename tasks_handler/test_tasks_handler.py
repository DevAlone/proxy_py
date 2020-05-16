import asyncio

import pytest

import settings
import tasks_handler
from tests_helpers.tests_helpers import *
from .tasks_handler import TasksHandler


zmq_context = zmq.asyncio.Context()


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
    await tasks_handler.produce_check_existing_proxies_tasks()


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

@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_tasks_handler():
    new_proxies = [
        "http://localhost1.com:8080",
        "socks4://localhost2.com:8081",
        "socks5://localhost3.com:8082",
    ]
    expected_check_proxy_messages = [
        # it ignores protocol, so there will be more messages
        CheckProxyMessage(Protocol.http, "", "", "localhost1.com", 8080),
        CheckProxyMessage(Protocol.socks4, "", "", "localhost1.com", 8080),
        CheckProxyMessage(Protocol.socks5, "", "", "localhost1.com", 8080),

        CheckProxyMessage(Protocol.http, "", "", "localhost2.com", 8081),
        CheckProxyMessage(Protocol.socks4, "", "", "localhost2.com", 8081),
        CheckProxyMessage(Protocol.socks5, "", "", "localhost2.com", 8081),

        CheckProxyMessage(Protocol.http, "", "", "localhost3.com", 8082),
        CheckProxyMessage(Protocol.socks4, "", "", "localhost3.com", 8082),
        CheckProxyMessage(Protocol.socks5, "", "", "localhost3.com", 8082),
    ]
    check_results = [
        # TODO
    ]

    tasks_handler_task = asyncio.create_task(tasks_handler.main(noop_tasks_producer()))

    await connect_and_produce_messages_to_socket(
        zmq_context,
        zmq.PUSH,
        settings.collectors_handler.collectors_results_socket_address,
        new_proxies,
    )

    await connect_and_expect_messages_from_socket(
        zmq_context,
        zmq.PULL,
        settings.proxies_handler.proxies_to_check_socket_address,
        expected_check_proxy_messages,
    )

    await connect_and_produce_messages_to_socket(
        zmq_context,
        zmq.PUSH,
        settings.proxies_handler.check_results_socket_address,
        check_results,
    )

    await connect_and_expect_messages_from_socket(
        zmq_context,
        zmq.PULL,
        settings.results_handler.results_to_handle_socket_address,
        check_results,
    )

    # TODO: others

    tasks_handler_task.cancel()
