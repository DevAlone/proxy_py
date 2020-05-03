import asyncio

import pytest

import proxies_handler
import results_handler
import tasks_handler
from tests_helpers import *


@pytest.mark.asyncio
@pytest.mark.timeout(10)
async def test_mock_tasks_producer():
    n = 99

    expects = [
        CheckProxyMessage(Protocol.http, "", "", "localhost", 8080)
        for _ in range(n)
    ]
    results = [
        ProxyCheckingResult(
            CheckProxyMessage(Protocol.http, "", "", "localhost", 8080),
            True,
            888,
        )
        for _ in range(n)
    ]

    tasks = [
        asyncio.create_task(coroutine)
        for coroutine in [
            proxies_handler.main(create_mock_proxy_checker(expects, results)),
            results_handler.main(),
        ]
    ]

    await tasks_handler.main(create_range_tasks_producer(n))

    assert tasks_handler.main.tasks_handler.number_of_produced_tasks == n
    assert tasks_handler.main.tasks_handler.number_of_fetched_results == n

    for task in tasks:
        task.cancel()


# TODO: test message flow
