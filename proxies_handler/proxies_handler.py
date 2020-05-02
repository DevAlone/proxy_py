import logging
import time

import typing
import zmq
import zmq.asyncio

import settings
from handler import handler
from proxies_handler import proxy_utils
from proxy_py_types import CheckProxyMessage
from proxy_py_types.messages import ProxyCheckingResult


async def main(
        checker: typing.Callable[
            [CheckProxyMessage], typing.Awaitable[ProxyCheckingResult]
        ] = None,
) -> int:
    if checker is None:
        checker = default_checker

    return await handler(
        handler_name="proxies_handler",
        worker=worker,
        number_of_workers=settings.proxies_handler.number_of_workers,
        socket_descriptions=[
            (
                zmq.PULL,
                settings.proxies_handler.proxies_to_check_socket_address,
                settings.proxies_handler.high_water_mark,
                settings.proxies_handler.kernel_buffer_size,
            ),
            (
                zmq.PUSH,
                settings.proxies_handler.check_results_socket_address,
            ),
        ],
        worker_kwargs={
            "checker": checker,
        },
    )


async def worker(
        proxies_to_check_socket: zmq.asyncio.Socket,
        results_socket: zmq.asyncio.Socket,
        checker: typing.Callable[[CheckProxyMessage], typing.Awaitable[ProxyCheckingResult]],
):
    while True:
        check_proxy_message: CheckProxyMessage = await proxies_to_check_socket.recv_pyobj()
        logging.debug(f"<- {check_proxy_message}")

        proxy_checking_result = await checker(check_proxy_message)

        logging.debug(f"-> {proxy_checking_result}")
        await results_socket.send_pyobj(proxy_checking_result)


async def default_checker(check_proxy_message: CheckProxyMessage) -> ProxyCheckingResult:
    start_checking_time = time.time()
    check_result, _ = await proxy_utils.check_proxy(check_proxy_message.to_url())
    end_checking_time = time.time()

    return ProxyCheckingResult(
        check_proxy_message=check_proxy_message,
        does_work=check_result,
        response_time=end_checking_time - start_checking_time,
    )
