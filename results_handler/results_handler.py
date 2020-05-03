import asyncio
import logging
import time

import zmq
import zmq.asyncio

import settings
from handler import handler
from proxy_py_types.messages import ProxyCheckingResult
from storage import models
from storage.models import db


async def main() -> int:
    return await handler(
        handler_name="results_handler",
        worker=worker,
        number_of_workers=settings.results_handler.number_of_workers,
        socket_descriptions=[(zmq.PULL, settings.results_handler.results_to_handle_socket_address)],
    )


async def worker(results_socket: zmq.asyncio.Socket):
    while True:
        proxy_checking_result: ProxyCheckingResult = await results_socket.recv_string()
        logging.debug(f"<- {proxy_checking_result}")
        await create_or_update_proxy(proxy_checking_result)


async def create_or_update_proxy(
        proxy_checking_result: ProxyCheckingResult,
):
    # to microseconds
    response_time = proxy_checking_result.response_time * 1000 * 1000

    proxy_message = proxy_checking_result.check_proxy_message
    raw_protocol = proxy_message.protocol.value
    auth_data = ""
    if proxy_message.login or proxy_message.password:
        auth_data = f"{proxy_message.login}:{proxy_message.password}"

    domain = proxy_message.hostname
    port = proxy_message.port

    # TODO: why atomic?
    async with db.atomic():
        # TODO: fix spontaneous issue with unique constraint:
        # peewee.IntegrityError: duplicate key value violates unique constraint
        # "proxies_raw_protocol_auth_data_domain_port"

        proxy, was_created = await db.get_or_create(
            models.Proxy,
            raw_protocol=raw_protocol,
            auth_data=auth_data,
            domain=domain,
            port=port,
        )

        if was_created:
            proxy.number_of_bad_checks = 0

        if proxy.bad_proxy or proxy.uptime is None or proxy.uptime == 0:
            proxy.uptime = int(time.time())

        if proxy.bad_uptime is None or proxy.bad_uptime == 0 or \
                proxy.number_of_bad_checks >= settings.dead_proxy_threshold:
            proxy.bad_uptime = int(time.time())

        proxy.response_time = response_time
        proxy.number_of_bad_checks = 0
        proxy.last_check_time = int(time.time())

        # TODO:
        # if additional_info is not None:
        #     if additional_info.ipv4 is not None:
        #         proxy.white_ipv4 = additional_info.ipv4

        # TODO: calculate
        proxy.checking_period = 5 * 60
        # proxy.checking_period = settings.MIN_PROXY_CHECKING_PERIOD \
        #                         + (checking_time / settings.PROXY_CHECKING_TIMEOUT) \
        #                         * (settings.MAX_PROXY_CHECKING_PERIOD - settings.MIN_PROXY_CHECKING_PERIOD)

        # TODO: bad and not working proxies period

        proxy.next_check_time = proxy.last_check_time + proxy.checking_period

        await db.update(proxy)
