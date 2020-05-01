import asyncio
import logging
from typing import Callable, Awaitable, Sequence, Tuple, Any

import zmq.asyncio

context = zmq.asyncio.Context()


async def handler(
        handler_name: str,
        worker: Callable[[zmq.asyncio.Socket], Awaitable[int]],
        number_of_workers: int,
        socket_descriptions: Sequence[Tuple[Any, ...]],
) -> int:
    """
    // TODO: doc!
    socket_descirpition (socket_type, socket_address, use_bind = False)
    """

    sockets = []
    for socket_type, socket_address, *extra in socket_descriptions:
        high_water_mark = 0
        if len(extra) > 0:
            high_water_mark = extra[0]

        kernel_buffer_size = 0
        if len(extra) > 1:
            kernel_buffer_size = extra[1]

        logging.debug(
            f'creating a socket with type "{socket_type}", '
            f'address "{socket_address}" and '
            f'high water mark = {high_water_mark} and'
            f'kernel buffer size = {kernel_buffer_size}',
        )
        socket = context.socket(socket_type)

        if high_water_mark > 0:
            socket.setsockopt(zmq.SNDHWM, high_water_mark)
            socket.setsockopt(zmq.RCVHWM, high_water_mark)

        if kernel_buffer_size > 0:
            socket.setsockopt(zmq.SNDBUF, kernel_buffer_size)
            socket.setsockopt(zmq.RCVBUF, kernel_buffer_size)

        socket.connect(socket_address)

        sockets.append(socket)

    logging.info(f"starting {handler_name} workers")

    tasks = [
        asyncio.create_task(worker_wrapper(handler_name, worker, sockets))
        for _ in range(number_of_workers)
    ]

    for task in tasks:
        await task

    # TODO: handle error code

    for socket in sockets:
        socket.close()

    context.destroy()

    return 0


async def worker_wrapper(
        handler_name: str,
        worker: Callable[[zmq.asyncio.Socket], Awaitable[int]],
        sockets: Sequence[zmq.asyncio.Socket],
) -> int:
    logging.debug(f"started {handler_name} worker")
    return await worker(*sockets)
