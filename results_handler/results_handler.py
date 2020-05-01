import asyncio
import logging

import zmq
import zmq.asyncio

import settings
from handler import handler


async def main() -> int:
    return await handler(
        handler_name="results_handler",
        worker=worker,
        number_of_workers=settings.results_handler.number_of_workers,
        socket_descriptions=[(zmq.PULL, settings.results_handler.results_to_handle_socket_address)],
    )


async def worker(results_socket: zmq.asyncio.Socket):
    res = 0
    while True:
        proxy_checking_result = await results_socket.recv_string()
        logging.debug(f"<- {proxy_checking_result}")

        # do some handling
        # res += int(proxy_checking_result)

        # TODO: handle the results
