import zmq
import zmq.asyncio as zmq_asyncio

import settings

context = zmq.asyncio.Context()


async def main():
    # TODO: logs
    print("broker")
    tasks_handler_socket = context.socket(zmq.ROUTER)
    tasks_handler_socket.bind(settings.tasks_handler.socket_address)

    proxies_handler_socket = context.socket(zmq.DEALER)
    proxies_handler_socket.bind(settings.proxies_handler.socket_address)

    await zmq.proxy(tasks_handler_socket, proxies_handler_socket)

    tasks_handler_socket.close()
    proxies_handler_socket.close()
    context.term()

    # poller = zmq.asyncio.Poller()
    # poller.register(tasks_handler_socket, zmq.POLLIN)
    # poller.register(proxies_handler_socket, zmq.POLLIN)
    #
    # print("starting a loop...")
    # while True:
    #     socks = dict(await poller.poll())
    #
    #     if socks.get(tasks_handler_socket) == zmq.POLLIN:
    #         message = await tasks_handler_socket.recv_multipart()
    #         await proxies_handler_socket.send_multipart(message)
    #
    #     if socks.get(proxies_handler_socket) == zmq.POLLIN:
    #         message = await proxies_handler_socket.recv_multipart()
    #         await tasks_handler_socket.send_multipart(message)
