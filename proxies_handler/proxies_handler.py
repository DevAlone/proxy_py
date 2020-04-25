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
        socket_type=zmq.REP,
        socket_address=settings.proxies_handler.socket_address,
    )


i = 0

async def worker(socket: zmq.asyncio.Socket):
    global i

    while True:
        i += 1
        task = await socket.recv_string()
        logging.debug(f"<- {task}")
        # await asyncio.sleep(random.randint(1, 3))
        # await asyncio.sleep(99999)
        logging.debug(f"-> {task}")
        await socket.send_string(task)
        if i > 50:
            sys.exit(1)
