import asyncio
import logging
import random
import sys

import zmq
import zmq.asyncio

import settings
from handler import handler


async def main() -> int:
    return await handler(
        handler_name="proxies_handler",
        worker=worker,
        number_of_workers=settings.proxies_handler.number_of_workers,
        socket_descriptions=[
            (zmq.PULL, settings.tasks_handler.proxies_to_check_socket_address),
            (zmq.PUSH, settings.tasks_handler.check_results_socket_address),
        ],
    )


async def worker(
        proxies_to_check_socket: zmq.asyncio.Socket,
        results_socket: zmq.asyncio.Socket,
) -> int:
    while True:
        task = await proxies_to_check_socket.recv_string()
        logging.debug(f"<- {task}")

        # do some checking
        await asyncio.sleep(random.randint(1, 3))

        logging.debug(f"-> {task}")
        await results_socket.send_string(task)
        # TODO:!!!
        # await proxies_to_check_socket.send_string(task)

    return 0