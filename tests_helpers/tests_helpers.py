import typing

import zmq
import zmq.asyncio

from proxy_py_types import Protocol, CheckProxyMessage
from proxy_py_types.messages import ProxyCheckingResult


def create_range_tasks_producer(n: int) -> typing.Callable[
    [], typing.AsyncGenerator[CheckProxyMessage, None],
]:
    async def producer() -> typing.AsyncGenerator[CheckProxyMessage, None]:
        for i in range(n):
            yield CheckProxyMessage(Protocol.http, "", "", "localhost", 8080)

    return producer


def create_mock_proxy_checker(
        expects: typing.Iterable[CheckProxyMessage],
        results: typing.Iterable[ProxyCheckingResult],
) -> typing.Callable[[CheckProxyMessage], typing.Awaitable[ProxyCheckingResult]]:
    i = 0
    expects = list(expects)
    results = list(results)
    assert len(expects) == len(results), "expects and results should have the same length"

    async def checker(check_proxy_message: CheckProxyMessage) -> ProxyCheckingResult:
        nonlocal i
        assert i < len(expects), f"call to checker({check_proxy_message}) wasn't expected"
        assert expects[i] == check_proxy_message, f"expected '{expects[i]}', got '{check_proxy_message}'"
        result = results[i]
        i += 1
        return result

    return checker


async def bind_and_produce_messages_to_socket(
        context: zmq.asyncio.Context, socket_type, socket_address, messages,
):
    socket = context.socket(socket_type)
    try:
        socket.bind(socket_address)

        for message in messages:
            await socket.send_pyobj(message)
    finally:
        socket.close()


async def bind_and_expect_messages_from_socket(
        context: zmq.asyncio.Context, socket_type, socket_address, messages,
):
    socket = context.socket(socket_type)
    try:
        socket.bind(socket_address)

        for expected_message in messages:
            message = await socket.recv_pyobj()
            assert message == expected_message
    finally:
        socket.close()
