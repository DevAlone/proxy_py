import zmq
import zmq.asyncio as zmq_asyncio

import settings

context = zmq.asyncio.Context()


async def main():
    # TODO: logs
    print("broker")
    tasks_handler_publish_socket = context.socket(zmq.ROUTER)
    proxies_handler_listen_socket = context.socket(zmq.DEALER)
    proxies_handler_publish_socket = context.socket(zmq.PULL)
    results_handler_listen_socket = context.socket(zmq.PUSH)

    context.setsockopt(zmq.LINGER, 0)
    # TODO: rewrite this shit
    tasks_handler_publish_socket.setsockopt(zmq.LINGER, 0)
    proxies_handler_listen_socket.setsockopt(zmq.LINGER, 0)
    proxies_handler_publish_socket.setsockopt(zmq.LINGER, 0)
    results_handler_listen_socket.setsockopt(zmq.LINGER, 0)

    try:
        tasks_handler_publish_socket.bind(settings.tasks_handler.publish_socket_address)
        proxies_handler_listen_socket.bind(settings.proxies_handler.listen_socket_address)
        proxies_handler_publish_socket.bind(settings.proxies_handler.publish_socket_address)
        results_handler_listen_socket.bind(settings.results_handler.listen_socket_address)

        await zmq.device(zmq.STREAMER, proxies_handler_publish_socket, results_handler_listen_socket)
        await zmq.proxy(tasks_handler_publish_socket, proxies_handler_listen_socket)
    finally:
        tasks_handler_publish_socket.close()
        proxies_handler_listen_socket.close()
        proxies_handler_publish_socket.close()

        # TODO: figure out why it hangs everything
        # context.term()

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
