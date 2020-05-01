import asyncio

import zmq
import zmq.asyncio

import settings
from .tasks_handler import TasksHandler

context = zmq.asyncio.Context()


async def main():
    sockets = {
        "proxies_to_check_socket": {
            "instance": None,
            "type": zmq.PUSH,
            "address": settings.tasks_handler.proxies_to_check_socket_address
        },
        "check_results_socket": {
            "instance": None,
            "type": zmq.PULL,
            "address": settings.tasks_handler.check_results_socket_address,
        },
        "results_to_handle_socket": {
            "instance": None,
            "type": zmq.PUSH,
            "address": settings.tasks_handler.results_to_handle_socket_address
        },
    }

    for socket_name, socket_description in sockets.values():
        socket = context.socket(socket_description["type"])
        if settings.tasks_handler.high_water_mark > 0:
            socket.setsockopt(zmq.SNDHWM, settings.tasks_handler.high_water_mark)
            socket.setsockopt(zmq.RCVHWM, settings.tasks_handler.high_water_mark)

        if settings.tasks_handler.kernel_buffer_size > 0:
            socket.setsockopt(zmq.SNDBUF, settings.tasks_handler.kernel_buffer_size)
            socket.setsockopt(zmq.RCVBUF, settings.tasks_handler.kernel_buffer_size)

        socket.bind(socket_description["address"])

        sockets[socket_name] = socket

    await TasksHandler(**sockets).run()

    # TODO: handle error code?
    # TODO: close the sockets
    # for socket in sockets:
    #     socket.close()
    #
    # context.destroy()
