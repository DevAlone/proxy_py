import asyncio
import ssl

import aiohttp
import aiosocks

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
                    aiohttp.errors.ClientDisconnectedError,
                    aiohttp.errors.ClientTimeoutError,
                    aiosocks.errors.SocksError,
                    aiohttp.client_exceptions.ClientResponseError,
                    aiohttp.errors.HttpProcessingError,
                    ssl.SSLError,
                    ConnectionRefusedError):
        return False
    return False


async def detect_raw_proxy_protocols(raw_proxy):
    """
    method gets proxy in any of the supported formats
    and return proxy protocols
    supported raw proxy formats:
    ip:port
    domain:port
    user:pass@ip:port
    user:pass@domain:port

    :param raw_proxy:
    :return:
    """

    result = []

    protocols = ['http', 'socks5', 'socks4']

    for protocol in protocols:
        # TODO: add other test sites
        try:
            res = await async_requests.get(
                'https://pikagraphs.d3d.info/OK/',
                proxy="{}://{}".format(protocol, raw_proxy),
                timeout=settings.PROXY_CHECKING_TIMEOUT
            )

            if res.status == 200 and res.text == "OK":
                result.append(protocol)
                except (asyncio.TimeoutError,
                        aiohttp.client_exceptions.ServerDisconnectedError,
                        aiohttp.client_exceptions.ClientOSError,
                        aiohttp.errors.ClientDisconnectedError,
                        aiohttp.errors.ClientTimeoutError,
                        aiosocks.errors.SocksError,
                        aiohttp.client_exceptions.ClientResponseError,
                        aiohttp.errors.HttpProcessingError,
                        ssl.SSLError,
                        ConnectionRefusedError):
                pass

    return result
