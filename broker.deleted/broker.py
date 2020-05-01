import asyncio

import zmq
import zmq.asyncio as zmq_asyncio

import settings

context = zmq.asyncio.Context()

# tasks_handler_publish_socket = context.socket(zmq.ROUTER)
# proxies_handler_listen_socket = context.socket(zmq.DEALER)
# proxies_handler_publish_socket = context.socket(zmq.PULL)
# results_handler_listen_socket = context.socket(zmq.PUSH)


async def main():
    # TODO: logs
    print("broker")

    # context.setsockopt(zmq.LINGER, 0)
    # TODO: rewrite this shit
    # tasks_handler_publish_socket.setsockopt(zmq.LINGER, 0)
    # proxies_handler_listen_socket.setsockopt(zmq.LINGER, 0)
    # proxies_handler_publish_socket.setsockopt(zmq.LINGER, 0)
    # results_handler_listen_socket.setsockopt(zmq.LINGER, 0)

    try:
        # tasks_handler_publish_socket.bind(settings.tasks_handler.proxies_to_check_req_socket)
        # proxies_handler_listen_socket.bind(settings.proxies_handler.proxies_to_check_resp_socket_address)
        # proxies_handler_publish_socket.bind(settings.proxies_handler.publish_socket_address)
        # results_handler_listen_socket.bind(settings.results_handler.listen_socket_address)

        # existing_proxies_checking_gateway_task = asyncio.create_task(
        #     zmq.proxy(tasks_handler_publish_socket, proxies_handler_listen_socket),
        # )
        # results_handling_gateway_task = asyncio.create_taks(
        #     zmq.device(zmq.STREAMER, proxies_handler_publish_socket, results_handler_listen_socket),
        # )
        #
        # await existing_proxies_checking_gateway_task
        # await results_handling_gateway_task
        await worker()
    finally:
        pass
        # tasks_handler_publish_socket.close()
        # proxies_handler_listen_socket.close()
        # proxies_handler_publish_socket.close()
        # results_hanlder....close()

        # TODO: figure out why it hangs everything
        # context.term()


async def worker():
    poller = zmq.asyncio.Poller()
    # TODO: rewrite
    # poller.register(tasks_handler_publish_socket, zmq.POLLIN)
    # poller.register(proxies_handler_listen_socket, zmq.POLLIN)
    # poller.register(proxies_handler_publish_socket, zmq.POLLIN)
    # poller.register(results_handler_listen_socket, zmq.POLLIN)

    print("starting a loop...")
    while True:
        socks = dict(await poller.poll())

        # if socks.get(tasks_handler_publish_socket) == zmq.POLLIN:
        #     message = await tasks_handler_publish_socket.recv_multipart()
        #     await proxies_handler_listen_socket.send_multipart(message)

        # if socks.get(proxies_handler_listen_socket) == zmq.POLLIN:
        #     message = await proxies_handler_listen_socket.recv_multipart()
        #     await tasks_handler_publish_socket.send_multipart(message)

        # if socks.get(proxies_handler_publish_socket) == zmq.POLLIN:
        #     message = await proxies_handler_publish_socket.recv_multipart()
        #     await results_handler_listen_socket.send_multipart(message)
