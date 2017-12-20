import asyncio
import ssl

import aiohttp
import aiosocks
import time

from models import Proxy
from proxy_py import settings
import async_requests


# TODO: add multiple checks with several sites
async def check_proxy(proxy):
    try:
        res = await async_requests.get(
            'https://pikagraphs.d3d.info/OK/',
            proxy=proxy.to_url(),
            timeout=settings.PROXY_CHECKING_TIMEOUT,
        )
        if res.status == 200 and res.text == "OK":
            return True

    except (asyncio.TimeoutError,
            aiohttp.client_exceptions.ServerDisconnectedError,
            aiohttp.client_exceptions.ClientOSError,
            aiohttp.ClientProxyConnectionError,
            aiosocks.errors.SocksError,
            aiohttp.client_exceptions.ClientResponseError,
            ssl.SSLError,
            ConnectionError):
        return False
    except:
        raise


async def get_working_proxies(domain, port, auth_data=""):
    proxies = []

    for protocol in Proxy.PROTOCOLS:
        proxy = Proxy(protocol=protocol, domain=domain, port=port, auth_data=auth_data)

        start_checking_time = time.time()
        if await check_proxy(proxy):
            end_checking_time = time.time()
            proxies.append((proxy, start_checking_time, end_checking_time))

    return proxies
