import asyncio
import logging
import time

import typing
import zmq.asyncio

import proxy_py_types
import proxy_validator
import storage
import settings
from proxy_py_types import CheckProxyMessage
from proxy_py_types.messages import ProxyCheckingResult


# TODO: if collector sent a proxy which exists in db and was checked recently, ignore it
# TODO: validate proxies from collector(length for example)


async def postgres_tasks_producer() -> typing.AsyncGenerator[CheckProxyMessage, None]:
    good_next_update_timestamp = 0
    bad_next_update_timestamp = 0
    dead_next_update_timestamp = 0
    postgres_storage = storage.PostgresStorage()
    await postgres_storage.init()

    try:
        while True:
            # TODO: there can be a problem when a lot of proxies with the same timestamp
            # would make it push same tasks
            async def fetch(func, next_update_timestamp) -> typing.List[storage.Proxy]:
                return await func(next_update_timestamp, settings.tasks_handler.fetch_n_proxies_at_time)

            def proxy_to_check_proxy_message(proxy: storage.Proxy) -> CheckProxyMessage:
                return CheckProxyMessage(
                    protocol=proxy.protocol,
                    login=proxy.login,
                    password=proxy.password,
                    hostname=proxy.address,
                    port=proxy.port,
                )

            proxies = await fetch(postgres_storage.get_good_proxies_to_check, good_next_update_timestamp)
            for proxy in proxies:
                yield proxy_to_check_proxy_message(proxy)

            if proxies:
                good_next_update_timestamp = proxies[-1].next_check_time
                continue

            proxies = await fetch(postgres_storage.get_bad_proxies_to_check, bad_next_update_timestamp)
            for proxy in proxies:
                yield proxy_to_check_proxy_message(proxy)

            if proxies:
                bad_next_update_timestamp = proxies[-1].next_check_time
                continue

            proxies = await fetch(postgres_storage.get_dead_proxies_to_check, dead_next_update_timestamp)
            for proxy in proxies:
                yield proxy_to_check_proxy_message(proxy)

            if proxies:
                dead_next_update_timestamp = proxies[-1].next_check_time
                continue

            await asyncio.sleep(1)
    finally:
        await postgres_storage.close()


class TasksHandler:
    def __init__(
            self,
            proxies_to_check_socket: zmq.asyncio.Socket,
            check_results_socket: zmq.asyncio.Socket,
            results_to_handle_socket: zmq.asyncio.Socket,
            collectors_results_socket: zmq.asyncio.Socket,
            tasks_producer=None,
    ):
        self.proxies_to_check_socket = proxies_to_check_socket
        self.check_results_socket = check_results_socket
        self.results_to_handle_socket = results_to_handle_socket
        self.collectors_results_socket = collectors_results_socket
        self.tasks_producer = tasks_producer
        if self.tasks_producer is None:
            self.tasks_producer = postgres_tasks_producer

        self.checking_proxies_semaphore = asyncio.Semaphore(settings.tasks_handler.proxies_checking_queue_size)
        self.checking_proxies = set()
        self.checking_proxies_timeouts = asyncio.Queue()
        self.has_more_tasks = True
        self.number_of_produced_tasks = 0
        self.number_of_fetched_results = 0

    async def run(self) -> int:
        tasks = [
            asyncio.create_task(task)
            for task in [
                self.produce_check_existing_proxies_tasks(),
                self.produce_check_new_proxies_tasks(),
                self.fetch_results(),
                self.timeout_handler(),
            ]
        ]

        for task in tasks:
            await task

        return 0

    async def produce_check_existing_proxies_tasks(self):
        logging.info("starting  produce_check_existing_proxies_tasks...")

        async for task in self.tasks_producer():
            await self.push_task_to_the_queue(task)

        self.has_more_tasks = False

    async def produce_check_new_proxies_tasks(self):
        logging.info("starting  produce_check_new_proxies_tasks...")

        # TODO: add condition to stop
        while True:
            # TODO: accept pyobj?
            collector_result = await self.collectors_results_socket.recv_string()
            logging.debug(f"<- {collector_result}")
            proxy_address = collector_result

            try:
                _, auth_data, domain, port = proxy_validator.retrieve(proxy_address)
            except proxy_validator.ValidationError as ex:
                logging.error(
                    f'Collector with id "unknown" returned bad raw proxy "{proxy_address}". Message: {ex}',
                )
                return

            for protocol in proxy_py_types.Protocol:
                login = ""
                password = ""
                if auth_data:
                    login = auth_data.split(":")[0]
                    password = auth_data.split(":")[1]

                task = CheckProxyMessage(
                    protocol=protocol.name,
                    login=login,
                    password=password,
                    hostname=domain,
                    port=port,
                )
                await self.push_task_to_the_queue(task)

    async def push_task_to_the_queue(self, task):
        timeout = int(time.time()) + settings.tasks_handler.task_processing_timeout

        logging.debug(f"-> {task}")
        await self.proxies_to_check_socket.send_pyobj(task)

        self.checking_proxies.add(task)
        await self.checking_proxies_timeouts.put((task, timeout))

        await self.checking_proxies_semaphore.acquire()
        self.number_of_produced_tasks += 1

    async def fetch_results(self):
        logging.info("starting fetch_results...")

        while self.has_more_tasks and self.checking_proxies_semaphore:
            result: ProxyCheckingResult = await self.check_results_socket.recv_pyobj()
            logging.debug(f"<- {result}")

            if result.check_proxy_message in self.checking_proxies:
                self.checking_proxies.remove(result.check_proxy_message)

            logging.debug(f"-> {result}")
            await self.results_to_handle_socket.send_pyobj(result)

            self.checking_proxies_semaphore.release()
            self.number_of_fetched_results += 1

    async def timeout_handler(self):
        logging.info("starting timeout_handler...")

        while self.has_more_tasks and not self.checking_proxies_timeouts.empty():
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

    async def handle_timeout_task(self, task: CheckProxyMessage, timeout):
        if task in self.checking_proxies:
            logging.warning("found timed out proxy", extra={
                "task": task,
            })
            self.checking_proxies_semaphore.release()
            self.checking_proxies.remove(task)
            # TODO: move to the end in DB(time.now() + some_value)
