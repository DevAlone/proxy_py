#!/usr/bin/env python3

from proxy_py import settings
from processor import Processor
from server.proxy_provider_server import ProxyProviderServer
import collectors_list
from models import Proxy, ProxyCountItem, session

import asyncio
import time


async def create_proxy_count_item():
    session.add(ProxyCountItem(
        timestamp=int(time.time()),
        good_proxies_count=session.query(Proxy).filter(Proxy.number_of_bad_checks == 0).count(),
        bad_proxies_count =session.query(Proxy)
            .filter(Proxy.number_of_bad_checks > 0)
            .filter(Proxy.number_of_bad_checks < settings.DEAD_PROXY_THRESHOLD).count(),
        dead_proxies_count=session.query(Proxy)
            .filter(Proxy.number_of_bad_checks >= settings.DEAD_PROXY_THRESHOLD).count()
    ))
    session.commit()


async def proxy_counter():
    while True:
        if session.query(ProxyCountItem).count() == 0:
            await create_proxy_count_item()
        else:
            last_item = session.query(ProxyCountItem).order_by(ProxyCountItem.timestamp.desc()).first()
            if int(last_item.timestamp // 60) * 60 + 60 < time.time():
                await create_proxy_count_item()

        await asyncio.sleep(1)


if __name__ == "__main__":
    proxy_processor = Processor()
    # for module_name, CollectorType in collectors_list.collector_types.items():
    #     proxy_processor.add_collector_of_type(CollectorType)

    proxy_provider_server = ProxyProviderServer.get_proxy_provider_server(
        settings.PROXY_PROVIDER_SERVER_ADDRESS['HOST'],
        settings.PROXY_PROVIDER_SERVER_ADDRESS['PORT'],
        proxy_processor,
    )

    loop = asyncio.get_event_loop()
    loop.run_until_complete(proxy_provider_server.start(loop))
    loop.run_until_complete(asyncio.wait([
        proxy_processor.exec(),
        proxy_counter(),
    ]))