import requests


def getRandomUserAgent():
    # TODO: do it
    return 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'


def get(url, proxy, params=None, **kwargs):
    if 'headers' not in kwargs:
        kwargs['headers'] = {
            'User-Agent': getRandomUserAgent()
        }
    else:
        if 'User-Agent' not in kwargs['headers']:
            kwargs['headers']['User-Agent'] = getRandomUserAgent()

    proxies = {}
    if proxy.getProtocol() == 'socks5':
        proxies = {
            'http': proxy.toUrl('socks5'),
            'https': proxy.toUrl('socks5'),
        }
    elif proxy.getProtocol() == 'socks4':
        proxies = {
            'http': proxy.toUrl('socks4'),
            'https': proxy.toUrl('socks4'),
        }
    elif proxy.getProtocol() == 'socks':
        proxies = {
            'http': proxy.toUrl('socks'),
            'https': proxy.toUrl('socks'),
        }
    else:
        proxies = {
            'http': proxy.toUrl('http'),
            'https': proxy.toUrl('https'),
        }
    kwargs['proxies'] = proxies

    if 'timeout' not in kwargs:
        kwargs['timeout'] = 10

    return requests.get(url, params, **kwargs)


def post(url, proxy, data=None, json=None, **kwargs):
    if 'headers' not in kwargs:
        kwargs['headers'] = {
            'User-Agent': getRandomUserAgent()
        }
    else:
        if 'User-Agent' not in kwargs['headers']:
            kwargs['headers']['User-Agent'] = getRandomUserAgent()

    if 'timeout' not in kwargs:
        kwargs['timeout'] = 10

    return requests.post(url, data, json, **kwargs)
