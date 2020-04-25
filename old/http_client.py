from proxy_py import settings
from fake_useragent import UserAgent
from aiosocks.connector import ProxyConnector, ProxyClientRequest

import aiohttp
import json


class HttpClientResult:
    text = None
    aiohttp_response = None

    @staticmethod
    async def make(aiohttp_response):
        obj = HttpClientResult()
        obj.aiohttp_response = aiohttp_response
        obj.text = await obj.aiohttp_response.text()

        return obj

    def as_text(self):
        return self.text

    def as_json(self):
        return json.loads(self.text)


# TODO: complete cookies saving
class HttpClient:
    """
    Simple class for making http requests,
    user-agent is set to random one in constructor
    """
    _aiohttp_connector = None

    def __init__(self):
        self.user_agent = UserAgent().random
        self.timeout = 60
        if HttpClient._aiohttp_connector is None:
            HttpClient._aiohttp_connector = ProxyConnector(
                remote_resolve=True,
                limit=settings.NUMBER_OF_SIMULTANEOUS_REQUESTS,
                limit_per_host=settings.NUMBER_OF_SIMULTANEOUS_REQUESTS_PER_HOST,
            )
        self.proxy_address = None

    async def get(self, url):
        """
        send HTTP GET request

        :param url:
        :return:
        """
        return await self.request('GET', url, None)

    async def post(self, url, data):
        """
        send HTTP POST request

        :param url:
        :param data:
        :return:
        """
        return await self.request('POST', url, data)

    async def request(self, method, url, data) -> HttpClientResult:
        headers = {
            'User-Agent': self.user_agent,
        }

        async with aiohttp.ClientSession(connector=HttpClient._aiohttp_connector,
                                         connector_owner=False,
                                         request_class=ProxyClientRequest
                                         ) as session:
            async with session.request(method,
                                       url=url,
                                       data=data,
                                       proxy=self.proxy_address,
                                       timeout=self.timeout,
                                       headers=headers) as response:
                return await HttpClientResult.make(response)

    @staticmethod
    async def clean():
        HttpClient._aiohttp_connector.close()


async def get_text(url):
    """
    fast method for sending get response without creating extra objects

    :param url:
    :return:
    """
    return (await HttpClient().get(url)).as_text()


async def get_json(url):
    return (await HttpClient().get(url)).as_json()
