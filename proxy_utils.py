import traceback

import sys

from proxy_py import settings
import async_requests

import asyncio
import ssl
import aiohttp
import aiosocks
import os

from aiosocks.connector import ProxyConnector, ProxyClientRequest


# TODO: add multiple checks with several sites
async def check_proxy(proxy_url: str, session=None, timeout=None):
    try:
        res = await _request(
            'get',
            'https://pikagraphs.d3d.info/OK/',
            # 'https://wtfismyip.com/text',
            proxy_url,
            settings.PROXY_CHECKING_TIMEOUT if timeout is None else timeout,
            session
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
            ssl.CertificateError,
            ) as ex:
        message = str(ex)
        if "file" in message:
            print(message)
        # TODO: check for "Too many open files"
        return False

    return False


async def _request(method, url, proxy_url, timeout, session: aiohttp.ClientSession=None):
    headers = {
        'User-Agent': async_requests.get_random_user_agent()
    }

    conn = ProxyConnector(remote_resolve=True)

    with aiohttp.ClientSession(connector=conn, request_class=ProxyClientRequest) as session:
        async with session.request(method, url, proxy=proxy_url, timeout=timeout) as response:
            # async with session.request(method, url, timeout=timeout, headers=headers, proxy=proxy_url) as response:
            status = response.status
            text = await response.text()
            return async_requests.Response(status, text)
