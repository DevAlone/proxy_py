import asyncio
import random
import time

import zmq
import zmq.asyncio

import settings
from handler import handler

context = zmq.asyncio.Context()


async def main():
    tasks = [
        asyncio.create_task(task)
        for task in [
            produce_tasks(),
            fetch_results(),
        ]
    ]

    for task in tasks:
        await task

    # TODO: handle error code?
    # TODO: close the sockets
    # for socket in sockets:
    #     socket.close()
    #
    # context.destroy()


# async def worker(socket: zmq.asyncio.Socket):
#     while True:
#         try:
#             # TODO: replace with zeromq's timeout
#             await asyncio.wait_for(work(socket), timeout=settings.tasks_handler.task_processing_timeout)
#         except asyncio.TimeoutError:
#             # TODO: log
#             print("timeout happened!")
#


async def produce_tasks():
    proxies_to_check_socket = context.socket(zmq.PUSH)
    proxies_to_check_socket.bind(settings.tasks_handler.proxies_to_check_socket_address)

    while True:
        # task = str(random.randint(0, 9999))
        task = str(time.time())

        print(f"-> {task}")
        await proxies_to_check_socket.send_string(task)
        await asyncio.sleep(5)
    # print(f"trying to recieve something")

    # resp = await socket.recv_string()
    # print(f"<- {resp}")

    # if resp != task:
    #     raise Exception("AAAAA")


async def fetch_results():
    check_results_socket = context.socket(zmq.PULL)
    check_results_socket.bind(settings.tasks_handler.check_results_socket_address)

    results_to_handle_socket = context.socket(zmq.PUSH)
    results_to_handle_socket.bind(settings.tasks_handler.results_to_handle_socket_address)

    while True:
        result = await check_results_socket.recv_string()
        print(f"<- {result}")

        print(f"2-> {result}")
        await results_to_handle_socket.send_string(result)
