import aiohttp
import json
from aiosocks.connector import ProxyConnector, ProxyClientRequest
from fake_useragent import UserAgent


async def get(url, **kwargs):
    return await request('get', url, **kwargs)


async def post(url, data, **kwargs):
    if data is dict or data is str:
        kwargs['json'] = data
    else:
        kwargs['data'] = data

    return await request('post', url, **kwargs)


async def request(method, url, **kwargs):
    session_kwargs = {}
    if 'proxy' in kwargs and kwargs['proxy'].startswith('socks'):
        session_kwargs['connector'] = ProxyConnector(remote_resolve=False)
        session_kwargs['request_class'] = ProxyClientRequest

    if 'cookies'in kwargs:
        session_kwargs['cookies'] = kwargs['cookies']
        del kwargs['cookies']

    if 'timeout' not in kwargs:
        kwargs['timeout'] = 10

    # headers={'User-Agent': get_random_user_agent()}
    if 'headers' not in kwargs:
        kwargs['headers'] = {'User-Agent': get_random_user_agent()}
    elif 'User-Agent' not in kwargs['headers']:
            kwargs['headers']['User-Agent'] = get_random_user_agent()

    async with aiohttp.ClientSession(**session_kwargs) as session:
        async with session.request(method, url, **kwargs) as response:
            status = response.status
            text = await response.text()
            return Response(status, text)


class Response:
    def __init__(self, status, text):
        self.status = status
        self.text = text

    def __str__(self):
        return json.dumps({
            'status': self.status,
            'text': self.text,
        })

    __repr__ = __str__


def get_random_user_agent():
    return UserAgent().random