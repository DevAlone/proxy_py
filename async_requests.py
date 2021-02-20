import json

import aiohttp
from aiosocks.connector import ProxyClientRequest, ProxyConnector


async def get(url, **kwargs):
    return await request("get", url, **kwargs)


async def post(url, data, **kwargs):
    if data is dict or data is str:
        kwargs["json"] = data
    else:
        kwargs["data"] = data

    return await request("post", url, **kwargs)


async def request(method, url, **kwargs):
    session_kwargs = {}
    if "proxy" in kwargs and kwargs["proxy"].startswith("socks"):
        session_kwargs["connector"] = ProxyConnector(remote_resolve=False)
        session_kwargs["request_class"] = ProxyClientRequest

    if "cookies" in kwargs:
        session_kwargs["cookies"] = kwargs["cookies"]
        del kwargs["cookies"]

    if "timeout" not in kwargs:
        kwargs["timeout"] = 10

    # headers={'User-Agent': get_random_user_agent()}
    if "headers" not in kwargs:
        kwargs["headers"] = {"User-Agent": get_random_user_agent()}
    elif "User-Agent" not in kwargs["headers"]:
        kwargs["headers"]["User-Agent"] = get_random_user_agent()

    if "override_session" in kwargs:
        session = kwargs["override_session"]
        del kwargs["override_session"]
        async with session.request(method, url, **kwargs) as response:
            return await Response.from_aiohttp_response(response)

    async with aiohttp.ClientSession(**session_kwargs) as session:
        async with session.request(method, url, **kwargs) as response:
            return await Response.from_aiohttp_response(response)


class Response:
    def __init__(self, status, text, aiohttp_response=None):
        self.status = status
        self.text = text
        self.aiohttp_response = aiohttp_response

    @staticmethod
    async def from_aiohttp_response(aiohttp_response):
        return Response(
            status=aiohttp_response.status,
            text=await aiohttp_response.text(),
            aiohttp_response=aiohttp_response,
        )

    def __str__(self):
        return json.dumps(
            {
                "status": self.status,
                "text": self.text,
            }
        )

    __repr__ = __str__


def get_random_user_agent():
    return "Mozilla/5.0 (Windows NT;) Gecko/20100101 Firefox/58.0"
    # return 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'
    # TODO: do it
    # return UserAgent().random
