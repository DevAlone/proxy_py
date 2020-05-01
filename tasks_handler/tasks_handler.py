import asyncio
import collections
import logging
import time

import zmq.asyncio

import settings


async def postgres_tasks_producer():
    i = 0
    while True:
        i += 1
        yield str(int(time.time()))


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
        self.checking_proxies_timeouts = asyncio.Queue()

    async def run(self):
        tasks = [
            asyncio.create_task(task)
            for task in [
                self.produce_tasks(),
                self.fetch_results(),
                self.timeout_handler(),
            ]
        ]

        for task in tasks:
            await task

    async def produce_tasks(self):
        logging.info("starting produce_tasks...")

        async for task in self.tasks_producer():
            timeout = int(task) + 10

            logging.debug(f"-> {task}")
            await self.proxies_to_check_socket.send_string(task)

            self.checking_proxies.add(task)
            await self.checking_proxies_timeouts.put((task, timeout))

            await self.checking_proxies_semaphore.acquire()

    async def fetch_results(self):
        logging.info("starting fetch_results...")

        while True:
            result = await self.check_results_socket.recv_string()
            logging.debug(f"<- {result}")

            self.checking_proxies.remove(result)
            logging.debug(f"-> {result}")
            await self.results_to_handle_socket.send_string(result)

            self.checking_proxies_semaphore.release()

    async def timeout_handler(self):
        logging.info("starting timeout_handler...")

        while True:
            logging.debug("waiting to get checking proxy timeout")
            task, timeout = await self.checking_proxies_timeouts.get()
            curr_time = time.time()
            if curr_time >= timeout:
                logging.debug("curr_time >= timeout")
                await self.handle_timeout_task(task, timeout)
            else:
                logging.debug("sleeping")
                await asyncio.sleep(timeout - curr_time)
                logging.debug("curr_time >= timeout")
                await self.handle_timeout_task(task, timeout)

    async def handle_timeout_task(self, task, timeout):
        if task in self.checking_proxies:
            logging.warning("found timed out proxy", extra={
                "task": task,
            })
            self.checking_proxies_semaphore.release()
            self.checking_proxies.remove(task)
            # TODO: move to the end in DB(time.now() + some_value)
