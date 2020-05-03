#!/usr/bin/env python3

import asyncio
import sys

import zmq
import zmq.asyncio

context = zmq.asyncio.Context()


async def main():
    socket_type = zmq.PULL
    socket_address = sys.argv[1]

    socket = context.socket(socket_type)

    # if high_water_mark > 0:
    #     socket.setsockopt(zmq.SNDHWM, high_water_mark)
    #     socket.setsockopt(zmq.RCVHWM, high_water_mark)

    # if kernel_buffer_size > 0:
    #     socket.setsockopt(zmq.SNDBUF, kernel_buffer_size)
    #     socket.setsockopt(zmq.RCVBUF, kernel_buffer_size)

    socket.bind(socket_address)

    while True:
        item = await socket.recv_string()
        print(item)


if __name__ == '__main__':
    asyncio.run(main())
