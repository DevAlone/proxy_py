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
            (zmq.REP, settings.proxies_handler.listen_socket_address),
            (zmq.PUSH, settings.proxies_handler.publish_socket_address),
        ],
    )


async def worker(
        proxies_to_check_socket: zmq.asyncio.Socket,
        results_socket: zmq.asyncio.Socket,
) -> int:
    while True:
        # task = await proxies_to_check_socket.recv_string()
        # logging.debug(f"<- {task}")
        # await asyncio.sleep(random.randint(1, 3))
        task = str(random.randint(1, 3))
        logging.debug(f"-> {task}")
        await results_socket.send_string(task)
        # await proxies_to_check_socket.send_string(task)
