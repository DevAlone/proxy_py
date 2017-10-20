import requests
from core.models import Proxy, getProxyOfProtocol

import async_requests


# TODO: add multiple checks with several sites
async def checkProxy(proxy):
    try:
        res = await async_requests.get(
            'http://pikagraphs.d3d.info/OK/',
            proxy=proxy.toUrl(),
            timeout=10,
            headers={'User-Agent': getRandomUserAgent()},
        )
        if res.status == 200 and res.text == "OK":
            return True
    except Exception:
        return False
    return False


# method gets proxy in any of the supported formats
# and return proxy protocols
# supported raw proxy formats:
# ip:port
# domain:port
# user:pass@ip:port
# user:pass@domain:port
async def detectRawProxyProtocols(rawProxy):
    result = []

    protocols = ['http', 'socks5', 'socks4']

    for protocol in protocols:
        # TODO: add other test sites
        try:
            res = await async_requests.get(
                'http://pikagraphs.d3d.info/OK/',
                proxy="{}://{}".format(protocol, rawProxy),
                timeout=10,
                headers={'User-Agent': getRandomUserAgent()},
            )

            if res.status == 200 and res.text == "OK":
                result.append(protocol)
        except Exception as ex:
            pass

    return result


def getRandomUserAgent():
    # TODO: do it
    return 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'
