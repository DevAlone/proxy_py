import asyncio
import time

from models import (
    CollectorState,
    NumberOfCollectorsToProcess,
    NumberOfProxiesToProcess,
    Proxy,
    ProxyCountItem,
    db,
)
from proxy_py import settings


async def worker():
    while True:
        await process_graph(ProxyCountItem, 60, create_proxy_count_item)
        await process_graph(NumberOfProxiesToProcess, 60, number_of_proxies_to_process)
        await process_graph(
            NumberOfCollectorsToProcess, 60, number_of_collectors_to_process
        )
        await asyncio.sleep(10)


async def process_graph(model, period, func):
    timestamp = time.time()

    if (await db.count(model.select())) == 0:
        await func(timestamp)
    else:
        last_item = await db.get(
            model.select().order_by(model.timestamp.desc()).limit(1)
        )

        if int(last_item.timestamp // period) * period + period < timestamp:
            await func(timestamp)


async def create_proxy_count_item(timestamp):
    good_proxies_count = await db.count(
        Proxy.select().where(Proxy.number_of_bad_checks == 0)
    )
    bad_proxies_count = await db.count(
        Proxy.select().where(
            Proxy.number_of_bad_checks > 0,
            Proxy.number_of_bad_checks < settings.DEAD_PROXY_THRESHOLD,
        )
    )
    dead_proxies_count = await db.count(
        Proxy.select().where(
            Proxy.number_of_bad_checks >= settings.DEAD_PROXY_THRESHOLD
        )
    )

    await db.create(
        ProxyCountItem,
        timestamp=timestamp,
        good_proxies_count=good_proxies_count,
        bad_proxies_count=bad_proxies_count,
        dead_proxies_count=dead_proxies_count,
    )


async def number_of_proxies_to_process(timestamp):
    good_proxies_count = await db.count(
        Proxy.select().where(
            Proxy.number_of_bad_checks == 0,
            Proxy.next_check_time < timestamp,
        )
    )

    bad_proxies_count = await db.count(
        Proxy.select().where(
            Proxy.number_of_bad_checks > 0,
            Proxy.number_of_bad_checks < settings.DEAD_PROXY_THRESHOLD,
            Proxy.next_check_time < timestamp,
        )
    )

    dead_proxies_count = await db.count(
        Proxy.select().where(
            Proxy.number_of_bad_checks >= settings.DEAD_PROXY_THRESHOLD,
            Proxy.number_of_bad_checks < settings.DO_NOT_CHECK_ON_N_BAD_CHECKS,
            Proxy.next_check_time < timestamp,
        )
    )

    await db.create(
        NumberOfProxiesToProcess,
        timestamp=timestamp,
        good_proxies=good_proxies_count,
        bad_proxies=bad_proxies_count,
        dead_proxies=dead_proxies_count,
    )


async def number_of_collectors_to_process(timestamp):
    number_of_collectors = await db.count(
        CollectorState.select().where(
            CollectorState.last_processing_time
            < timestamp - CollectorState.processing_period,
        )
    )

    await db.create(
        NumberOfCollectorsToProcess,
        timestamp=timestamp,
        value=number_of_collectors,
    )
