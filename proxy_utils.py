import traceback

from proxy_py import settings
import async_requests

import asyncio
import ssl
import aiohttp
import aiosocks
import os


# TODO: add multiple checks with several sites
async def check_proxy(proxy_url: str):
    try:
        res = await async_requests.get(
            'https://pikagraphs.d3d.info/OK/',
            proxy=proxy_url,
            timeout=settings.PROXY_CHECKING_TIMEOUT,
        )
        if res.status == 200 and res.text == "OK":
            return True
    except (aiohttp.client_exceptions.ServerDisconnectedError,
            aiohttp.client_exceptions.ClientHttpProxyError,
            aiohttp.client_exceptions.ClientProxyConnectionError,
            aiohttp.client_exceptions.ClientResponseError,
            aiosocks.errors.SocksError,
            aiosocks.SocksError,
            asyncio.TimeoutError,
            aiohttp.client_exceptions.ClientOSError,
            ) as ex:
        # TODO: check to "Too many open files"
        return False
#
# async def get_working_proxies(domain, port, auth_data=""):
#     proxies = []
#
#     for protocol in Proxy.PROTOCOLS:
#         proxy = Proxy(protocol=protocol, domain=domain, port=port, auth_data=auth_data)
#
#         start_checking_time = time.time()
#         if await check_proxy(proxy):
#             end_checking_time = time.time()
#             proxies.append((proxy, start_checking_time, end_checking_time))
#
#     return proxies
