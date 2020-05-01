import asyncio
import collections
import logging

import zmq.asyncio

import settings


async def postgres_tasks_producer():
    i = 0
    while True:
        i += 1
        yield str(i)


class TasksHandler:
    def __init__(
            self,
            proxies_to_check_socket: zmq.asyncio.Socket,
            check_results_socket: zmq.asyncio.Socket,
            results_to_handle_socket: zmq.asyncio.Socket,
            tasks_producer=None,
    ):
        self.proxies_to_check_socket = proxies_to_check_socket
        self.check_results_socket = check_results_socket
        self.results_to_handle_socket = results_to_handle_socket
        self.tasks_producer = tasks_producer
        if self.tasks_producer is None:
            self.tasks_producer = postgres_tasks_producer

        self.checking_proxies_semaphore = asyncio.Semaphore(settings.tasks_handler.proxies_checking_queue_size)
        self.checking_proxies = set()
        self.checking_proxies_timeouts = collections.deque()

    async def run(self):
        tasks = [
            asyncio.create_task(task)
            for task in [
                self.produce_tasks(),
                self.fetch_results(),
            ]
        ]

        for task in tasks:
            await task

    async def produce_tasks(self):
        logging.debug("starting produce_tasks...")

        async for task in self.tasks_producer():
            timeout = int(task) + 10

            logging.debug(f"-> [produce_tasks] {task}")
            await self.proxies_to_check_socket.send_string(task)

            self.checking_proxies.add(task)
            self.checking_proxies_timeouts.append((task, timeout))

            await self.checking_proxies_semaphore.acquire()

    async def fetch_results(self):
        logging.debug("starting fetch_results...")

        while True:
            result = await self.check_results_socket.recv_string()
            print(f"<- [fetch_results] {result}")

            print(f"-> [fetch_results] {result}")
            await self.results_to_handle_socket.send_string(result)

            self.checking_proxies_semaphore.release()
