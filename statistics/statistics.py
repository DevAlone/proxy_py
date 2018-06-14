from models import Proxy, ProxyCountItem, NumberOfProxiesToProcess, db
from models import CollectorState, NumberOfCollectorsToProcess
from proxy_py import settings
import time
import asyncio


async def worker():
    while True:
        await process_graph(ProxyCountItem, 60, create_proxy_count_item)
        await process_graph(NumberOfProxiesToProcess, 60, number_of_proxies_to_process)
        await process_graph(NumberOfCollectorsToProcess, 60, number_of_collectors_to_process)
        await asyncio.sleep(10)


async def process_graph(model, period, func):
    if (await db.count(model.select())) == 0:
        await func()
    else:
        last_item = await db.get(
            model.select().order_by(
                model.timestamp.desc()
            ).limit(1)
        )

        if int(last_item.timestamp // period) * period + period < time.time():
            await func()


async def create_proxy_count_item():
    good_proxies_count = await db.count(
        Proxy.select().where(Proxy.number_of_bad_checks == 0)
    )
    bad_proxies_count = await db.count(Proxy.select().where(
        Proxy.number_of_bad_checks > 0,
        Proxy.number_of_bad_checks < settings.DEAD_PROXY_THRESHOLD,
    ))
    dead_proxies_count = await db.count(Proxy.select().where(
        Proxy.number_of_bad_checks >= settings.DEAD_PROXY_THRESHOLD
    ))

    await db.create(
        ProxyCountItem,
        timestamp=int(time.time()),
        good_proxies_count=good_proxies_count,
        bad_proxies_count=bad_proxies_count,
        dead_proxies_count=dead_proxies_count,
    )


async def number_of_proxies_to_process():
    timestamp = time.time()
    good_proxies_count = await db.count(
        Proxy.select().where(
            Proxy.number_of_bad_checks == 0,
            Proxy.last_check_time < timestamp - Proxy.checking_period,
        )
    )

    bad_proxies_count = await db.count(
        Proxy.select().where(
            Proxy.number_of_bad_checks > 0,
            Proxy.number_of_bad_checks < settings.DEAD_PROXY_THRESHOLD,
            Proxy.last_check_time < timestamp - settings.BAD_PROXY_CHECKING_PERIOD,
        )
    )

    dead_proxies_count = await db.count(
        Proxy.select().where(
            Proxy.number_of_bad_checks >= settings.DEAD_PROXY_THRESHOLD,
            Proxy.number_of_bad_checks < settings.REMOVE_ON_N_BAD_CHECKS,
            Proxy.last_check_time < timestamp - settings.DEAD_PROXY_CHECKING_PERIOD,
        )
    )

    await db.create(
        NumberOfProxiesToProcess,
        timestamp=timestamp,
        good_proxies=good_proxies_count,
        bad_proxies=bad_proxies_count,
        dead_proxies=dead_proxies_count,
    )


async def number_of_collectors_to_process():
    timestamp = time.time()

    number_of_collectors = await db.count(
        CollectorState.select().where(
            CollectorState.last_processing_time <
            timestamp - CollectorState.processing_period,
        )
    )

    await db.create(
        NumberOfCollectorsToProcess,
        timestamp=timestamp,
        value=number_of_collectors,
    )
