import requests


def getRandomUserAgent():
    # TODO: do it
    return 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'


def get(url, params=None, **kwargs):
    if 'headers' not in kwargs:
        kwargs['headers'] = {
            'User-Agent': getRandomUserAgent()
        }
    else:
        if 'User-Agent' not in kwargs['headers']:
            kwargs['headers']['User-Agent'] = getRandomUserAgent()

    return requests.get(url, params, **kwargs)


def post(url, data=None, json=None, **kwargs):
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