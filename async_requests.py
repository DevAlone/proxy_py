import aiohttp
import json
import requests
import aiosocks
from aiosocks.connector import ProxyConnector, ProxyClientRequest

async def get(url, *args, **kwargs):
    return await request('get', url, *args, **kwargs)


async def post(url, data, *args, **kwargs):
    if data is dict or data is str:
        kwargs['json'] = data
    else:
        kwargs['data'] = data

    return await request('post', url, *args, **kwargs)


async def request(type, url, *args, **kwargs):
    sessionKwargs = {}
    if 'proxy' in kwargs and kwargs['proxy'].startswith('socks'):
        sessionKwargs['connector'] = ProxyConnector(remote_resolve=False)
        sessionKwargs['request_class'] = ProxyClientRequest

    if 'cookies'in kwargs:
        sessionKwargs['cookies'] = kwargs['cookies']
        del kwargs['cookies']

    if 'timeout' not in kwargs:
        kwargs['timeout'] = 10

    async with aiohttp.ClientSession(**sessionKwargs) as session:
        async with session.request(type, url, **kwargs) as response:
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


# def getProxyDict(rawProxy, protocol):
#     proxiesTypesList = {
#         'http': {
#             'http': 'http://' + rawProxy,
#             'https': 'https://' + rawProxy
#         },
#         'socks5': {
#             'http': 'socks5://' + rawProxy,
#             'https': 'socks5://' + rawProxy
#         },
#         'socks4': {
#             'http': 'socks4://' + rawProxy,
#             'https': 'socks4://' + rawProxy
#         },
#         'socks': {
#             'http': 'socks://' + rawProxy,
#             'https': 'socks://' + rawProxy
#         }
#     }
#     try:
#         return proxiesTypesList[protocol]
#     except:
#         return proxiesTypesList['http']