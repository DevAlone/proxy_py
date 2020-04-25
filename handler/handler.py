import asyncio
import logging
import random
from typing import Callable, Awaitable

import zmq
import zmq.asyncio

import settings


async def handler(
        handler_name: str,
        worker: Callable[[zmq.asyncio.Socket], Awaitable[int]],
        number_of_workers: int,
        socket_type,
        socket_address: str,
) -> int:
    context = zmq.asyncio.Context()
    socket = context.socket(socket_type)
    socket.connect(socket_address)

    logging.info(f"starting {handler_name} workers")

    tasks = [
        asyncio.create_task(worker_wrapper(handler_name, worker, socket))
        for _ in range(number_of_workers)
    ]

    for task in tasks:
        await task

    # TODO: handle error code

    return 0


async def worker_wrapper(
        handler_name: str,
        worker: Callable[[zmq.asyncio.Socket], Awaitable[int]],
        socket: zmq.asyncio.Socket,
) -> int:
    logging.debug(f"started {handler_name} worker")
    return await worker(socket)
