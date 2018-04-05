#!/usr/bin/env python3

from proxy_py import settings
from processor import Processor
from server.proxy_provider_server import ProxyProviderServer

from models import Proxy, ProxyCountItem, db

import asyncio
import time


async def create_proxy_count_item():
    good_proxies_count = await db.count(Proxy.select().where(Proxy.number_of_bad_checks == 0))
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


async def proxy_counter():
    while True:
        if (await db.count(ProxyCountItem.select())) == 0:
            await create_proxy_count_item()
        else:
            last_item = await db.get(ProxyCountItem.select().order_by(ProxyCountItem.timestamp.desc()))

            if int(last_item.timestamp // 60) * 60 + 60 < time.time():
                await create_proxy_count_item()

        await asyncio.sleep(5)


if __name__ == "__main__":
    proxy_processor = Processor()

    proxy_provider_server = ProxyProviderServer.get_proxy_provider_server(
        settings.PROXY_PROVIDER_SERVER_ADDRESS['HOST'],
        settings.PROXY_PROVIDER_SERVER_ADDRESS['PORT'],
        None,  # proxy_processor,
    )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(proxy_provider_server.start(loop))
    loop.run_until_complete(asyncio.wait([
        proxy_processor.exec(),
        proxy_counter(),
    ]))
