import asyncio
import random

import zmq
import zmq.asyncio

import settings
from handler import handler


async def main():
    return await handler(
        handler_name="tasks_handler",
        worker=worker,
        number_of_workers=settings.tasks_handler.number_of_workers,
        socket_type=zmq.REQ,
        socket_address=settings.tasks_handler.socket_address,
    )


async def worker(socket):
    while True:
        try:
            # TODO: replace with zeromq's timeout
            await asyncio.wait_for(work(socket), timeout=settings.tasks_handler.task_processing_timeout)
        except asyncio.TimeoutError:
            # TODO: log
            print("timeout happened!")


async def work(socket: zmq.asyncio.Socket):
    # task = str(int(time.time()))
    task = str(random.randint(0, 9999))
    print(f"-> {task}")
    await socket.send_string(task)
    resp = await socket.recv_string()
    print(f"<- {resp}")
    if resp != task:
        raise Exception("AAAAA")

    await asyncio.sleep(0.1)
