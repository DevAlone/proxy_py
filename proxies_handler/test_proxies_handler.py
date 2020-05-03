import asyncio

import pytest
import zmq.asyncio

import proxies_handler
import settings
from tests_helpers import *

zmq_context = zmq.asyncio.Context()


@pytest.mark.asyncio
# @pytest.mark.timeout(10)
async def test_proxies_handler():
    expects = [
        CheckProxyMessage(Protocol.http, "login1", "password1", "hostname1", 1),
        CheckProxyMessage(Protocol.socks4, "login2", "password2", "hostname2", 2),
        CheckProxyMessage(Protocol.socks5, "login3", "password3", "hostname3", 3),
    ]
    results = [
        ProxyCheckingResult(
            check_proxy_message,
            True,
            i
        ) for i, check_proxy_message in enumerate(expects)
    ]

    checker = create_mock_proxy_checker(expects=expects, results=results)
    proxies_handler_task = asyncio.create_task(proxies_handler.main(checker))

    await bind_and_produce_messages_to_socket(
        zmq_context, zmq.PUSH, settings.tasks_handler.proxies_to_check_socket_address, expects,
    )

    await bind_and_expect_messages_from_socket(
        zmq_context, zmq.PULL, settings.tasks_handler.check_results_socket_address, results,
    )

    proxies_handler_task.cancel()
