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
        if len(extra) > 0:
            use_bind = extra[0]
        else:
            use_bind = False

        logging.debug(
            f'creating a socket with type "{socket_type}", address "{socket_address}" and use_bind = {use_bind}',
        )
        socket = context.socket(socket_type)
        if use_bind:
            socket.bind(socket_address)
        else:
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
