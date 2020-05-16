import asyncio
import logging
import time

import typing
import zmq
import zmq.asyncio

import collectors_list
import settings
from handler import handler
# TODO: rewrite it so that collectors' state is saved in redis or something like this
from storage import CollectorState, PostgresStorage


async def main() -> int:
    await collectors_list.init()

    return await handler(
        handler_name="collectors_handler",
        worker=worker,
        number_of_workers=settings.proxies_handler.number_of_workers,
        socket_descriptions=[
            (
                zmq.PUSH,
                settings.collectors_handler.collectors_results_socket_address,
                settings.collectors_handler.high_water_mark,
                settings.collectors_handler.kernel_buffer_size,
            ),
        ],
    )


async def worker(
        collector_results_socket: zmq.asyncio.Socket,
):
    storage = PostgresStorage()
    await storage.init()
    try:
        while True:
            collector_states = await storage.get_collectors_to_check(time.time(), 1)
            if not collector_states:
                await asyncio.sleep(1)
                continue

            async for proxy_address in process_collector_of_state(collector_states[0]):
                # TODO: validate proxy?
                # TODO: send pyobj?
                await collector_results_socket.send_string(proxy_address)
    finally:
        await storage.close()


async def process_collector_of_state(collector_state: CollectorState) -> typing.AsyncGenerator[str, None]:
    collector = await collectors_list.load_collector(collector_state)

    try:
        logging.debug(
            "start processing collector of type \"{}\"".format(type(collector))
        )

        number_of_proxies = 0
        async for proxy in collector._collect():
            number_of_proxies += 1
            # TODO: do something with collector_state.id?
            yield proxy

        def log_number_of_proxies():
            log_level_func = logging.warning if number_of_proxies == 0 else logging.info
            log_level_func(
                f'got {number_of_proxies} proxies from collector of type "{type(collector)}"'
            )

        log_number_of_proxies()
    except BaseException as ex:
        logging.error(
            f'Error in collector of type "{collector_state.identifier}": {ex}',
        )
        logging.exception(ex)
    finally:
        collector.last_processing_time = int(time.time())
        await collectors_list.save_collector(collector_state)
